"""Transcribe Woike (2008) Tabellen 6.10-6.12 (per-dataset accuracies, in percent)
from the dissertation PDF text layer into one CSV, and check the transcription
against the printed 'Mittelwert' (mean) row of each table.

Blocks per table: Fitting (95%), Prediction (15%), Prediction (50%), Prediction (90%).
6.10: five FFT algorithms, original construction (MS ZS MV ZV MA; MV = MaxVal = MKW08 'Max').
6.11: six FFT variants (SP SM SF VP VM VF; VF = ZigVal Fold = MKW08 'Zig').
6.12: LR, CART (CT) and three context models (Ex3 Ex4 Ex5).
Stdlib + pypdf.  Run from DATA_SETS/MKW08-30/:  python analysis/parse_woike_tables.py
"""
import csv
import re
from pathlib import Path
from pypdf import PdfReader

PKG = Path(__file__).resolve().parent.parent
PDF = PKG / "references" / "Woike_2008_Dissertation_Bochum.pdf"
BLOCKS = ["fit95", "pred15", "pred50", "pred90"]
ROW = re.compile(r"^(.+?) (\d+) (\d+) ((?:-|\d+)(?: (?:-|\d+)){19,23})$")

reader = PdfReader(str(PDF))
out, ok, worst = [], True, 0.0
for table, page in (("6.10", 243), ("6.11", 244), ("6.12", 245)):
    lines = reader.pages[page].extract_text().splitlines()
    head = next(l for l in lines if l.startswith("Datensatz n Cues"))
    cols = head.split()[3:]
    assert len(cols) in (20, 24), (table, cols)
    per = len(cols) // 4
    rows, mean_line = [], None
    for l in lines:
        if l.startswith("Mittelwert"):
            mean_line = [int(v) for v in l.split()[1:]]
        m = ROW.match(l)
        if m and not l.startswith("Mittelwert"):
            vals = [None if v == "-" else int(v) for v in m.group(4).split()]
            assert len(vals) == len(cols), (table, l)
            rows.append((m.group(1), int(m.group(2)), int(m.group(3)), vals))
    assert len(rows) == 30, (table, len(rows))
    for j in range(len(cols)):
        present = [r[3][j] for r in rows if r[3][j] is not None]
        mean = sum(present) / len(present)
        # entries and printed means are both rounded to integers, so the mean of
        # rounded entries may sit a little over 0.5 from the printed mean
        good = abs(mean - mean_line[j]) <= 0.75
        worst = max(worst, abs(mean - mean_line[j]))
        ok &= good
        if not good:
            print(f"  MEAN MISMATCH table {table} col {cols[j]} block {BLOCKS[j // per]}: "
                  f"computed {mean:.2f} vs printed {mean_line[j]}")
    print(f"Tabelle {table}: 30 rows, models {cols[:per]}")
    for name, n, cues, vals in rows:
        for j, v in enumerate(vals):
            out.append({"table": table, "dataset": name, "n": n, "cues": cues,
                        "block": BLOCKS[j // per], "model": cols[j], "accuracy": "" if v is None else v})

with open(PKG / "analysis" / "woike_tables_6_10_to_6_12.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
print("rows written:", len(out), "| all 64 printed means reproduced within 0.75:", ok,
      "| largest deviation:", round(worst, 2))
