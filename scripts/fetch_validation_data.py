"""Fetch independent within-climate validation datasets for Paper 1.

These are held-out external test sets — NOT training data. See
`docs/external_validation_datasets.md` for the pre-registration rationale and the
independence (de-duplication) rule.

Training baseline (must stay disjoint from anything fetched here):
    SAFE Borneo   ~4.69 N, 117.58 E  (humid tropical)   sites E_*
    La Jarda ES   ~36.57 N, -5.60 E  (Mediterranean)    sites LJ_*

Status of sources
-----------------
- cocoa_altobeni : READY, clean. Humid-tropical agroforestry (Bolivia ~15.4 S,
  67.5 W). T/RH time series + stand structure + PAR/LAI + throughfall. Disjoint
  from SAFE/La Jarda by continent, study and decade. -> primary within-climate test.
- pantropical_tms: GATED + CONTAMINATION RISK. Raw loggers via SoilTemp request;
  spans South/SE Asia and may include SAFE/Bornean sites -> must de-dup by coords
  before any use. Not auto-fetched here.
- mediterranean  : TODO. Clean in-situ sub-canopy *air* T independent of La Jarda
  is not yet sourced openly (ForestTemp is modelled output; SoilTemp is gated;
  Montseny/SENTHYMED need vetting for sub-canopy air T). Not auto-fetched here.

Usage:  python scripts/fetch_validation_data.py
Lands data under data/raw/<dataset>/ (gitignored).
"""
from __future__ import annotations

import io
import sys
import urllib.request
import zipfile
from pathlib import Path

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"

SOURCES = {
    "cocoa_altobeni": {
        "doi": "10.5281/zenodo.1185579",
        "zip_url": (
            "https://zenodo.org/records/1185579/files/"
            "Microclimate%20in%20cocoa%20production%20systems%20Data.zip?download=1"
        ),
        "climate": "humid tropical (agroforestry)",
        "role": "primary within-climate validation",
    },
}


def fetch_zip(name: str, url: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    print(f"[{name}] downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r:  # noqa: S310 (trusted repo)
        blob = r.read()
    print(f"[{name}] {len(blob):,} bytes -> extracting")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        z.extractall(dest)
    print(f"[{name}] extracted to {dest}")


def main() -> int:
    for name, meta in SOURCES.items():
        try:
            fetch_zip(name, meta["zip_url"], RAW / name)
        except Exception as exc:  # noqa: BLE001
            print(f"[{name}] FAILED: {exc}", file=sys.stderr)
            return 1
    print("\nDone. Remember: de-duplicate any SoilTemp-derived set against "
          "data/processed/all_label_sites.csv before scoring (see ADR-015).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
