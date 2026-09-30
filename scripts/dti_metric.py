"""Distance-weighted Tversky index (DTI) — exact transcription of the official spec.

Source: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  k(d) = max(1 - d/R, 0), R = 300 m
  TPw = sum over truth pixels of max_{x within R} p(x)*k(d)
  FPw = sum over predicted pixels of p(x)*[1 - max_g k(d)]
  FNw = sum over truth pixels of [1 - max_{x within R} p(x)*k(d)]
  DTI = TPw / (TPw + alpha*FPw + beta*FNw + eps), alpha=0.2, beta=0.8

Official worked fixture: TPw=3.00, FPw=1.89, FNw=2.00 -> DTI = 0.60.
Run `python dti_metric.py --selftest` to verify the transcription (no data needed).

Conventions (must match the scorer):
  - p in [0, 1]; NaN in predictions is treated as 0.0 (matches sibling-verified
    scorer behavior AND the "outside bounds is null/NaN" convention).
  - Known USGS/INGENIOUS fault pixels are masked/excluded from scoring, both
    rounds (staff: forum 11516). Pass `known_mask` to apply it.
  - Distances in PIXELS; convert R=300 m -> 3 px at 100 m resolution.
"""

from __future__ import annotations

import argparse
import math

import numpy as np

try:
    from scipy.ndimage import distance_transform_edt  # type: ignore
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY = False

ALPHA = 0.2
BETA = 0.8
R_METERS = 300.0
PIXEL_METERS = 100.0
R_PIXELS = R_METERS / PIXEL_METERS  # 3.0
EPS = 1e-12


def triangular_kernel(dist_px: np.ndarray, r_px: float = R_PIXELS) -> np.ndarray:
    return np.maximum(1.0 - dist_px / r_px, 0.0)


def _require_scipy() -> None:
    if not _HAVE_SCIPY:
        raise ImportError(
            "scipy is required for distance transforms. "
            "Install with: conda env create -f environment.yml"
        )


def distance_weighted_tversky(
    p: np.ndarray,
    g: np.ndarray,
    known_mask: np.ndarray | None = None,
    alpha: float = ALPHA,
    beta: float = BETA,
    r_px: float = R_PIXELS,
) -> dict:
    """Compute DTI and its components.

    Args:
        p: predicted probabilities, any shape, values in [0, 1], NaN treated as 0.
        g: binary ground truth (0/1), same shape as p.
        known_mask: boolean array, True where known-fault pixels are EXCLUDED
            from scoring (forum 11516). Applied to both p and g.
    """
    _require_scipy()
    p = np.asarray(p, dtype=np.float64)
    g = np.asarray(g, dtype=np.float64)
    if p.shape != g.shape:
        raise ValueError(f"shape mismatch: p {p.shape} vs g {g.shape}")
    p = np.where(np.isfinite(p), p, 0.0)
    if np.any((p < 0.0) | (p > 1.0)):
        raise ValueError("predictions must be in [0, 1]")
    if known_mask is not None:
        known = np.asarray(known_mask, dtype=bool)
        if known.shape != p.shape:
            raise ValueError("known_mask shape mismatch")
        p = np.where(known, 0.0, p)
        g = np.where(known, 0.0, g)

    truth = g > 0.5
    if not np.any(truth):
        return {"dti": 1.0 if not np.any(p > 0) else 0.0,
                "tpw": 0.0, "fpw": float(np.sum(p)), "fnw": 0.0}

    # For each pixel: distance to nearest truth pixel -> k(d(x, G)).
    dist_to_truth = distance_transform_edt(~truth)
    k_to_truth = triangular_kernel(dist_to_truth, r_px)

    # FPw: predicted mass weighted by (1 - best kernel to truth).
    fpw = float(np.sum(p * (1.0 - k_to_truth)))

    # Per-truth-pixel best kernel-weighted prediction within R.
    # Exact per spec: max over x within R of p(x)*k(d(x,g)).
    # Computed via distance transform trick on thresholded fields is complex;
    # brute force with a local window is exact and fine for holdout tiles.
    tpw = 0.0
    R = int(math.ceil(r_px))
    H, W = p.shape
    ys, xs = np.nonzero(truth)
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    win_k = triangular_kernel(np.sqrt(yy * yy + xx * xx), r_px)
    for y, x in zip(ys.tolist(), xs.tolist()):
        y0, y1 = max(0, y - R), min(H, y + R + 1)
        x0, x1 = max(0, x - R), min(W, x + R + 1)
        ky0, ky1 = y0 - (y - R), y1 - (y - R)
        kx0, kx1 = x0 - (x - R), x1 - (x - R)
        best = float(np.max(p[y0:y1, x0:x1] * win_k[ky0:ky1, kx0:kx1]))
        tpw += best
    fnw = float(len(ys) - tpw)
    dti = tpw / (tpw + alpha * fpw + beta * fnw + EPS)
    return {"dti": float(dti), "tpw": float(tpw), "fpw": fpw, "fnw": fnw}


def selftest() -> None:
    """Official worked fixture: TPw=3.00, FPw=1.89, FNw=2.00 -> 0.60."""
    tpw, fpw, fnw = 3.00, 1.89, 2.00
    dti = tpw / (tpw + ALPHA * fpw + BETA * fnw + EPS)
    # Official page prints 0.60 (two decimals); exact value is 3/4.978 ≈ 0.6027.
    assert abs(dti - 0.60265) < 1e-3, dti
    # Synthetic sanity: perfect 1-px prediction on 1-px truth -> DTI 1.0.
    p = np.zeros((11, 11)); g = np.zeros((11, 11))
    p[5, 5] = 1.0; g[5, 5] = 1.0
    r = distance_weighted_tversky(p, g)
    assert abs(r["dti"] - 1.0) < 1e-9, r
    # All-zero prediction -> DTI 0.0 with FNw = #truth.
    r0 = distance_weighted_tversky(np.zeros((11, 11)), g)
    assert abs(r0["dti"]) < 1e-9 and abs(r0["fnw"] - 1.0) < 1e-9, r0
    # Masking: truth on a known pixel is excluded -> DTI 1.0 even with p=0.
    known = np.zeros((11, 11), bool); known[5, 5] = True
    rm = distance_weighted_tversky(np.zeros((11, 11)), g, known_mask=known)
    assert abs(rm["dti"] - 1.0) < 1e-9, rm
    print("DTI selftest PASS: fixture 0.60, perfect 1.0, zero 0.0, masking OK.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DTI metric selftest (no data needed).")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    else:
        ap.print_help()
