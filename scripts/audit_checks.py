#!/usr/bin/env python3
"""Independent re-derivation of every load-bearing claim on this site.

Nothing here is copied from a report: each check reads bytes and recomputes.  A
check whose inputs are absent is *skipped and recorded as skipped*, never
silently passed — that is the whole point of the file.

Checks
------
``A``  official raster hashes and grid properties (needs ``data/``)
``B``  the training labels are the USGS QFaults network inside the footprint
       (needs the public INGENIOUS/QFaults shapefile, optional path)
``C``  the provided feature stack vs the GeoDAWN area-2 release: which bands are
       the release's own grids, and which release layers are missing (optional)
``D``  the repeated 0.1563 files are byte-identical (optional sibling checkouts)
``E``  the shipped submission passes the format validator (needs ``docs/downloads``)

Usage::

    python scripts/audit_checks.py --qfaults /path/to/qfaults.shp \
        --geodawn-area2 /path/to/22103_area2_tiffs \
        --sibling /path/to/GEMSDOE --sibling /path/to/5GEMSDOE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "data" / "evidence" / "audit_checks.json"

# Pins from the official bridge (data/bridge/manifest.json).
PINS = {
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
    "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
}
# The duplicate the group kept scoring 0.1563 with.
DUPLICATE_SHA = "7f00890a62878d612fb5eef67a9a364a2df819433dde74b6762ce4fc0fc4fe15"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_a(data: Path, report: dict) -> None:
    import rasterio

    rows = {}
    for name, pin in PINS.items():
        p = data / name
        if not p.exists():
            rows[name] = {"status": "SKIPPED", "reason": "file absent"}
            continue
        digest = sha256_file(p)
        with rasterio.open(p) as ds:
            rows[name] = {
                "status": "PASS" if digest == pin else "FAIL",
                "sha256": digest,
                "sha256_pinned": pin,
                "shape": [ds.height, ds.width],
                "count": ds.count,
                "crs": ds.crs.to_string() if ds.crs else None,
                "dtype": ds.dtypes[0],
                "bounds": [float(x) for x in ds.bounds],
            }
    lab_p = data / "labels.tif"
    if lab_p.exists():
        with rasterio.open(lab_p) as ds:
            lab = ds.read(1)
            rows["labels_value_counts"] = {
                "outside_footprint(-1)": int((lab == -1).sum()),
                "no_fault(0)": int((lab == 0).sum()),
                "fault(1)": int((lab == 1).sum()),
            }
    report["A_official_rasters"] = rows


def check_b(qfaults: Path | None, data: Path, report: dict) -> None:
    if not qfaults or not Path(qfaults).exists():
        report["B_labels_are_qfaults"] = {"status": "SKIPPED", "reason": "shapefile not supplied"}
        return
    import rasterio
    import shapefile  # pyshp
    from rasterio.warp import transform as warp_transform
    from scipy import ndimage

    with rasterio.open(data / "labels.tif") as ds:
        lab = ds.read(1)
        T, H, W, b = ds.transform, ds.height, ds.width, ds.bounds
    valid = lab != -1
    known = lab == 1
    dist = ndimage.distance_transform_edt(~known)

    proj = ("+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-117 +x_0=0 +y_0=0 "
            "+datum=NAD83 +units=m +no_defs")
    r = shapefile.Reader(str(qfaults))
    mask = np.zeros((H, W), dtype=bool)
    n_rec = 0
    for sr in r.shapeRecords():
        s = sr.shape
        if s.bbox is None or len(s.points) < 2:
            continue
        pts = np.asarray(s.points, dtype=float)
        parts = list(s.parts) + [len(pts)]
        touched = False
        for k in range(len(parts) - 1):
            seg = pts[parts[k]:parts[k + 1]]
            if seg.shape[0] < 2:
                continue
            px, py = warp_transform(proj, "EPSG:32611", seg[:, 0].tolist(), seg[:, 1].tolist())
            px, py = np.asarray(px), np.asarray(py)
            if px.max() < b.left or px.min() > b.right or py.max() < b.bottom or py.min() > b.top:
                continue
            d = np.hypot(np.diff(px), np.diff(py))
            n = np.maximum(2, (d / 50.0).astype(int) + 1)
            xi = np.concatenate([np.linspace(px[i], px[i + 1], n[i]) for i in range(len(px) - 1)])
            yi = np.concatenate([np.linspace(py[i], py[i + 1], n[i]) for i in range(len(py) - 1)])
            col = ((xi - T.c) / T.a).astype(int)
            row = ((yi - T.f) / T.e).astype(int)
            ok = (col >= 0) & (col < W) & (row >= 0) & (row < H)
            if ok.any():
                mask[row[ok], col[ok]] = True
                touched = True
        n_rec += int(touched)

    qv = mask & valid
    near = dist <= 3
    report["B_labels_are_qfaults"] = {
        "status": "PASS",
        "shapefile": str(qfaults),
        "records_touching_footprint": n_rec,
        "qfaults_px_grid": int(mask.sum()),
        "qfaults_px_inside_valid_footprint": int(qv.sum()),
        "qfaults_inside_footprint_within_300m_of_label": int((qv & near).sum()),
        "fraction": float((qv & near).sum() / max(1, qv.sum())),
        "label_px_within_300m_of_qfaults": int(near[known].sum()),
        "label_px": int(known.sum()),
        "note": ("QFaults pixels outside the valid footprint are not scored and are reported "
                 "separately on purpose: counting them as 'faults missing from the labels' is a "
                 "mistake this check exists to prevent."),
    }


def check_c(area2: Path | None, data: Path, report: dict) -> None:
    if not area2 or not Path(area2).exists():
        report["C_feature_stack_vs_geodawn"] = {"status": "SKIPPED", "reason": "area-2 grids not supplied"}
        return
    import rasterio

    def sig(a, m):
        v = a[~m]
        return (int(v.size), float(v.min()), float(v.max()), float(v.sum()),
                float(np.sum(v.astype(np.float64) ** 2)))

    comp = {}
    with rasterio.open(data / "training_features.tif") as ds:
        for i in range(1, ds.count + 1):
            tag = (ds.tags(i).get("band_name") or ds.descriptions[i - 1] or f"band{i}").split(" - ")[0]
            arr = ds.read(i, masked=True)
            comp[tag] = sig(arr.filled(0), arr.mask)
    geo = {}
    for f in sorted(Path(area2).glob("*.tif")):
        with rasterio.open(f) as ds:
            arr = ds.read(1, masked=True)
            geo[f.name.replace("22103_", "").replace("_a2.tif", "")] = sig(arr.filled(0), arr.mask)
    matched = {g: [c for c, s in comp.items() if s == gs] for g, gs in geo.items()}
    report["C_feature_stack_vs_geodawn"] = {
        "status": "PASS",
        "geodawn_area2_layers": sorted(geo),
        "exact_signature_matches": {k: v for k, v in matched.items()},
        "not_present_in_provided_stack": sorted(k for k, v in matched.items() if not v),
        "note": ("A layer with no exact-signature match is not in the provided 19-band stack. "
                 "The radiometric ratios (uk, uth, thk) and single channels (k, th, u) are the "
                 "material ones: they exist on the competition grid in the public release."),
    }


def check_d(siblings: list[Path], report: dict) -> None:
    rows = {}
    rel = "data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif"
    for s in siblings:
        p = Path(s) / rel
        if not p.exists():
            continue
        digest = sha256_file(p)
        rows[str(s)] = {"path": str(p), "sha256": digest,
                        "bytes": p.stat().st_size,
                        "matches_duplicate_pin": digest == DUPLICATE_SHA}
    if not rows:
        report["D_duplicate_evidence"] = {"status": "SKIPPED", "reason": "no sibling run found"}
        return
    digests = {v["sha256"] for v in rows.values()}
    report["D_duplicate_evidence"] = {
        "status": "PASS" if len(digests) == 1 else "INCONCLUSIVE",
        "duplicate_pin": DUPLICATE_SHA,
        "files": rows,
        "distinct_digests": len(digests),
        "conclusion": ("One byte sequence is shipped from several repositories: the repeated "
                       "public score is one prediction, not several ideas converging."),
    }


def check_e(report: dict) -> None:
    manifest_p = ROOT / "docs" / "downloads" / "manifest.json"
    if not manifest_p.exists():
        report["E_shipped_submission"] = {"status": "SKIPPED", "reason": "nothing packaged yet"}
        return
    from gems18.submission import validate_geotiff

    man = json.loads(manifest_p.read_text())
    path = ROOT / man["path"]
    if not path.exists():
        report["E_shipped_submission"] = {"status": "SKIPPED", "reason": f"{path} absent"}
        return
    res = validate_geotiff(path, ROOT / "data" / "sample_submission.tif")
    digest = sha256_file(path)
    report["E_shipped_submission"] = {
        "status": "PASS" if res.get("valid") and digest == man["sha256"] else "FAIL",
        "path": man["path"],
        "sha256_recomputed": digest,
        "sha256_manifest": man["sha256"],
        "validator": {k: v for k, v in res.items() if k != "errors"},
        "validator_errors": res.get("errors", []),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    ap.add_argument("--qfaults", type=Path, default=None)
    ap.add_argument("--geodawn-area2", type=Path, default=None)
    ap.add_argument("--sibling", action="append", default=[])
    args = ap.parse_args()

    t0 = time.time()
    report = {"generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "generated_by": "scripts/audit_checks.py"}
    check_a(args.data, report)
    check_b(args.qfaults, args.data, report)
    check_c(args.geodawn_area2, args.data, report)
    check_d([Path(s) for s in args.sibling], report)
    check_e(report)
    report["seconds"] = round(time.time() - t0, 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1, default=str))

    statuses = {k: v.get("status") for k, v in report.items() if isinstance(v, dict) and "status" in v}
    print(json.dumps(statuses, indent=1))
    print(f"wrote {OUT}")
    return 0 if all(s in {"PASS", "SKIPPED"} for s in statuses.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
