#!/usr/bin/env python3
"""Parse Table F.1 ("Performance Per Dataset") of the TabArena paper from the PDF.

    python scripts/parse_pdf_table_f1.py [pdf_path out_csv_path]

Needs pypdf (third-party; build step only, the verifier does not use it).
Reads  references/TabArena_arXiv_2506.16791v4.pdf
Writes references/TabArena_arXiv_2506.16791v4_TableF1_parsed.csv
        one row per (dataset, metric, model, regime) exactly as printed:
        mean and s.d. strings, or "-" where the table prints a dash.
All 51 dataset blocks are parsed; nothing is computed from the values.
"""
import csv
import re
import sys
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "references" / "TabArena_arXiv_2506.16791v4.pdf"
OUT = ROOT / "references" / "TabArena_arXiv_2506.16791v4_TableF1_parsed.csv"

MODELS = ["RF", "ExtraTrees", "XGBoost", "LightGBM", "CatBoost", "EBM", "FastAIMLP", "TorchMLP",
          "RealMLP", "TabM", "MNCA", "TabPFNv2", "TabDPT", "TabICL", "Linear", "KNN", "AutoGluon"]
REGIMES = ["default", "tuned", "tuned_ensemble"]
HDR = re.compile(r"^(?P<name>\S.*?) ?\((?P<metric>AUC|logloss|rmse)\s*[^)]*\)\s*$")
# A cell is "mean±sd" or a dash. pypdf sometimes glues neighbouring cells together
# ("-0.993±0.002", "0.991±0.0020.993±0.002"), so cells are scanned left to right and the
# s.d. is read with as many decimals as its mean (true of every unglued cell in the table).
MEAN = re.compile(r"(\d+)(?:\.(\d+))?\s*±\s*")  # the proceedings PDF puts spaces around the sign


def split_cells(rest):
    cells, i = [], 0
    while i < len(rest):
        if rest[i] == " ":
            i += 1
        elif rest[i] == "-":
            cells.append(("-", "-"))
            i += 1
        else:
            m = MEAN.match(rest, i)
            if not m:
                return None
            k = len(m.group(2) or "")
            sd = re.compile(r"\d+\.\d{%d}" % k if k else r"\d+").match(rest, m.end())
            if not sd:
                return None
            cells.append((m.group(1) + ("." + m.group(2) if m.group(2) else ""), sd.group(0)))
            i = sd.end()
    return cells

def main():
    global PDF, OUT
    if len(sys.argv) == 3:  # e.g. the NeurIPS proceedings PDF, as a further rendering
        PDF, OUT = Path(sys.argv[1]), Path(sys.argv[2])
    reader = pypdf.PdfReader(str(PDF))
    rows, cur, page_of = [], None, {}
    started = False
    for pno, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if "Table F.1" in text:
            started = True
        if not started:
            continue
        for line in text.split("\n"):
            line = line.strip()
            m = HDR.match(line)
            if m and not any(line.startswith(k) for k in MODELS):
                cur = (m.group("name").strip(), m.group("metric"))
                page_of[cur] = pno
                continue
            if cur is None:
                continue
            model = next((k for k in sorted(MODELS, key=len, reverse=True) if line.startswith(k)), None)
            if model is None:
                continue
            rest = line[len(model):]
            cells = split_cells(rest)
            if cells is None or len(cells) != 3:
                sys.exit(f"page {pno}: cannot split into 3 cells: {line!r}")
            for regime, (mean, sd) in zip(REGIMES, cells):
                rows.append([cur[0], cur[1], model, regime, mean, sd, pno])
    # integrity: every dataset block must hold all 17 models x 3 regimes exactly once
    seen = {}
    for r in rows:
        seen.setdefault((r[0], r[1]), []).append((r[2], r[3]))
    bad = {k: len(v) for k, v in seen.items() if sorted(v) != sorted((m, g) for m in MODELS for g in REGIMES)}
    if bad:
        sys.exit(f"incomplete blocks: {bad}")
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dataset", "metric", "model", "regime", "mean_as_printed", "sd_as_printed", "pdf_page"])
        w.writerows(rows)
    by_metric = {}
    for (name, metric) in seen:
        by_metric[metric] = by_metric.get(metric, 0) + 1
    print(f"blocks parsed: {len(seen)}  by metric: {by_metric}  rows: {len(rows)}")


if __name__ == "__main__":
    main()
