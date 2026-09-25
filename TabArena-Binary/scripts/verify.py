#!/usr/bin/env python3
"""TabArena-Binary raw-acquisition verifier. Standard library only. No network access.

    python scripts/verify.py

Re-checks everything that manifest.json asserts:
  1. byte size and SHA-256 of every listed file (and the MD5 that OpenML publishes for each ARFF),
     and that the pinned folders hold no unlisted file;
  2. for each of the 30 ARFF files: rows, columns, declared column types, missing values per
     column, distinct values of every nominal/string column, and the class counts of the target,
     against measured-counts.csv, measured-column-counts.csv and manifest.json;
  3. that published_results.csv has exactly 30 datasets x 17 models x 3 regimes and that its
     "published" columns equal the cells parsed from the PDF (references/..._TableF1_parsed.csv).
Writes verification-report.json and exits nonzero on any mismatch.

Nothing here trains, scores, correlates or cross-tabulates anything. Values are only counted,
one column at a time; no feature is ever related to the target.
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_DIRS = ["raw", "suite", "references", "results_artifact"]
CHUNK = 4000
MISSING = "?"                       # ARFF missing-value token (unquoted)
QUOTED_QM = "'?'"                   # a quoted question mark is a value, not a missing cell
# literal strings that are ordinary values in the file but read like "no information"
PSEUDO_MISSING = {"", "nan", "NaN", "NAN", "NA", "N/A", "na", "n/a", "null", "NULL", "None", "none",
                  "unknown", "Unknown", "UNKNOWN", "Not Available", "Not Mapped", "not available", QUOTED_QM}

ATTR = re.compile(r"""^@attribute\s+(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|(\S+))\s+(.*?)\s*$""", re.I)
TOK = re.compile(r"""\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"|([^,]*?))\s*(,|$)""")
ESC = re.compile(r"\\(.)")
ESC_MAP = {"n": "\n", "t": "\t", "r": "\r"}


def unescape(s):
    return ESC.sub(lambda m: ESC_MAP.get(m.group(1), m.group(1)), s) if "\\" in s else s


def split_line(line):
    """Split one ARFF data line. Unquoted '?' stays '?'; a quoted '?' becomes QUOTED_QM."""
    if "'" not in line and '"' not in line:
        return [v.strip() for v in line.split(",")]
    out, pos, n = [], 0, len(line)
    while True:
        m = TOK.match(line, pos)
        if m.group(1) is not None or m.group(2) is not None:
            v = unescape(m.group(1) if m.group(1) is not None else m.group(2))
            out.append(QUOTED_QM if v == "?" else v)
        else:
            out.append(m.group(3))
        pos = m.end()
        if m.group(4) == "":
            return out
        if pos >= n:            # trailing comma: one more, empty, field
            out.append("")
            return out


def read_header(fh):
    """Return the attribute list [(name, declared_type, [nominal values] or None)], leaving fh at the data."""
    attrs = []
    for raw in fh:
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        low = line.lower()
        if low.startswith("@data"):
            return attrs
        if low.startswith("@attribute"):
            m = ATTR.match(line)
            name = unescape(next(g for g in m.groups()[:3] if g is not None))
            spec = m.group(4)
            if spec.startswith("{"):
                vals = split_line(spec[1:spec.rindex("}")])
                attrs.append((name, "nominal", [QUOTED_QM if v == QUOTED_QM else v for v in vals]))
            else:
                attrs.append((name, spec.split()[0].upper(), None))
    raise ValueError("no @data section")


class Col:
    def __init__(self, name, dtype, nominal):
        self.name, self.dtype, self.nominal = name, dtype, nominal
        self.numeric = dtype in ("NUMERIC", "REAL", "INTEGER")
        self.missing = 0
        self.pseudo = Counter()
        self.counts = None if self.numeric else Counter()
        self.seen = set()            # numeric: every value so far, kept only while all are distinct
        self.all_distinct = True
        self.integer_like = True
        self.small = set()           # numeric: distinct values, tracked exactly up to 1000
        self.small_over = False

    def feed(self, col):
        miss = col.count(MISSING)
        self.missing += miss
        if not self.numeric:
            c = Counter(col)
            c.pop(MISSING, None)
            self.counts.update(c)
            return
        toks = [v for v in col if v != MISSING] if miss else col
        distinct = set(toks)
        floats = set()
        for s in distinct:
            try:
                f = float(s)
            except ValueError:
                f = None
            if f is None or f != f or f in (float("inf"), float("-inf")):
                self.pseudo[s] += toks.count(s)
                continue
            floats.add(f)
            if self.integer_like and not f.is_integer():
                self.integer_like = False
        n_valid = len(toks) - sum(toks.count(s) for s in distinct if s in self.pseudo)
        if self.all_distinct:
            if len(floats) < n_valid or (self.seen & floats):
                self.all_distinct, self.seen = False, set()
            else:
                self.seen |= floats
        if not self.small_over:
            self.small |= floats
            if len(self.small) > 1000:
                self.small_over, self.small = True, set()

    def result(self, n_rows):
        if self.numeric:
            n_distinct = ">1000" if self.small_over else str(len(self.small))
            pseudo = dict(self.pseudo)
        else:
            n_distinct = str(len(self.counts))
            pseudo = {k: v for k, v in self.counts.items() if k in PSEUDO_MISSING}
        n_valid = n_rows - self.missing
        all_distinct = (self.all_distinct if self.numeric else len(self.counts) == n_valid) and n_valid > 1
        return dict(column=self.name, declared_type=self.dtype,
                    n_declared_nominal_values="" if self.nominal is None else str(len(self.nominal)),
                    n_missing=str(self.missing), n_distinct_observed=n_distinct,
                    all_values_distinct="yes" if all_distinct else "no",
                    integer_valued=("yes" if self.integer_like else "no") if self.numeric else "",
                    pseudo_missing_literals=";".join(f"{k or '<empty>'}={v}" for k, v in sorted(pseudo.items())))


def measure(path, target):
    """Count one ARFF file. Returns (dataset-level dict, list of per-column dicts)."""
    with open(path, encoding="utf-8", newline="") as fh:
        attrs = read_header(fh)
        cols = [Col(*a) for a in attrs]
        width, n_rows, rows_with_missing, bad_width, buf = len(cols), 0, 0, 0, []

        def flush():
            for c, values in zip(cols, zip(*buf)):
                c.feed(list(values))
            buf.clear()

        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("%"):
                continue
            if line.startswith("{"):
                raise ValueError("sparse ARFF rows are not supported")
            row = split_line(line)
            if len(row) != width:
                bad_width += 1
                continue
            n_rows += 1
            if MISSING in row:
                rows_with_missing += 1
            buf.append(row)
            if len(buf) >= CHUNK:
                flush()
        if buf:
            flush()
    per_col = [c.result(n_rows) for c in cols]
    for i, (pc, c) in enumerate(zip(per_col, cols), start=1):
        pc["column_index"] = str(i)
        pc["is_target"] = "yes" if c.name == target else "no"
    tcol = next(c for c in cols if c.name == target)
    types = Counter("numeric" if c.numeric else c.dtype.lower() for c in cols)
    summary = dict(n_rows=str(n_rows), n_columns_incl_target=str(width), n_features=str(width - 1),
                   n_numeric_columns=str(types.get("numeric", 0)), n_nominal_columns=str(types.get("nominal", 0)),
                   n_string_columns=str(types.get("string", 0)), n_date_columns=str(types.get("date", 0)),
                   n_missing_cells=str(sum(c.missing for c in cols)), n_rows_with_missing=str(rows_with_missing),
                   n_columns_with_missing=str(sum(1 for c in cols if c.missing)),
                   n_data_lines_with_wrong_field_count=str(bad_width),
                   target=target, target_declared_values=";".join(tcol.nominal or []),
                   class_counts=";".join(f"{k}={v}" for k, v in sorted(tcol.counts.items())),
                   target_missing=str(tcol.missing))
    return summary, per_col


def digest(path, algo):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    errors, report = [], {"files": {}, "datasets": {}, "published_results": {}}
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    # 1. files
    listed = {}
    for group in [manifest["shared_files"]] + [d["files"] for d in manifest["datasets"]]:
        for f in group:
            listed[f["path"]] = f
    for rel, f in sorted(listed.items()):
        p = ROOT / rel
        if not p.is_file():
            errors.append(f"missing file: {rel}")
            continue
        if p.stat().st_size != f["bytes"]:
            errors.append(f"size mismatch: {rel}")
        if digest(p, "sha256") != f["sha256"]:
            errors.append(f"sha256 mismatch: {rel}")
        if f.get("openml_md5") and digest(p, "md5") != f["openml_md5"]:
            errors.append(f"md5 differs from the checksum OpenML publishes: {rel}")
    on_disk = {p.relative_to(ROOT).as_posix() for d in PINNED_DIRS for p in (ROOT / d).rglob("*") if p.is_file()}
    for rel in sorted(on_disk - set(listed)):
        errors.append(f"unlisted file: {rel}")
    report["files"] = {"listed": len(listed), "on_disk_in_pinned_dirs": len(on_disk)}
    print(f"files: {len(listed)} listed, {len(on_disk)} on disk in {PINNED_DIRS}")

    # 2. counts
    ds_rows = {r["dataset"]: r for r in csv.DictReader((ROOT / "measured-counts.csv").open(encoding="utf-8"))}
    col_rows = {}
    for r in csv.DictReader((ROOT / "measured-column-counts.csv").open(encoding="utf-8")):
        col_rows.setdefault(r["dataset"], []).append(r)
    for d in manifest["datasets"]:
        name = d["name"]
        summary, per_col = measure(ROOT / d["primary_data_file"], d["target"])
        bad = [k for k, v in summary.items() if ds_rows[name].get(k) != v]
        bad += [f"manifest.{k}" for k, v in summary.items() if d["measured"].get(k) != v]
        want = col_rows.get(name, [])
        if len(want) != len(per_col):
            bad.append("column count in measured-column-counts.csv")
        else:
            for got, exp in zip(per_col, want):
                bad += [f"{got['column']}.{k}" for k, v in got.items() if exp.get(k) != v]
        status = "PASS" if not bad else "FAIL"
        if bad:
            errors.append(f"{name}: {bad[:8]}")
        report["datasets"][name] = dict(status=status, **summary)
        print(f"{status}  {name}: rows {summary['n_rows']}, columns {summary['n_columns_incl_target']}, "
              f"missing cells {summary['n_missing_cells']}, classes {summary['class_counts']}")

    # 3. published results against the PDF parse
    pub = list(csv.DictReader((ROOT / "published_results.csv").open(encoding="utf-8")))
    pdf = {(r["dataset"], r["model"], r["regime"]): r for r in csv.DictReader(
        (ROOT / "references" / "TabArena_arXiv_2506.16791v4_TableF1_parsed.csv").open(encoding="utf-8"))
        if r["metric"] == "AUC"}
    alias = manifest["published_results"]["pdf_dataset_name_aliases"]
    keys = {(r["dataset"], r["model"], r["regime"]) for r in pub}
    shape = (len(pub), len({r["dataset"] for r in pub}), len({r["model"] for r in pub}), len({r["regime"] for r in pub}))
    if shape != (1530, 30, 17, 3) or len(keys) != 1530:
        errors.append(f"published_results.csv shape {shape}")
    n_cmp = 0
    for r in pub:
        p = pdf[(alias.get(r["dataset"], r["dataset"]), r["model"], r["regime"])]
        exp = ("", "") if p["mean_as_printed"] == "-" else (p["mean_as_printed"], p["sd_as_printed"])
        n_cmp += 1
        if (r["published_auc_mean_pdf"], r["published_auc_sd_pdf"]) != exp:
            errors.append(f"published_results.csv differs from the PDF parse: {r['dataset']}/{r['model']}/{r['regime']}")
    status_counts = Counter(r["crosscheck"] for r in pub)
    if dict(status_counts) != manifest["published_results"]["crosscheck_status_counts"]:
        errors.append("crosscheck status counts differ from the manifest")
    report["published_results"] = dict(rows=len(pub), cells_compared_with_pdf_parse=n_cmp,
                                       crosscheck_status_counts=dict(status_counts))
    print(f"published_results.csv: {len(pub)} rows, {n_cmp} compared with the PDF parse, statuses {dict(status_counts)}")

    report["errors"] = errors
    report["result"] = "PASS" if not errors else "FAIL"
    (ROOT / "verification-report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for e in errors:
        print("ERROR:", e)
    print("RESULT:", report["result"])
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
