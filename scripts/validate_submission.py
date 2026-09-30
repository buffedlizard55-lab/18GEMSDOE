"""13-gate submission-format validator. Run on EVERY candidate before upload.

Usage:
    python scripts/validate_submission.py candidate.tif --template sample_submission.tif

Gates (spec: problem description "Submission format" + official sample profile):
  hard: single band, float32, CRS EPSG:32611, shape==template, transform==template,
        footprint all finite, footprint range [0,1] via 3 independent read paths
  advisory-but-reported: outside-footprint NaN, nodata==NaN, profile==template,
        strict whole-array range (expected N/A whenever NaN-outside is used)

Exit code 0 only if every HARD gate passes. Prints sha256 + pixel census +
the sha8 content-id to paste into the DrivenData note field.

Requires: rasterio, numpy. See environment.yml.
"""

from __future__ import annotations

import argparse
import hashlib
import sys

import numpy as np

try:
    import rasterio  # type: ignore
except Exception as e:  # pragma: no cover
    print(f"FATAL: rasterio is required: {e}", file=sys.stderr)
    print("Install with: conda env create -f environment.yml", file=sys.stderr)
    sys.exit(2)


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a GEMS submission GeoTIFF.")
    ap.add_argument("candidate", help="candidate .tif to check")
    ap.add_argument("--template", required=True, help="official sample_submission.tif")
    args = ap.parse_args()

    results: list[tuple[str, str, bool, str]] = []  # (name, kind, pass, detail)

    def gate(name: str, kind: str, ok: bool, detail: str = "") -> None:
        results.append((name, kind, bool(ok), detail))

    with rasterio.open(args.template) as t:
        t_profile = t.profile.copy()
        t_arr = t.read(1)
        t_transform, t_crs, t_shape = t.transform, t.crs, t_arr.shape
    # Footprint = template's finite pixels (official sample: 0.0 inside, NaN outside).
    footprint = np.isfinite(t_arr)
    n_in, n_out = int(footprint.sum()), int((~footprint).sum())

    digest = sha256_of(args.candidate)
    with rasterio.open(args.candidate) as c:
        c_profile = c.profile.copy()
        count, dtypes = c.count, c.dtypes
        arr = c.read(1)
        gate("single band", "hard", count == 1, f"count={count}")
        gate("dtype float32", "hard", tuple(dtypes) == ("float32",), f"dtypes={dtypes}")
        gate("crs epsg 32611", "hard",
             c.crs is not None and c.crs.to_epsg() == 32611, f"crs={c.crs}")
        gate("shape matches template", "hard", arr.shape == t_shape,
             f"{arr.shape} vs {t_shape}")
        gate("geotransform matches template", "hard", c.transform == t_transform,
             f"{tuple(c.transform)} vs {tuple(t_transform)}")
        inside = arr[footprint]
        gate("footprint all finite", "hard",
             bool(np.all(np.isfinite(inside))),
             f"{int((~np.isfinite(inside)).sum())} NaN/Inf inside {n_in}-px footprint")
        finite_inside = inside[np.isfinite(inside)]
        in_range = finite_inside.size == inside.size and (
            finite_inside.size == 0 or
            (float(finite_inside.min()) >= 0.0 and float(finite_inside.max()) <= 1.0))
        lo = float(finite_inside.min()) if finite_inside.size else float("nan")
        hi = float(finite_inside.max()) if finite_inside.size else float("nan")
        gate("footprint range 0 1", "hard", bool(in_range), f"min={lo} max={hi}")
        outside = arr[~footprint]
        gate("outside is nan (official text)", "advisory",
             bool(np.all(~np.isfinite(outside))) if outside.size else True,
             f"{int(np.isfinite(outside).sum())} finite outside / {n_out}")
        gate("nodata tag is nan", "advisory",
             c.nodata is not None and float(c.nodata) != float(c.nodata),
             f"nodata={c.nodata!r}")
        # Three independent range-check read paths (whole-array + masked).
        gate("variant nan-aware whole array", "hard",
             bool(np.nanmin(arr) >= 0.0 and np.nanmax(arr) <= 1.0),
             f"nanmin={float(np.nanmin(arr))} nanmax={float(np.nanmax(arr))}")
    with rasterio.open(args.candidate) as c2:
        masked = c2.read(1, masked=True).compressed()
        gate("variant masked read", "hard",
             bool(masked.size == 0 or (masked.min() >= 0.0 and masked.max() <= 1.0)),
             f"n={masked.size}")
    gate("variant strict whole-array (no NaN allowed)", "advisory-na", True,
         "informational only: rejects ANY NaN incl. official-convention outside pixels")
    same_profile = all(c_profile.get(k) == t_profile.get(k)
                       for k in ("driver", "dtype", "nodata", "width", "height", "crs", "transform"))
    gate("profile matches official sample", "advisory", bool(same_profile), "")

    hard_ok = all(ok for _, kind, ok, _ in results if kind == "hard")
    print(f"file: {args.candidate}")
    print(f"sha256: {digest}  (content id for upload note: {digest[:8]})")
    print(f"footprint: {n_in} inside / {n_out} outside; "
          f"inside @1.0: {int(np.sum(inside == 1.0))}, @0.0: {int(np.sum(inside == 0.0))}")
    for name, kind, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] ({kind}) {name} {detail}")
    n_hard = sum(1 for _, kind, _, _ in results if kind == "hard")
    n_hard_ok = sum(1 for _, kind, ok, _ in results if kind == "hard" and ok)
    print("VERDICT:", f"HARD-GATE PASS ({n_hard_ok}/{n_hard}) — safe to upload"
          if hard_ok else "FAIL — do NOT upload; fix failing hard gates first")
    return 0 if hard_ok else 1


if __name__ == "__main__":
    sys.exit(main())
