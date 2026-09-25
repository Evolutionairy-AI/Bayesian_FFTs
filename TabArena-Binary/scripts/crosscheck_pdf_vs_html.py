#!/usr/bin/env python3
"""Third rendering: parse Table F.1 from the arXiv HTML (v4) and compare it, cell by cell,
with the PDF parse. Standard library only.

    python scripts/crosscheck_pdf_vs_html.py

The HTML keeps every table cell in its own <td>, so it is an independent check on the PDF text
extraction, where pypdf glues some neighbouring cells together.
Reads  references/TabArena_arXiv_2506.16791v4.html
       references/TabArena_arXiv_2506.16791v4_TableF1_parsed.csv   (from parse_pdf_table_f1.py)
Writes references/TabArena_arXiv_2506.16791v4_TableF1_html_parsed.csv
Prints every disagreement; exits nonzero if there is one.
"""
import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "references"
REGIMES = ["default", "tuned", "tuned_ensemble"]
CAP = re.compile(r"^(?P<name>\S.*?) ?\((?P<metric>AUC|logloss|rmse)\s*[^)]*\)\s*$")
VAL = re.compile(r"^(\d+(?:\.\d+)?)\s*±\s*(\d+(?:\.\d+)?)$")


class F1(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0          # inside <annotation>: TeX source duplicated by LaTeXML
        self.in_cap = self.in_td = False
        self.buf, self.row, self.cur, self.rows = [], [], None, []

    def handle_starttag(self, tag, attrs):
        if tag == "annotation":
            self.skip += 1
        elif tag == "figcaption":
            self.in_cap, self.buf = True, []
        elif tag == "tr":
            self.row = []
        elif tag == "td":
            self.in_td, self.buf = True, []

    def handle_endtag(self, tag):
        if tag == "annotation":
            self.skip -= 1
        elif tag == "figcaption":
            self.in_cap = False
            m = CAP.match(" ".join("".join(self.buf).split()).replace("( ", "(").replace(" )", ")"))
            if m:  # only the per-dataset panels of Table F.1 have a "(metric arrow)" caption
                self.cur = (m.group("name").strip(), m.group("metric"))
        elif tag == "td":
            self.in_td = False
            self.row.append(" ".join("".join(self.buf).split()))
        elif tag == "tr" and self.cur and len(self.row) == 4 and self.row[0] and self.row[1] != "Default":
            for regime, cell in zip(REGIMES, self.row[1:]):
                m = VAL.match(cell)
                if m:
                    mean, sd = m.groups()
                elif cell == "-":
                    mean = sd = "-"
                else:
                    sys.exit(f"unparsed cell {cell!r} in {self.cur} / {self.row[0]}")
                self.rows.append([self.cur[0], self.cur[1], self.row[0], regime, mean, sd])
        elif tag == "table":
            self.cur = None

    def handle_data(self, data):
        if not self.skip and (self.in_cap or self.in_td):
            self.buf.append(data)


def main():
    p = F1()
    p.feed((REF / "TabArena_arXiv_2506.16791v4.html").read_text(encoding="utf-8"))
    with (REF / "TabArena_arXiv_2506.16791v4_TableF1_html_parsed.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["dataset", "metric", "model", "regime", "mean_as_printed", "sd_as_printed"])
        w.writerows(p.rows)
    html = {tuple(r[:4]): (r[4], r[5]) for r in p.rows}
    pdf = {(r["dataset"], r["metric"], r["model"], r["regime"]): (r["mean_as_printed"], r["sd_as_printed"])
           for r in csv.DictReader((REF / "TabArena_arXiv_2506.16791v4_TableF1_parsed.csv").open(encoding="utf-8"))}
    only_pdf, only_html = sorted(set(pdf) - set(html)), sorted(set(html) - set(pdf))
    diff = [(k, pdf[k], html[k]) for k in sorted(set(pdf) & set(html)) if pdf[k] != html[k]]
    auc = [k for k in pdf if k[1] == "AUC"]
    print(f"cells: PDF {len(pdf)}, HTML {len(html)}; AUC cells in PDF {len(auc)}")
    print(f"only in PDF: {len(only_pdf)}; only in HTML: {len(only_html)}; differing: {len(diff)}")
    for k in only_pdf[:20] + only_html[:20]:
        print("  unmatched:", k)
    for k, a, b in diff:
        print("  DIFF", k, "PDF", a, "HTML", b)
    sys.exit(1 if (only_pdf or only_html or diff) else 0)


if __name__ == "__main__":
    main()
