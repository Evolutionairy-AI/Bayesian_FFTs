#!/usr/bin/env python3
"""MKW08-30 raw-acquisition verifier. Standard library only.

    python scripts/mkw08_verify.py

Re-checks everything that manifest.json asserts about the files under raw/:
  1. byte size and SHA-256 of every listed file, and that raw/ holds no unlisted file;
  2. every extracted file is byte-identical to its member inside the pinned archive;
  3. raw row counts and field counts of every primary data file;
  4. raw class counts, where the manifest records a class column;
  5. the reduction / binarization counts that back each comparison with
     Woike (2008), Tabelle 6.9 (the CHECKS table below).
Writes verification-report.json and exits nonzero on any mismatch.
Nothing here downloads, edits, filters or builds data; rows are only counted.
"""
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MISSING = {"", "?", "NA", "."}  # blank (ACD), "?" (UCI), "." (halloffame.csv); "NA" does not occur


# ---------------------------------------------------------------- parsing
def parse(spec):
    """Return (header or None, list of records) for one primary data file."""
    text = (ROOT / spec["path"]).read_bytes().decode("latin-1")
    kind = spec["parser"]
    if kind == "csv_header":
        rows = [[v.strip() for v in r] for r in csv.reader(io.StringIO(text, newline=""))]
        rows = [r for r in rows if any(r)]
        return rows[0], rows[1:]
    lines = text.splitlines()
    if kind == "arff":
        start = next(i for i, l in enumerate(lines) if l.strip().lower() == "@data")
        lines = [l for l in lines[start + 1:] if l.strip() and not l.startswith("%")]
        return None, [[v.strip() for v in l.split(",")] for l in lines]
    if kind == "regex":  # data block embedded in a StatLib text file
        pat = re.compile(spec["pattern"])
        return None, [l.split() for l in lines if pat.match(l)]
    if kind == "delimited":
        sep = None if spec["sep"] == "ws" else spec["sep"]
        return None, [[v.strip() for v in l.split(sep)] for l in lines if l.strip()]
    raise ValueError(kind)


def load(ds, key="primary_data_files"):
    header, rows = None, []
    for spec in ds[key]:
        h, r = parse(spec)
        header = header or h
        rows += r
    return header, rows


def complete(rows, idx=None):
    return [r for r in rows if all(v not in MISSING for v in (r if idx is None else [r[i] for i in idx]))]


def col(header, name):
    return header.index(name)


# ------------------------------------------ reduction / binarization checks
# Each returns {label: count}. They document what was MEASURED when comparing the
# raw files with Tabelle 6.9; they are not a preprocessing protocol.
def chk_echo(h, rows):
    r13 = [r for r in rows if len(r) == 13]
    cc = complete(r13, [2, 3, 4, 5, 6, 7, 8, 12])  # attrs 3-9 + alive-at-1
    return {"rows_with_13_fields": len(r13), "alive_at_1_unknown": sum(r[12] == "?" for r in r13),
            "complete_attrs3to9_and_alive_at_1": len(cc),
            "alive_at_1=1": sum(r[12] == "1" for r in cc), "alive_at_1=0": sum(r[12] == "0" for r in cc)}


def chk_post(h, rows):
    cc = complete(rows)
    keep = [r for r in cc if r[-1] != "I"]
    return {"complete_rows": len(cc), "complete_rows_excluding_class_I": len(keep),
            "S": sum(r[-1] == "S" for r in keep), "A": sum(r[-1] == "A" for r in keep)}


def chk_bway(h, rows):
    cc = complete(rows)
    i = col(h, "Show run")
    short = sum(r[i] == "Less than 6 months" for r in cc)
    return {"complete_rows": len(cc), "run_less_than_6_months": short, "run_6_months_or_more": len(cc) - short}


def chk_hepa(h, rows):
    cc = complete(rows, [1, 2, 3, 4, 5, 6, 7, 19])  # AGE SEX STEROID ANTIVIRALS FATIGUE MALAISE ANOREXIA HISTOLOGY
    return {"complete_rows_all_19_attrs": len(complete(rows)), "complete_on_8_low_missing_attrs": len(cc),
            "class_2_live": sum(r[0] == "2" for r in cc), "class_1_die": sum(r[0] == "1" for r in cc)}


def chk_clev(h, rows):
    cc = complete(rows)
    return {"complete_rows": len(cc), "num=0": sum(r[-1] == "0" for r in cc), "num>0": sum(r[-1] != "0" for r in cc)}


def chk_tour(h, rows):
    idx = [col(h, c) for c in ("Age", "Sex", "Income", "Travel cost", "Trips")]
    cc = complete(rows, idx)
    t = col(h, "Trips")
    return {"complete_rows_all_columns": len(complete(rows)), "complete_on_Age_Sex_Income_TravelCost": len(cc),
            "trips>0": sum(float(r[t]) > 0 for r in cc), "trips=0": sum(float(r[t]) == 0 for r in cc)}


def chk_educ(h, rows):
    keep = [r for r in rows if r[2] not in ("0", "1") and r[4] != "0"]
    return {"edlevel=0": sum(r[2] == "0" for r in rows), "edlevel=1": sum(r[2] == "1" for r in rows),
            "prestige=0": sum(r[4] == "0" for r in rows), "rows_edlevel>=2_and_prestige>0": len(keep),
            "cert_taken": sum(r[3] == "2" for r in keep), "cert_not_taken": sum(r[3] == "1" for r in keep)}


def chk_bcw(h, rows):
    cc = complete(rows)
    return {"complete_rows": len(cc), "class_2_benign": sum(r[-1] == "2" for r in cc),
            "class_4_malignant": sum(r[-1] == "4" for r in cc)}


def chk_hof(h, rows):
    cc = complete(rows)
    return {"complete_rows": len(cc), "HoF=0": sum(r[-1] == "0" for r in cc), "HoF=1or2": sum(r[-1] != "0" for r in cc)}


def chk_vote(h, rows):
    n_q = [sum(v == "?" for v in r[1:]) for r in rows]
    return {"complete_rows": sum(n == 0 for n in n_q), "rows_with_at_most_2_?": sum(n <= 2 for n in n_q),
            "rows_with_at_most_3_?": sum(n <= 3 for n in n_q), "distinct_rows": len({tuple(r) for r in rows})}


def chk_foot(h, rows):
    fav = sum(int(r[1]) > int(r[2]) for r in rows)
    home = sum((int(r[1]) > int(r[2])) if r[0] == "1" else (int(r[2]) > int(r[1])) for r in rows)
    return {"favorite_wins": fav, "favorite_does_not_win": len(rows) - fav,
            "home_team_wins": home, "home_team_does_not_win": len(rows) - home,
            "ties": sum(r[1] == r[2] for r in rows)}


def gt0(name):
    def f(h, rows):
        i = col(h, name)
        return {name + ">0": sum(float(r[i]) > 0 for r in rows), name + "=0": sum(float(r[i]) == 0 for r in rows)}
    return f


def one_vs_rest(index, values, label):
    def f(h, rows):
        n = sum(r[index] in values for r in rows)
        return {label: n, "rest": len(rows) - n}
    return f


def chk_glas(h, rows):
    n12 = sum(r[-1] in ("1", "2") for r in rows)
    n123 = sum(r[-1] in ("1", "2", "3") for r in rows)
    return {"types_1+2_building_windows": n12, "rest_after_1+2": len(rows) - n12,
            "types_1+2+3_all_windows": n123, "rest_after_1+2+3": len(rows) - n123}


def chk_iris(h, rows):
    sizes = sorted(Counter(r[-1] for r in rows).values())
    return {"smallest_species": sizes[0], "largest_species": sizes[-1], "rows_minus_one_species": len(rows) - sizes[0]}


def chk_alco(h, rows):
    return {"drinks>5_half_pints": sum(float(r[5]) > 5 for r in rows), "drinks<=5_half_pints": sum(float(r[5]) <= 5 for r in rows)}


def chk_iono(h, rows):
    return {"distinct_values_in_attribute_2": len({r[1] for r in rows})}


def chk_hung(h, rows):
    return {"missing_slope": sum(r[10] == "?" for r in rows), "missing_ca": sum(r[11] == "?" for r in rows),
            "missing_thal": sum(r[12] == "?" for r in rows), "complete_on_first_10_attrs": len(complete(rows, range(10)))}


CHECKS = {
    "ECHO": chk_echo, "POST": chk_post, "BWAY": chk_bway, "HEPA": chk_hepa, "CLEV": chk_clev,
    "TOUR": chk_tour, "EDUC": chk_educ, "BCW": chk_bcw, "HOF": chk_hof, "VOTE": chk_vote,
    "FOOT": chk_foot, "GLAS": chk_glas, "IRIS": chk_iris, "ALCO": chk_alco, "IONO": chk_iono, "HUNG": chk_hung,
    "STRK": gt0("Wildcat strikes"), "SCOT": gt0("Actions taken"),
    "ZOO": one_vs_rest(-1, ("1",), "type_1_mammal"), "WINE": one_vs_rest(0, ("2",), "class_2"),
    "YEAS": one_vs_rest(-1, ("CYT",), "CYT"), "AUTH": one_vs_rest(-1, ("Shakespeare",), "Shakespeare"),
}


# ---------------------------------------------------------------- measuring
def measure_file(spec):
    header, rows = parse(spec)
    return {"rows": len(rows), "field_counts": {str(k): v for k, v in sorted(Counter(len(r) for r in rows).items())}}


def measure_class(ds, key="primary_data_files"):
    header, rows = load(ds, key)
    c = ds["raw_class"]["column"] if key == "primary_data_files" else ds["alternate_class_column"]
    i = col(header, c) if isinstance(c, str) else c
    return dict(sorted(Counter(r[i] if len(r) > abs(i) else "<short row>" for r in rows).items()))


def measure_checks(ds):
    fn = CHECKS.get(ds["code"])
    return fn(*load(ds)) if fn else {}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- verifying
def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    problems, report = [], []
    listed = set()
    n_files = 0
    for ds in manifest["datasets"] + manifest["shared_sources"]:
        for f in ds["files"]:
            p = ROOT / f["path"]
            listed.add(p.resolve())
            n_files += 1
            if not p.is_file():
                problems.append(f"{f['path']}: missing")
                continue
            if p.stat().st_size != f["bytes"]:
                problems.append(f"{f['path']}: size {p.stat().st_size} != {f['bytes']}")
            if sha256(p) != f["sha256"]:
                problems.append(f"{f['path']}: SHA-256 mismatch")
            if f["origin"] == "extracted":
                with zipfile.ZipFile(ROOT / f["archive"]) as z:
                    if z.read(f["member"]) != p.read_bytes():
                        problems.append(f"{f['path']}: differs from member {f['member']} of {f['archive']}")
    for p in (ROOT / "raw").rglob("*"):
        if p.is_file() and p.resolve() not in listed:
            problems.append(f"{p.relative_to(ROOT).as_posix()}: present under raw/ but not in manifest")

    print(f"{'code':5} {'Woike label':18} {'raw rows':>8} {'Woike n':>8}  {'n':12} {'split':22} result")
    tally = Counter()
    for ds in manifest["datasets"]:
        before = len(problems)
        total = 0
        for key in ("primary_data_files", "alternate_data_files"):
            for spec in ds.get(key, []):
                got = measure_file(spec)
                if got != {"rows": spec["rows"], "field_counts": spec["field_counts"]}:
                    problems.append(f"{ds['code']} {spec['path']}: measured {got}, manifest says rows={spec['rows']} {spec['field_counts']}")
                if key == "primary_data_files":
                    total += got["rows"]
        if total != ds["raw_rows"]:
            problems.append(f"{ds['code']}: raw_rows {ds['raw_rows']} but files sum to {total}")
        if ds.get("raw_class"):
            got = measure_class(ds)
            if got != ds["raw_class"]["counts"]:
                problems.append(f"{ds['code']}: class counts {got} != manifest {ds['raw_class']['counts']}")
        if ds.get("alternate_class_counts"):
            got = measure_class(ds, "alternate_data_files")
            if got != ds["alternate_class_counts"]:
                problems.append(f"{ds['code']}: alternate class counts {got} != manifest")
        got = measure_checks(ds)
        if got != ds["comparison"]["measured"]:
            problems.append(f"{ds['code']}: checks {got} != manifest {ds['comparison']['measured']}")
        ok = len(problems) == before
        cmp_ = ds["comparison"]
        tally[cmp_["n_status"]] += 1
        print(f"{ds['code']:5} {ds['woike_label']:18} {total:8d} {ds['woike_expected']['n']:8d}  "
              f"{cmp_['n_status']:12} {cmp_['split_status']:22} {'OK' if ok else 'FAIL'}")
        report.append({"code": ds["code"], "raw_rows": total, "woike_n": ds["woike_expected"]["n"],
                       "n_status": cmp_["n_status"], "split_status": cmp_["split_status"], "verified": ok})

    print(f"\nfiles hashed: {n_files}   datasets: {len(manifest['datasets'])}   "
          f"n vs Tabelle 6.9: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    for line in problems:
        print("PROBLEM:", line)
    print("RESULT:", "PASS (every hash, size, archive member, row count, class count and check matches manifest.json)"
          if not problems else f"FAIL ({len(problems)} problem(s))")
    (ROOT / "verification-report.json").write_text(json.dumps(
        {"files_hashed": n_files, "datasets": report, "n_status_tally": dict(sorted(tally.items())),
         "problems": problems, "result": "PASS" if not problems else "FAIL"}, indent=2) + "\n", encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
