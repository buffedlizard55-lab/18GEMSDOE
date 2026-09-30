"""Lineament fields for the GEMS Prize: derivatives, ridges, and agreement.

Every operator here is a *mechanism* statement, not a filter chosen because it
looks right (``docs/research/hypotheses.md`` states the mechanism, the specific
non-fault process that produces the same pattern, and the test that separates
them):

* horizontal-gradient magnitude (HGM) — a fault plane juxtaposes rocks of
  different density and magnetic susceptibility, so the gradient of the
  potential field peaks over the trace of the plane;
* tilt derivative (TDR) — arctan of the vertical over the horizontal gradient;
  it changes sign across a contact/fault, so its zero-crossing locates the edge
  independently of the amplitude of the anomaly and of its depth;
* curvature (Laplacian) of detrended elevation — a scarp is a break in slope;
  its second derivative localises the break even when the scarp is degraded.

All operators are computed at several scales (Gaussian sigma in pixels,
1 px = 100 m) because the depth of the source and the length of the structure
are unknown a priori.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

SCALES_PX = (2.0, 4.0, 8.0, 15.0)


def robust_normalise(arr: np.ndarray, *, lo: float = 2.0, hi: float = 98.0) -> np.ndarray:
    """Percentile stretch to [0, 1]; NaN preserved as NaN."""
    a = np.asarray(arr, dtype=np.float32)
    finite = np.isfinite(a)
    if not finite.any():
        return np.zeros_like(a)
    vals = a[finite]
    p_lo, p_hi = np.percentile(vals, [lo, hi])
    if not np.isfinite(p_lo) or not np.isfinite(p_hi) or p_hi <= p_lo:
        return np.zeros_like(a)
    out = np.zeros_like(a)
    out[finite] = np.clip((a[finite] - p_lo) / (p_hi - p_lo), 0.0, 1.0)
    return out


def fill_nan(arr: np.ndarray) -> np.ndarray:
    """Replace non-finite cells with the finite median so derivatives stay local."""
    a = np.asarray(arr, dtype=np.float32)
    finite = np.isfinite(a)
    if finite.all():
        return a
    if not finite.any():
        return np.zeros_like(a)
    return np.where(finite, a, np.float32(np.median(a[finite]))).astype(np.float32)


def smooth(arr: np.ndarray, sigma: float) -> np.ndarray:
    return ndimage.gaussian_filter(arr, sigma=sigma, mode="nearest")


def gradient(arr: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    gy = ndimage.sobel(smooth(arr, sigma), axis=0, mode="nearest") / (8.0 * 100.0)
    gx = ndimage.sobel(smooth(arr, sigma), axis=1, mode="nearest") / (8.0 * 100.0)
    return gy, gx


def hgm(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Horizontal gradient magnitude in nT (or mGal) per metre."""
    gy, gx = gradient(arr, sigma)
    return np.hypot(gx, gy).astype(np.float32)


def vertical_gradient(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Second vertical derivative approximated by the negative Laplacian."""
    return (-ndimage.laplace(smooth(arr, sigma), mode="nearest")).astype(np.float32)


def tilt_derivative(arr: np.ndarray, sigma: float) -> np.ndarray:
    """TDR = atan2(dV/dz, sqrt((dV/dx)^2 + (dV/dy)^2)) in radians."""
    vg = vertical_gradient(arr, sigma)
    h = hgm(arr, sigma) * 100.0  # back to per-pixel units of the vertical term
    return np.arctan2(vg, np.maximum(h, 1e-12)).astype(np.float32)


def curvature(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Laplacian of elevation: a break in slope, i.e. a scarp, localises here."""
    return ndimage.laplace(smooth(arr, sigma), mode="nearest").astype(np.float32)


def multiscale_max(builder, arr: np.ndarray, scales=SCALES_PX) -> np.ndarray:
    """Normalise each scale, then take the per-pixel maximum across scales."""
    out = None
    for s in scales:
        band = robust_normalise(np.abs(builder(arr, s)))
        out = band if out is None else np.maximum(out, band)
    return out


def nms_ridges(strength: np.ndarray, gy: np.ndarray, gx: np.ndarray) -> np.ndarray:
    """Non-maximum suppression along the gradient direction -> 1 px wide ridges.

    A ridge of the gradient magnitude lies across the gradient direction, so a
    pixel survives when its strength is the local maximum of its two neighbours
    along the gradient vector (the Canny criterion, applied to a field that is
    itself a derivative).
    """
    mag = np.hypot(gx, gy)
    with np.errstate(invalid="ignore", divide="ignore"):
        ny = np.where(mag > 0, gy / mag, 0.0)
        nx = np.where(mag > 0, gx / mag, 0.0)
    # Quantise to 4 orientations: 0/90/45/135 degrees.
    ang = (np.degrees(np.arctan2(ny, nx)) + 180.0) % 180.0
    keep = np.zeros(strength.shape, dtype=bool)
    # 0 deg (E-W gradient -> compare N/S neighbours), etc.
    bins = [(0, 22.5), (22.5, 67.5), (67.5, 112.5), (112.5, 157.5), (157.5, 180.0)]
    for lo, hi in bins:
        sel = (ang >= lo) & (ang < hi)
        if not sel.any():
            continue
        if lo == 0 or hi == 180.0:
            a = np.roll(strength, 1, axis=0)
            b = np.roll(strength, -1, axis=0)
        elif lo == 22.5:
            a = np.roll(np.roll(strength, 1, axis=0), 1, axis=1)
            b = np.roll(np.roll(strength, -1, axis=0), -1, axis=1)
        elif lo == 67.5:
            a = np.roll(strength, 1, axis=1)
            b = np.roll(strength, -1, axis=1)
        else:
            a = np.roll(np.roll(strength, 1, axis=0), -1, axis=1)
            b = np.roll(np.roll(strength, -1, axis=0), 1, axis=1)
        keep |= sel & (strength >= a) & (strength >= b)
    out = np.where(keep, strength, 0.0).astype(np.float32)
    out[0, :] = 0.0
    out[-1, :] = 0.0
    out[:, 0] = 0.0
    out[:, -1] = 0.0
    return out


def boundary_safe_mask(valid: np.ndarray, sigma: float = 4.0, frac: float = 0.9) -> np.ndarray:
    """Cells far enough from the survey/data boundary that gradients are real.

    ``fill_nan`` replaces missing cells with a constant, which manufactures an
    artificial edge along the data boundary.  Any detector that reads that edge
    as a lineament is measuring the *mask*, not the geology, so ridge pixels are
    restricted to cells whose neighbourhood is almost entirely valid.
    """
    coverage = ndimage.gaussian_filter(valid.astype(np.float32), sigma=sigma, mode="nearest")
    return coverage >= frac


def ridge_map(
    field: np.ndarray,
    gy: np.ndarray,
    gx: np.ndarray,
    *,
    valid: np.ndarray | None = None,
    min_quantile: float = 0.9,
) -> np.ndarray:
    """1 px wide ridge strength (normalised 0..1), gated to significant ridges.

    Two gates keep the ridge set physical rather than noise-driven:

    * ``min_quantile`` — only ridges in the strongest tail of the strength
      distribution survive (a ridge that is not distinguishable from the local
      background is not a lineament);
    * ``valid`` — the data-boundary mask above, so the edge of the survey is
      never mistaken for a structure.
    """
    norm = robust_normalise(field)
    ridge = nms_ridges(norm, gy, gx)
    positive = ridge[ridge > 0]
    if positive.size == 0:
        return ridge
    threshold = float(np.quantile(positive, min_quantile))
    ridge = np.where(ridge >= threshold, ridge, 0.0).astype(np.float32)
    if valid is not None:
        ridge = np.where(boundary_safe_mask(valid), ridge, 0.0).astype(np.float32)
    return ridge


def dilate(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    return ndimage.binary_dilation(mask, iterations=iterations)


def agreement_2plus(masks: list[np.ndarray], radius: int = 1) -> np.ndarray:
    """Conjunction: pixels where at least two *independent* families have a ridge.

    Two physically independent layers agreeing at one location is far less
    likely by chance than either alone — that is the evidential claim, and the
    random-lineament control in ``scripts/run_detectors.py`` measures how much
    agreement a matched random network produces by chance.
    """
    votes = np.zeros(masks[0].shape, dtype=np.uint8)
    for m in masks:
        votes += dilate(m, radius).astype(np.uint8)
    return votes >= 2
