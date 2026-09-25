#!/usr/bin/env python3
"""Convert Woike's thirty original files to the layout the harness reads. Follows analysis/ADDENDUM_A_FROZEN.md.

    python scripts/mkw08_build_woike.py      ->  data-woike/<CODE>.csv, data-woike/build-report.json

Each output file is his file with a header row, decimal points, and the criterion moved to the last column
as `class`. Rows, row order, attributes and codings are his. The only values rewritten are his two missing
codes (-9 in Hungarian heart, 0.5 in Voting), which become `?`; the count per column is logged. Every other
cell is asserted equal to the corresponding cell of his file, and every file is checked against its pinned
SHA-256 and against the n and class split of Tabelle 6.9.
"""
import csv
import hashlib
import json
import os

PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PKG, "woike-original", "extracted")
OUT = os.path.join(PKG, "data-woike")
FILES = {"BANK": "Bankruptcy", "SOLV": "Solvency", "ECHO": "Echocardiogram", "POST": "Post-Operative",
         "BWAY": "Broadway", "CRED": "Credit Score", "ZOO": "Zoo", "IRIS": "Iris", "HEPA": "Hepatitis",
         "STRK": "Strikes", "WINE": "Wine", "CYY": "Baseball CYY", "GLAS": "Forensic Glass",
         "HORS": "Horse Colic", "SPCT": "SPECT", "HUNG": "Heart Disease (Hungaria)",
         "CLEV": "Heart Disease (Cleveland)", "ALCO": "Alcohol", "IONO": "Ionosphere", "TOUR": "Tourism",
         "VOTE": "Voting", "EDUC": "Education", "CARD": "Cardiac", "FOOT": "Football", "BCW": "Breast Cancer",
         "PIMA": "Diabetes", "AUTH": "Authorship", "HOF": "Baseball HoF", "YEAS": "Yeast", "SCOT": "Supreme Court"}
MISSING_CODE = {"HUNG": "-9", "VOTE": "0.5"}  # identified by exact match with the raw sources (AUDIT_2026-09-21.md)
NO_HEADER = {"ZOO"}
N_SLIPS = {"PIMA": 768}   # Tabelle 6.9 prints 786
SPLIT_SLIPS = {"BCW"}     # Tabelle 6.9 prints n1 = 444; his file codes the 239 malignant cases as 1


def main():
    with open(os.path.join(PKG, "woike-original", "hashes.json"), encoding="utf-8") as f:
        pinned = {r["path"]: r["sha256"] for r in json.load(f)}
    with open(os.path.join(PKG, "expected-counts.csv"), newline="", encoding="utf-8") as f:
        expected = {r["code"]: r for r in csv.DictReader(f)}
    os.makedirs(OUT, exist_ok=False)
    report = []
    for code, name in FILES.items():
        with open(os.path.join(SRC, name + ".dat"), "rb") as f:
            raw = f.read()
        assert hashlib.sha256(raw).hexdigest() == pinned["extracted/" + name + ".dat"], code
        lines = [ln.split("\t") for ln in raw.decode("latin-1").replace("\r\n", "\n").split("\n") if ln.strip()]
        width = len(lines[0])
        assert all(not any(v.strip() for v in ln[width:]) for ln in lines), code  # only blank fields beyond the header
        lines = [[v.strip().replace(",", ".") for v in ln[:width]] for ln in lines]
        if code in NO_HEADER:
            head, body = ["crit"] + [f"a{j}" for j in range(1, width)], lines
        else:
            head, body = lines[0], lines[1:]
        assert all(len(r) == width for r in body), code
        assert all(v != "" and v != "?" for r in body for v in r), code

        miss, rewritten = MISSING_CODE.get(code), {}
        rows = []
        for r in body:
            assert r[0] in ("0", "1"), (code, r[0])
            cells = []
            for j in range(1, width):
                v = r[j]
                if miss is not None and v == miss:
                    rewritten[head[j]] = rewritten.get(head[j], 0) + 1
                    v = "?"
                else:
                    assert v == r[j]
                cells.append(v)
            rows.append(cells + [r[0]])

        e = expected[code]
        n1 = sum(r[-1] == "1" for r in rows)
        assert len(rows) == N_SLIPS.get(code, int(e["woike_n"])), (code, len(rows))
        assert n1 == int(e["woike_n0" if code in SPLIT_SLIPS else "woike_n1"]), (code, n1)
        assert width - 1 == int(e["woike_cues"]), (code, width - 1)

        with open(os.path.join(OUT, code + ".csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(head[1:] + ["class"])
            w.writerows(rows)
        # read back and compare with his cells
        with open(os.path.join(OUT, code + ".csv"), newline="", encoding="utf-8") as f:
            back = list(csv.reader(f))[1:]
        for r, b in zip(body, back):
            assert b[-1] == r[0]
            assert all(x == y or (y == "?" and x == miss) for x, y in zip(r[1:], b[:-1])), code
        report.append({"code": code, "source": name + ".dat", "sha256": pinned["extracted/" + name + ".dat"],
                       "n": len(rows), "n1_his_coding": n1, "attributes": head[1:], "criterion_column": head[0],
                       "missing_code": miss, "cells_written_as_missing": rewritten})
        print(f"{code}: n={len(rows)} n1={n1} k={width - 1}" + (f" missing {miss} -> ?: {sum(rewritten.values())} cells" if miss else ""))
    with open(os.path.join(OUT, "build-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    print("built", len(report), "files")


if __name__ == "__main__":
    main()
