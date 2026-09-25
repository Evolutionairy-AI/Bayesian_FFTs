#!/usr/bin/env python3
"""Download the public raw files, check them against their pinned SHA-256, and build the analysis files.

    python fetch_data.py                      # all three collections
    python fetch_data.py holte mkw08          # or any of: holte, mkw08, tabarena

Standard library only. The raw files are not redistributed in this repository; each collection's manifest.json
records the URL, size and SHA-256 of every file as it was retrieved (2026-08-25 for Holte-16, 2026-09-18 for
MKW08-30, 2026-09-19 for TabArena-Binary). A file whose bytes differ from the manifest stops the script: the
upstream source has changed and the analysis files would no longer be the ones analyzed.

After building, every analysis file (data/<name>.csv) is checked against data_checksums.json, the SHA-256 of the
files the paper's analyses read.
"""
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AGENT = {"User-Agent": "Bayesian_FFTs-fetch/1.0"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check(path, expected, label):
    got = sha256(path)
    if got != expected:
        sys.exit(f"SHA-256 MISMATCH for {label}: expected {expected}, got {got}. The upstream file has changed.")


def download(url, dest, expected):
    """Fetch url to dest unless dest already holds the pinned bytes; one request at a time, two retries."""
    if dest.exists() and sha256(dest) == expected:
        return "kept"
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=AGENT), timeout=600) as r, \
                    open(part, "wb") as out:
                while block := r.read(1 << 20):
                    out.write(block)
            break
        except OSError as exc:
            if attempt == 2:
                sys.exit(f"DOWNLOAD FAILED: {url} ({exc})")
            time.sleep(5)
    check(part, expected, url)
    part.replace(dest)
    time.sleep(1)
    return "downloaded"


def run(*args):
    print("$ python", " ".join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def holte():
    run("Holte-16/scripts/holte16.py", "all")  # its own pinned download, extraction, build and validation


def mkw08():
    pkg = ROOT / "MKW08-30"
    manifest = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
    files = [f for d in manifest["datasets"] for f in d.get("files", [])]
    files += [f for s in manifest.get("shared_sources", []) for f in s.get("files", [])]
    n = {"downloaded": 0, "kept": 0, "extracted": 0}
    for f in files:
        if f.get("url") and f["origin"] != "extracted":
            n[download(f["url"], pkg / f["path"], f["sha256"])] += 1
    for f in files:
        if f["origin"] == "extracted":
            dest = pkg / f["path"]
            if not (dest.exists() and sha256(dest) == f["sha256"]):
                with zipfile.ZipFile(pkg / f["archive"]) as z:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(z.read(f["member"]))
                check(dest, f["sha256"], f["path"])
            n["extracted"] += 1
    print(f"MKW08-30: {n}", flush=True)
    run("MKW08-30/scripts/mkw08_verify.py")
    run("MKW08-30/scripts/mkw08_build.py")


def tabarena():
    pkg = ROOT / "TabArena-Binary"
    manifest = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
    n = {"downloaded": 0, "kept": 0}
    for d in manifest["datasets"]:
        for f in d.get("files", []):
            if f["path"] == f"raw/{d['name']}/{d['name']}.arff":  # the build reads the ARFF files only
                n[download(f["url"], pkg / f["path"], f["sha256"])] += 1
    print(f"TabArena-Binary: {n}", flush=True)
    run("TabArena-Binary/scripts/tabarena_build.py")


def check_built(prefixes):
    pinned = json.loads((ROOT / "data_checksums.json").read_text(encoding="utf-8"))
    bad = [p for p in pinned if p.startswith(prefixes) and sha256(ROOT / p) != pinned[p]]
    if bad:
        sys.exit(f"BUILT FILES DIFFER from the analyzed ones: {bad}")
    print(f"{sum(p.startswith(prefixes) for p in pinned)} analysis files equal the analyzed ones, byte for byte")


STEPS = {"holte": (holte, "Holte-16/"), "mkw08": (mkw08, "MKW08-30/"), "tabarena": (tabarena, "TabArena-Binary/")}

if __name__ == "__main__":
    chosen = sys.argv[1:] or list(STEPS)
    unknown = set(chosen) - set(STEPS)
    if unknown:
        sys.exit(f"unknown collection(s) {sorted(unknown)}; choose from {list(STEPS)}")
    for name in chosen:
        STEPS[name][0]()
    check_built(tuple(STEPS[name][1] for name in chosen))
