#!/usr/bin/env python3
"""Acquire, reconstruct, and validate the Holte-16 benchmark."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "manifest.json"
DATA_DIR = ROOT / "data"
EXTRACTED_DIR = ROOT / "raw" / "extracted"
METADATA_DIR = ROOT / "raw" / "metadata"


HEADERS: dict[str, list[str]] = {
    "BC": [
        "age",
        "menopause",
        "tumor_size",
        "inv_nodes",
        "node_caps",
        "deg_malig",
        "breast",
        "breast_quad",
        "irradiat",
    ],
    "CH": [
        "bkblk", "bknwy", "bkon8", "bkona", "bkspr", "bkxbq", "bkxcr",
        "bkxwp", "blxwp", "bxqsq", "cntxt", "dsopp", "dwipd", "hdchk",
        "katri", "mulch", "qxmsq", "r2ar8", "reskd", "reskr", "rimmx",
        "rkxwp", "rxmsq", "simpl", "skach", "skewr", "skrxp", "spcop",
        "stlmt", "thrsk", "wkcti", "wkna8", "wknck", "wkovl", "wkpos",
        "wtoeg",
    ],
    "GL": ["RI", "Na", "Mg", "Al", "Si", "K", "Ca", "Ba", "Fe"],
    "G2": ["RI", "Na", "Mg", "Al", "Si", "K", "Ca", "Ba", "Fe"],
    "HD": [
        "age", "sex", "chest_pain_type", "trestbps", "chol", "fbs",
        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal",
    ],
    "HE": [
        "age", "sex", "steroid", "antivirals", "fatigue", "malaise",
        "anorexia", "liver_big", "liver_firm", "spleen_palpable", "spiders",
        "ascites", "varices", "bilirubin", "alk_phosphate", "sgot", "albumin",
        "protime", "histology",
    ],
    "HO": [
        "surgery", "age", "rectal_temperature", "pulse", "respiratory_rate",
        "temperature_of_extremities", "peripheral_pulse", "mucous_membranes",
        "capillary_refill_time", "pain", "peristalsis", "abdominal_distension",
        "nasogastric_tube", "nasogastric_reflux", "nasogastric_reflux_ph",
        "rectal_examination_feces", "abdomen", "packed_cell_volume",
        "total_protein", "abdominocentesis_appearance",
        "abdominocentesis_total_protein", "outcome",
    ],
    "HY": [
        "age", "sex", "on_thyroxine", "query_on_thyroxine",
        "on_antithyroid_medication", "thyroid_surgery", "query_hypothyroid",
        "query_hyperthyroid", "pregnant", "sick", "tumor", "lithium", "goitre",
        "TSH_measured", "TSH", "T3_measured", "T3", "TT4_measured", "TT4",
        "T4U_measured", "T4U", "FTI_measured", "FTI", "TBG_measured", "TBG",
    ],
    "IR": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
    "LA": [
        "duration", "wage_increase_first_year", "wage_increase_second_year",
        "wage_increase_third_year", "cost_of_living_adjustment", "working_hours",
        "pension", "standby_pay", "shift_differential", "education_allowance",
        "statutory_holidays", "vacation", "longterm_disability_assistance",
        "contribution_to_dental_plan", "bereavement_assistance",
        "contribution_to_health_plan",
    ],
    "LY": [
        "lymphatics", "block_of_afferent", "block_of_lymphatic_c",
        "block_of_lymphatic_s", "bypass", "extravasates", "regeneration_of",
        "early_uptake_in", "lymph_nodes_diminution", "lymph_nodes_enlargement",
        "changes_in_lymphatics", "defect_in_node", "changes_in_node",
        "changes_in_structure", "special_forms", "dislocation_of",
        "exclusion_of_nodes", "number_of_nodes_in",
    ],
    "MU": [
        "cap_shape", "cap_surface", "cap_color", "bruises", "odor",
        "gill_attachment", "gill_spacing", "gill_size", "gill_color",
        "stalk_shape", "stalk_root", "stalk_surface_above_ring",
        "stalk_surface_below_ring", "stalk_color_above_ring",
        "stalk_color_below_ring", "veil_type", "veil_color", "ring_number",
        "ring_type", "spore_print_color", "population", "habitat",
    ],
    "SE": [
        "age", "sex", "on_thyroxine", "query_on_thyroxine",
        "on_antithyroid_medication", "thyroid_surgery", "query_hypothyroid",
        "query_hyperthyroid", "pregnant", "sick", "tumor", "lithium", "goitre",
        "TSH_measured", "TSH", "T3_measured", "T3", "TT4_measured", "TT4",
        "T4U_measured", "T4U", "FTI_measured", "FTI", "TBG_measured", "TBG",
    ],
    "SO": [
        "date", "plant_stand", "precip", "temp", "hail", "crop_hist",
        "area_damaged", "severity", "seed_tmt", "germination", "plant_growth",
        "leaves", "leafspots_halo", "leafspots_marg", "leafspot_size",
        "leaf_shread", "leaf_malf", "leaf_mild", "stem", "lodging",
        "stem_cankers", "canker_lesion", "fruiting_bodies", "external_decay",
        "mycelium", "int_discolor", "sclerotia", "fruit_pods", "fruit_spots",
        "seed", "mold_growth", "seed_discolor", "seed_size", "shriveling", "roots",
    ],
    "VO": [
        "handicapped_infants", "water_project_cost_sharing",
        "adoption_of_the_budget_resolution", "physician_fee_freeze",
        "el_salvador_aid", "religious_groups_in_schools", "anti_satellite_test_ban",
        "aid_to_nicaraguan_contras", "mx_missile", "immigration",
        "synfuels_corporation_cutback", "education_spending",
        "superfund_right_to_sue", "crime", "duty_free_exports",
        "export_administration_act_south_africa",
    ],
    "V1": [
        "handicapped_infants", "water_project_cost_sharing",
        "adoption_of_the_budget_resolution", "el_salvador_aid",
        "religious_groups_in_schools", "anti_satellite_test_ban",
        "aid_to_nicaraguan_contras", "mx_missile", "immigration",
        "synfuels_corporation_cutback", "education_spending",
        "superfund_right_to_sue", "crime", "duty_free_exports",
        "export_administration_act_south_africa",
    ],
}


def load_manifest() -> dict[str, Any]:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_hash(path: Path, expected: str) -> None:
    observed = sha256(path)
    if observed != expected:
        raise RuntimeError(
            f"SHA-256 mismatch for {path}: expected {expected}, observed {observed}"
        )


def download_verified(url: str, destination: Path, expected: str) -> None:
    if destination.exists():
        verify_hash(destination, expected)
        print(f"verified {destination.relative_to(ROOT)}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "Holte16/1.0"})
    try:
        with urllib.request.urlopen(request) as response, temporary.open("wb") as out:
            shutil.copyfileobj(response, out)
        verify_hash(temporary, expected)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"downloaded {destination.relative_to(ROOT)}")


def extract_required(manifest: dict[str, Any]) -> None:
    bundle_by_id = {item["uci_id"]: item for item in manifest["uci_bundles"]}
    required: dict[tuple[int, str], str] = {}
    for dataset in manifest["datasets"]:
        for raw_file in dataset["raw_files"]:
            key = (raw_file["uci_id"], raw_file["path"])
            expected = raw_file["sha256"]
            if key in required and required[key] != expected:
                raise RuntimeError(f"Conflicting hashes in manifest for {key}")
            required[key] = expected

    for (uci_id, relative), expected in sorted(required.items()):
        destination = EXTRACTED_DIR / f"uci-{uci_id}" / Path(relative)
        if destination.exists():
            verify_hash(destination, expected)
            continue
        bundle = ROOT / bundle_by_id[uci_id]["local_path"]
        verify_hash(bundle, bundle_by_id[uci_id]["sha256"])
        with zipfile.ZipFile(bundle) as archive:
            members = {name.replace("\\", "/"): name for name in archive.namelist()}
            normalized = relative.replace("\\", "/")
            if normalized not in members:
                raise RuntimeError(f"{relative} not found in {bundle}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(members[normalized]) as source, destination.open("wb") as out:
                shutil.copyfileobj(source, out)
        verify_hash(destination, expected)
    print(f"verified {len(required)} required raw files")


def acquire() -> None:
    manifest = load_manifest()
    for bundle in manifest["uci_bundles"]:
        download_verified(
            bundle["bundle_url"], ROOT / bundle["local_path"], bundle["sha256"]
        )
    paper = manifest["paper"]
    download_verified(paper["author_hosted_url"], ROOT / paper["local_path"], paper["sha256"])

    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    for bundle in manifest["uci_bundles"]:
        snapshot = METADATA_DIR / f"uci-{bundle['uci_id']}.json"
        if snapshot.exists():
            continue
        url = f"https://archive.ics.uci.edu/api/dataset?id={bundle['uci_id']}"
        request = urllib.request.Request(url, headers={"User-Agent": "Holte16/1.0"})
        try:
            with urllib.request.urlopen(request) as response:
                payload = json.load(response)
            with snapshot.open("w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
        except (OSError, urllib.error.URLError) as exc:
            print(f"warning: could not refresh {snapshot.relative_to(ROOT)}: {exc}")
    extract_required(manifest)


def raw_path(uci_id: int, relative: str) -> Path:
    return EXTRACTED_DIR / f"uci-{uci_id}" / Path(relative)


def read_csv_rows(path: Path) -> list[list[str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.reader(handle) if row]


def read_whitespace_rows(path: Path, comment_prefix: str | None = None) -> list[list[str]]:
    rows: list[list[str]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or (comment_prefix and stripped.startswith(comment_prefix)):
                continue
            rows.append(stripped.split())
    return rows


def require_width(rows: Iterable[list[str]], width: int, label: str) -> None:
    for number, row in enumerate(rows, start=1):
        if len(row) != width:
            raise RuntimeError(f"{label} row {number}: expected {width} fields, got {len(row)}")


def write_dataset(code: str, rows: list[list[str]]) -> None:
    expected_width = len(HEADERS[code]) + 1
    require_width(rows, expected_width, code)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{code}.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(HEADERS[code] + ["class"])
        writer.writerows(rows)
    print(f"built {path.relative_to(ROOT)} ({len(rows)} rows)")


def build() -> None:
    manifest = load_manifest()
    extract_required(manifest)

    bc = read_csv_rows(raw_path(14, "breast-cancer.data"))
    require_width(bc, 10, "BC raw")
    write_dataset("BC", [row[1:] + [row[0]] for row in bc])

    ch = read_csv_rows(raw_path(22, "kr-vs-kp.data"))
    require_width(ch, 37, "CH raw")
    write_dataset("CH", ch)

    glass = read_csv_rows(raw_path(42, "glass.data"))
    require_width(glass, 11, "GL raw")
    gl = [row[1:] for row in glass]
    write_dataset("GL", gl)
    g2: list[list[str]] = []
    for row in gl:
        if row[-1] not in {"1", "2", "3"}:
            continue
        transformed = list(row)
        if transformed[-1] == "3":
            transformed[-1] = "1"
        g2.append(transformed)
    write_dataset("G2", g2)

    hd = read_whitespace_rows(raw_path(45, "cleve.mod"), comment_prefix="%")
    require_width(hd, 15, "HD raw")
    write_dataset("HD", [row[:13] + [row[13]] for row in hd])

    he = read_csv_rows(raw_path(46, "hepatitis.data"))
    require_width(he, 20, "HE raw")
    write_dataset("HE", [row[1:] + [row[0]] for row in he])

    ho = read_whitespace_rows(raw_path(47, "horse-colic.data"))
    ho += read_whitespace_rows(raw_path(47, "horse-colic.test"))
    require_width(ho, 28, "HO raw")
    write_dataset("HO", [row[:2] + row[3:23] + [row[23]] for row in ho])

    hy = read_csv_rows(raw_path(102, "hypothyroid.data"))
    require_width(hy, 26, "HY raw")
    write_dataset("HY", [row[1:] + [row[0]] for row in hy])

    iris = read_csv_rows(raw_path(53, "iris.data"))
    require_width(iris, 5, "IR raw")
    write_dataset("IR", iris)

    labor = read_csv_rows(raw_path(56, "C4.5/labor-neg.data"))
    labor += read_csv_rows(raw_path(56, "C4.5/labor-neg.test"))
    require_width(labor, 17, "LA raw")
    write_dataset("LA", labor)

    lymph = read_csv_rows(raw_path(63, "lymphography.data"))
    require_width(lymph, 19, "LY raw")
    write_dataset("LY", [row[1:] + [row[0]] for row in lymph])

    mushroom = read_csv_rows(raw_path(73, "agaricus-lepiota.data"))
    require_width(mushroom, 23, "MU raw")
    write_dataset("MU", [row[1:] + [row[0]] for row in mushroom])

    se = read_csv_rows(raw_path(102, "sick-euthyroid.data"))
    require_width(se, 26, "SE raw")
    write_dataset("SE", [row[1:] + [row[0]] for row in se])

    soybean = read_csv_rows(raw_path(91, "soybean-small.data"))
    require_width(soybean, 36, "SO raw")
    write_dataset("SO", soybean)

    voting = read_csv_rows(raw_path(105, "house-votes-84.data"))
    require_width(voting, 17, "VO raw")
    write_dataset("VO", [row[1:] + [row[0]] for row in voting])
    write_dataset("V1", [row[1:4] + row[5:] + [row[0]] for row in voting])


def rounded_baseline(class_counts: Counter[str], rows: int) -> float:
    return round(100.0 * max(class_counts.values()) / rows, 1)


def validate(strict_historical: bool = False) -> bool:
    manifest = load_manifest()
    reports: list[dict[str, Any]] = []
    current_ok = True
    historical_ok = True

    for dataset in manifest["datasets"]:
        code = dataset["code"]
        path = DATA_DIR / f"{code}.csv"
        if not path.exists():
            reports.append({"code": code, "status": "fail", "error": "output missing"})
            current_ok = historical_ok = False
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            all_rows = list(csv.reader(handle))
        if not all_rows:
            reports.append({"code": code, "status": "fail", "error": "output empty"})
            current_ok = historical_ok = False
            continue
        header, rows = all_rows[0], all_rows[1:]
        widths = sorted(set(map(len, rows)))
        class_counts = Counter(row[-1] for row in rows if row)
        missing_tokens = sum(value == "?" for row in rows for value in row)
        observed = {
            "rows": len(rows),
            "features": len(header) - 1,
            "classes": len(class_counts),
            "class_counts": dict(sorted(class_counts.items())),
            "baseline_percent": rounded_baseline(class_counts, len(rows)) if rows else None,
            "has_missing": missing_tokens > 0,
            "missing_tokens": missing_tokens,
            "row_widths": widths,
            "sha256": sha256(path),
        }
        holte = dataset["holte_expected"]
        current = dataset["current_expected"]
        current_baseline = current.get("baseline_percent", holte["baseline_percent"])
        current_checks = {
            "header_class_last": bool(header) and header[-1] == "class",
            "uniform_width": widths == [holte["features"] + 1],
            "features": observed["features"] == holte["features"],
            "rows": observed["rows"] == current["rows"],
            "classes": observed["classes"] == holte["classes"],
            "class_counts": observed["class_counts"] == current["class_counts"],
            "baseline_percent": observed["baseline_percent"] == current_baseline,
            "has_missing": observed["has_missing"] == holte["has_missing"],
            "missing_tokens": observed["missing_tokens"] == current["missing_tokens"],
        }
        historical_checks = {
            "rows": observed["rows"] == holte["rows"],
            "features": observed["features"] == holte["features"],
            "classes": observed["classes"] == holte["classes"],
            "baseline_percent": observed["baseline_percent"] == holte["baseline_percent"],
            "has_missing": observed["has_missing"] == holte["has_missing"],
        }
        passes_current = all(current_checks.values())
        passes_historical = all(historical_checks.values())
        if passes_historical:
            status = "pass_historical"
        elif code == "LY" and passes_current:
            status = "version_drift_unresolved"
        else:
            status = "fail"
        reports.append(
            {
                "code": code,
                "name": dataset["name"],
                "status": status,
                "historical_fidelity": dataset["historical_fidelity"],
                "observed": observed,
                "current_checks": current_checks,
                "historical_checks": historical_checks,
            }
        )
        current_ok &= passes_current
        historical_ok &= passes_historical
        print(
            f"{code:>2}  {status:27} rows={observed['rows']:>4} "
            f"features={observed['features']:>2} baseline={observed['baseline_percent']:>4.1f}%"
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": manifest["package_name"],
        "current_authoritative_build_passes": current_ok,
        "strict_historical_build_passes": historical_ok,
        "strict_historical_requested": strict_historical,
        "summary": {
            "historical_pass_count": sum(r.get("status") == "pass_historical" for r in reports),
            "version_drift_count": sum(
                r.get("status") == "version_drift_unresolved" for r in reports
            ),
            "failure_count": sum(r.get("status") == "fail" for r in reports),
        },
        "datasets": reports,
    }
    report_path = ROOT / "validation-report.json"
    with report_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    if strict_historical:
        return historical_ok
    return current_ok


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("acquire", help="download/verify and extract authoritative sources")
    subparsers.add_parser("build", help="reconstruct all 16 standardized CSV files")
    validate_parser = subparsers.add_parser("validate", help="validate reconstructed outputs")
    validate_parser.add_argument("--strict-historical", action="store_true")
    all_parser = subparsers.add_parser("all", help="acquire, build, and validate")
    all_parser.add_argument("--strict-historical", action="store_true")
    return parser


def main() -> int:
    args = make_parser().parse_args()
    if args.command == "acquire":
        acquire()
        return 0
    if args.command == "build":
        build()
        return 0
    if args.command == "validate":
        return 0 if validate(args.strict_historical) else 1
    if args.command == "all":
        acquire()
        build()
        return 0 if validate(args.strict_historical) else 1
    raise AssertionError(args.command)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
