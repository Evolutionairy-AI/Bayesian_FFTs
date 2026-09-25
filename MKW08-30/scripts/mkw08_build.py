#!/usr/bin/env python3
"""MKW08-30 build: raw files -> data/<CODE>.csv in the Holte-16 harness format.

    python scripts/mkw08_build.py

Standard library only. Applies, per dataset, the row rule, the criterion rule and
the attribute list fixed in analysis/PRESPECIFICATION (Appendix A is generated from
the BUILD table below, so the document and the code cannot diverge). Writes

    data/<CODE>.csv            header = attribute names + "class"; missing = "?";
                               class = "1" for Woike's n1 category, "0" otherwise
    data/APPENDIX_A.md         the per-dataset attribute lists and exclusions
    data/build-report.json     n, split and attribute count per dataset

and asserts n and the class split against Tabelle 6.9 (HORS, VOTE, PIMA: against the
raw counts stated in the pre-specification). Nothing here fits, scores or compares
anything: rows are selected, columns are selected, values are copied.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mkw08_verify import MISSING, ROOT, col, load  # noqa: E402

OUT = ROOT / "data"

HEART = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
         "exang", "oldpeak", "slope", "ca", "thal"]
HORSE = {1: "age", 3: "rectal_temperature", 4: "pulse", 5: "respiratory_rate",
         6: "temperature_of_extremities", 7: "peripheral_pulse", 8: "mucous_membranes",
         9: "capillary_refill_time", 10: "pain", 11: "peristalsis",
         12: "abdominal_distension", 13: "nasogastric_tube", 14: "nasogastric_reflux",
         15: "nasogastric_reflux_ph", 16: "rectal_examination_feces", 17: "abdomen",
         18: "packed_cell_volume", 19: "total_protein",
         20: "abdominocentesis_appearance", 21: "abdominocentesis_total_protein"}


def by_index(names, first=0):
    """{column index: name} for consecutive columns starting at `first`."""
    return {first + i: n for i, n in enumerate(names)}


# code -> dict(rows=row filter or None, crit=(description, fn(header, r) -> bool: Woike's n1
# category), attrs={index: name} or [header names], expect=(n, n1, n0) or None (= Tabelle 6.9),
# excluded=[(column, reason)], note=str)
BUILD = {
    "BANK": dict(crit=("Bankrupt = 1", lambda h, r: r[col(h, "Bankrupt")] == "1"),
                 attrs=["WC/TA", "RE/TA", "EBIT/TA", "S/TA", "BVE/BVL"],
                 excluded=[("Company", "identifier")],
                 note="Split is 25/25; C1 is set to Bankrupt = 1."),
    "SOLV": dict(crit=("Solvent = 1", lambda h, r: r[col(h, "Solvent")] == "1"),
                 attrs=["EBIT/TA", "NI/TC", "Sales/TA", "EBIT/Sales", "NI/Sales", "WC/TA",
                        "Equity/TL", "Equity/TA"],
                 excluded=[("Firm", "identifier")]),
    "ECHO": dict(rows=("13 fields, attributes 3-9 and alive-at-1 known",
                       lambda h, r: len(r) == 13 and all(r[i] not in MISSING for i in (2, 3, 4, 5, 6, 7, 8, 12))),
                 crit=("alive-at-1 = 1, as shipped", lambda h, r: r[12] == "1"),
                 attrs=by_index(["age_at_heart_attack", "pericardial_effusion", "fractional_shortening",
                                 "epss", "lvdd", "wall_motion_score", "wall_motion_index"], 2),
                 excluded=[("survival, still-alive", "carry the outcome"),
                           ("mult, name, group", "to be ignored per echocardiogram.names")],
                 note="The shipped criterion column contradicts its own definition on these rows "
                      "(README, finding 3); it is used as shipped because it is Woike's."),
    "POST": dict(rows=("complete rows, intensive-care class (I) removed",
                       lambda h, r: all(v not in MISSING for v in r) and r[-1] != "I"),
                 crit=("ADM-DECS = S (sent home)", lambda h, r: r[-1] == "S"),
                 attrs=by_index(["L_CORE", "L_SURF", "L_O2", "L_BP", "SURF_STBL", "CORE_STBL",
                                 "BP_STBL", "COMFORT"]),
                 excluded=[]),
    "BWAY": dict(rows=("complete rows", lambda h, r: all(v not in MISSING for v in r)),
                 crit=("Show run of six months or more",
                       lambda h, r: r[col(h, "Show run")] != "Less than 6 months"),
                 attrs=["Type", "Revival", "NYT rating", "DN rating", "Tony awards",
                        "Tony nominations", "Week 1 attendance"],
                 excluded=[("Show", "identifier"), ("Show run code", "the criterion, recoded")]),
    "CRED": dict(crit=("Application.accepted = 1", lambda h, r: r[col(h, "Application.accepted")] == "1"),
                 attrs=["Age", "Income.per.dependent", "Monthly.credit.card.exp", "Own.home",
                        "Self.employed", "Derogatory.reports"],
                 excluded=[]),
    "ZOO": dict(crit=("type = 1 (mammal)", lambda h, r: r[-1] == "1"),
                attrs=by_index(["hair", "feathers", "eggs", "milk", "airborne", "aquatic", "predator",
                                "toothed", "backbone", "breathes", "venomous", "fins", "legs", "tail",
                                "domestic", "catsize"], 1),
                excluded=[("animal name", "identifier")]),
    "IRIS": dict(crit=("species = Iris-versicolor", lambda h, r: r[-1] == "Iris-versicolor"),
                 attrs=by_index(["sepal_length", "sepal_width", "petal_length", "petal_width"]),
                 excluded=[],
                 note="Woike does not name the species. His published accuracies (logistic regression "
                      "71 to 74, CART 95 to 98) fit versicolor against the rest and no other coding. "
                      "File iris.data, not bezdekIris.data."),
    "HEPA": dict(rows=("complete on AGE, SEX, STEROID, ANTIVIRALS, FATIGUE, MALAISE, ANOREXIA, HISTOLOGY",
                       lambda h, r: all(r[i] not in MISSING for i in (1, 2, 3, 4, 5, 6, 7, 19))),
                 crit=("class = 2 (live)", lambda h, r: r[0] == "2"),
                 attrs=by_index(["AGE", "SEX", "STEROID", "ANTIVIRALS", "FATIGUE", "MALAISE", "ANOREXIA",
                                 "LIVER_BIG", "LIVER_FIRM", "SPLEEN_PALPABLE", "SPIDERS", "ASCITES",
                                 "VARICES", "BILIRUBIN", "ALK_PHOSPHATE", "SGOT", "ALBUMIN", "PROTIME",
                                 "HISTOLOGY"], 1),
                 excluded=[]),
    "STRK": dict(crit=("Wildcat strikes > 0", lambda h, r: float(r[col(h, "Wildcat strikes")]) > 0),
                 attrs=["Grievances", "Rotate", "Union", "Workforce"],
                 excluded=[("Log workforce", "monotone transform of Workforce; the same cue after a median cut")]),
    "WINE": dict(crit=("cultivar = 2", lambda h, r: r[0] == "2"),
                 attrs=by_index(["alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium",
                                 "total_phenols", "flavanoids", "nonflavanoid_phenols", "proanthocyanins",
                                 "color_intensity", "hue", "od280_od315", "proline"], 1),
                 excluded=[]),
    "CYY": dict(crit=("Cy Young = 1", lambda h, r: r[col(h, "Cy Young")] == "1"),
                attrs=["Year", "League", "Type", "Wins", "Win pct", "Saves", "ERA", "Strikeouts",
                       "Innings pitched"],
                excluded=[("Pitcher", "identifier")],
                note="The two files (1980-92, 1993-2002) are pooled, as Woike's n requires."),
    "GLAS": dict(crit=("type 1 or 2 (building windows)", lambda h, r: r[-1] in ("1", "2")),
                 attrs=by_index(["RI", "Na", "Mg", "Al", "Si", "K", "Ca", "Ba", "Fe"], 1),
                 excluded=[("Id", "identifier")]),
    "HORS": dict(rows=("surgery known", lambda h, r: r[0] not in MISSING),
                 crit=("surgery = 1 (treated with surgery)", lambda h, r: r[0] == "1"),
                 attrs=HORSE, expect=(366, 214, 152),
                 excluded=[("hospital number", "identifier"),
                           ("outcome", "known only after the decision"),
                           ("surgical lesion, three lesion-type codes, cp_data", "established retrospectively, "
                            "after surgery or necropsy")],
                 note="Woike's 218 cases could not be reconstructed; all 366 rows of .data and .test with a "
                      "known criterion are used. Criterion per Woike et al. (2017), Table 1."),
    "SPCT": dict(crit=("diagnosis = 1 (abnormal)", lambda h, r: r[0] == "1"),
                 attrs=by_index(["F%d" % i for i in range(1, 23)], 1),
                 excluded=[], note="Donor's train and test files pooled, as Woike's n requires."),
    "HUNG": dict(crit=("num = 1 (disease present)", lambda h, r: r[-1] == "1"),
                 attrs=by_index(HEART), excluded=[],
                 note="File processed.hungarian.data, all 294 rows; slope, ca and thal are mostly missing "
                      "and enter with the missing value as a pseudo-value, as the protocol prescribes."),
    "CLEV": dict(rows=("complete rows", lambda h, r: all(v not in MISSING for v in r)),
                 crit=("num > 0 (disease present)", lambda h, r: r[-1] != "0"),
                 attrs=by_index(HEART), excluded=[], note="File processed.cleveland.data."),
    "ALCO": dict(crit=("drinks > 5 half-pints", lambda h, r: float(r[5]) > 5),
                 attrs=by_index(["mcv", "alkphos", "sgpt", "sgot", "gammagt"]),
                 excluded=[("selector", "the donor's train/test flag")]),
    "IONO": dict(crit=("class = g (good return)", lambda h, r: r[-1] == "g"),
                 attrs=by_index(["a%02d" % i for i in range(1, 35)]), excluded=[],
                 note="Attribute a02 is constant; the harness drops constant cues by itself."),
    "TOUR": dict(rows=("complete on Age, Sex, Income, Travel cost, Trips",
                       lambda h, r: all(r[col(h, c)] not in MISSING
                                        for c in ("Age", "Sex", "Income", "Travel cost", "Trips"))),
                 crit=("Trips > 0", lambda h, r: float(r[col(h, "Trips")]) > 0),
                 attrs=["Age", "Sex", "Income", "Travel cost", "Access road", "Active", "Passive"],
                 excluded=[("Logged income", "monotone transform of Income")],
                 note="The record with Sex = 4 is kept as it stands."),
    "VOTE": dict(crit=("party = democrat", lambda h, r: r[0] == "democrat"),
                 attrs=by_index(["vote%02d" % i for i in range(1, 17)], 1), expect=(435, 267, 168),
                 excluded=[],
                 note="Woike's 402 cases could not be reconstructed; all 435 rows are used, with '?' as a "
                      "third value."),
    "EDUC": dict(rows=("educational level 2 or higher and prestige recorded",
                       lambda h, r: r[2] not in ("0", "1") and r[4] != "0"),
                 crit=("Leaving Certificate taken (code 2)", lambda h, r: r[3] == "2"),
                 attrs={0: "sex", 1: "DVRT", 4: "fathers_prestige", 5: "school_type"},
                 excluded=[("educational level", "determines the criterion")]),
    "CARD": dict(crit=("any.event = 0 (no cardiac event; Woike's n1 = 469)",
                       lambda h, r: r[col(h, "any.event")] == "0"),
                 attrs=["bhr", "basebp", "basedp", "pkhr", "sbp", "dp", "dose", "maxhr", "pctMphr", "mbp",
                        "dpmaxdo", "dobdose", "age", "gender", "baseEF", "dobEF", "chestpain", "restwma",
                        "posSE", "hxofHT", "hxofDM", "hxofCig", "hxofMI", "hxofPTCA", "hxofCABG", "ecg"],
                 excluded=[("row index", "identifier"),
                           ("newMI, newPTCA, newCABG, death", "components of the criterion")],
                 note="File stressEcho.csv (hbiostat), whose event columns are coded 1 = yes."),
    "FOOT": dict(crit=("favorite wins (favorite points > underdog points)",
                       lambda h, r: int(r[1]) > int(r[2])),
                 attrs={0: "favorite_at_home", 3: "point_spread", 6: "year", 7: "week"},
                 excluded=[("favorite points, underdog points", "define the criterion"),
                           ("favorite, underdog (team names)", "identifiers"),
                           ("night / Monday / overtime tokens", "optional trailing tokens; overtime is "
                            "known only after the game")],
                 note="Woike's text says 'home team wins'; his counts are those of 'favorite wins' "
                      "(README, finding 1). The counts decide. The single tie counts as not won."),
    "BCW": dict(rows=("complete rows", lambda h, r: all(v not in MISSING for v in r)),
                crit=("class = 2 (benign)", lambda h, r: r[-1] == "2"),
                attrs=by_index(["clump_thickness", "cell_size_uniformity", "cell_shape_uniformity",
                                "marginal_adhesion", "epithelial_cell_size", "bare_nuclei",
                                "bland_chromatin", "normal_nucleoli", "mitoses"], 1),
                excluded=[("sample id", "identifier")]),
    "PIMA": dict(crit=("tested_positive", lambda h, r: r[-1] == "tested_positive"),
                 attrs=by_index(["preg", "plas", "pres", "skin", "insu", "mass", "pedi", "age"]),
                 expect=(768, 268, 500), excluded=[],
                 note="Tabelle 6.9 prints n = 786, a transposition of 768. Zeros are kept as recorded."),
    "AUTH": dict(crit=("Author = Shakespeare", lambda h, r: r[col(h, "Author")] == "Shakespeare"),
                 attrs="ALL_BUT", excluded=[("BookID", "identifies the author's books")]),
    "HOF": dict(rows=("complete rows", lambda h, r: all(v not in MISSING for v in r)),
                crit=("Hall of Fame code 1 or 2", lambda h, r: r[col(h, "Hall of Fame")] != "0"),
                attrs=["Number seasons", "Games played", "At bats", "Runs", "Hits", "Doubles", "Triples",
                       "Home runs", "RBIs", "Walks", "Strikeouts", "Batting average", "On base pct",
                       "Slugging pct", "Fielding ave", "Position"],
                excluded=[("Player", "identifier")]),
    "YEAS": dict(crit=("site = CYT", lambda h, r: r[-1] == "CYT"),
                 attrs=by_index(["mcg", "gvh", "alm", "mit", "erl", "pox", "vac", "nuc"], 1),
                 excluded=[("sequence name", "identifier")]),
    "SCOT": dict(crit=("Actions taken > 0", lambda h, r: float(r[col(h, "Actions taken")]) > 0),
                 attrs=["Liberal", "Unconstitutional", "Precedent alteration", "Unanimous",
                        "Year of decision", "Lower court disagreement", "Log exposure"],
                 excluded=[]),
}


def build(ds):
    spec = BUILD[ds["code"]]
    header, rows = load(ds)
    if "rows" in spec:
        rows = [r for r in rows if spec["rows"][1](header, r)]
    attrs = spec["attrs"]
    if attrs == "ALL_BUT":  # AUTH: 69 word-count columns
        attrs = [c for c in header if c not in ("BookID", "Author")]
    if isinstance(attrs, list):
        attrs = {col(header, c): c for c in attrs}
    idx = sorted(attrs)
    names = [attrs[i].replace(",", ";") for i in idx]
    y = ["1" if spec["crit"][1](header, r) else "0" for r in rows]
    body = [["?" if r[i] in MISSING else r[i] for i in idx] + [c] for r, c in zip(rows, y)]
    we = ds["woike_expected"]
    expect = spec.get("expect") or (we["n"], we["n1"], we["n0"])
    got = (len(body), y.count("1"), y.count("0"))
    assert got == expect, (ds["code"], got, expect)
    OUT.mkdir(exist_ok=True)
    with open(OUT / (ds["code"] + ".csv"), "w", newline="", encoding="utf-8") as f:
        f.write(",".join(names + ["class"]) + "\n")
        for r in body:
            assert not any("," in v for v in r), (ds["code"], r)
            f.write(",".join(r) + "\n")
    return names, got


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    report, lines = [], []
    for k, ds in enumerate(manifest["datasets"], 1):
        code, spec, we = ds["code"], BUILD[ds["code"]], ds["woike_expected"]
        names, (n, n1, n0) = build(ds)
        c1 = "Woike's n1 category" if n1 >= n0 else "its complement"
        report.append({"code": code, "n": n, "n1_woike_category": n1, "n0": n0,
                       "attributes": len(names), "woike_cues": we["cues"]})
        lines.append(f"**{k}. {code}** ({ds['woike_label']}). n = {n}; criterion: {spec['crit'][0]}, "
                     f"{n1} / {n0}; C1 (the larger side) is {c1}. "
                     + (f"Rows: {spec['rows'][0]}. " if "rows" in spec else "Rows: all. ")
                     + f"Attributes ({len(names)}; Woike used {we['cues']}): " + ", ".join(names) + ". "
                     + ("Excluded: " + "; ".join(f"{c} ({why})" for c, why in spec["excluded"]) + ". "
                        if spec["excluded"] else "Excluded: none. ")
                     + spec.get("note", ""))
        print(f"{code:5} n={n:5d} split={n1}/{n0} attributes={len(names)} (Woike {we['cues']})")
    (OUT / "APPENDIX_A.md").write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    (OUT / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"built {len(report)} datasets; total attributes {sum(r['attributes'] for r in report)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
