"""Distance-weighted Tversky index (DTI) — the official GEMS competition metric.

Transcribed from the official problem description, fetched and quoted in
``docs/sources.md`` (S1):

    k(d)  = max(1 - d/R, 0)                       R = 300 m = 3 px at 100 m
    TP_w  = sum_{g in G}  max_{x: d(x,g) <= R}  p(x) * k(d(x,g))
    FP_w  = sum_{x: p(x) > 0}  p(x) * [1 - max_{g in G} k(d(x,g))]
    FN_w  = sum_{g in G}  [1 - max_{x: d(x,g) <= R} p(x) * k(d(x,g))]
    DTI   = TP_w / (TP_w + alpha*FP_w + beta*FN_w + eps)      alpha=0.2, beta=0.8

Two properties are used deliberately for auditability and are asserted in
``tests/test_metric.py``:

* ``TP_w + FN_w == |G|`` for *any* prediction whatsoever (the two terms are the
  same maximum, complemented).  Hence
  ``DTI == TP_w / (0.2*(TP_w + FP_w) + 0.8*|G|)``.
* Scoring-mask semantics confirmed in writing by DrivenData staff (forum thread
  11516, posts 2 and 4): the mask over known USGS/INGENIOUS fault pixels is
  **pixel-exact and identical to the provided training labels**; those pixels are
  excluded from the penalty terms, and predictions within 300 m of a known fault
  receive **no** buffer.  ``known_mask`` implements exactly that.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ALPHA = 0.2
BETA = 0.8
EPS = 1e-7
R_PIXELS = 3.0
R_METERS = 300.0


@dataclass(frozen=True)
class DTIResult:
    """Result of one DTI evaluation. ``dti`` is the headline number."""

    dti: float
    tp_w: float
    fp_w: float
    fn_w: float
    truth_px: int
    mass: float
    emission_px: int
    scored_px: int

    def as_dict(self) -> dict:
        return {
            "dti": self.dti,
            "tp_w": self.tp_w,
            "fp_w": self.fp_w,
            "fn_w": self.fn_w,
            "truth_px": self.truth_px,
            "mass": self.mass,
            "emission_px": self.emission_px,
            "scored_px": self.scored_px,
        }


def kernel_offsets(r: float = R_PIXELS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Offsets and weights of the triangular kernel inside radius ``r`` (pixels)."""
    rad = int(np.ceil(r))
    dy, dx = np.mgrid[-rad : rad + 1, -rad : rad + 1]
    dist = np.sqrt((dx * dx + dy * dy).astype(np.float64))
    weight = np.maximum(1.0 - dist / r, 0.0)
    keep = weight > 0
    return dy[keep].astype(int), dx[keep].astype(int), weight[keep].astype(np.float32)


def _shift(arr: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Shift ``arr`` by (dy, dx) filling the vacated border with zeros."""
    out = np.zeros_like(arr)
    h, w = arr.shape
    ys, xs = max(0, dy), max(0, dx)
    ye, xe = min(h, h + dy), min(w, w + dx)
    yt, xt = max(0, -dy), max(0, -dx)
    out[ys:ye, xs:xe] = arr[yt : yt + (ye - ys), xt : xt + (xe - xs)]
    return out


def score(
    prediction: np.ndarray,
    truth: np.ndarray,
    *,
    known_mask: np.ndarray | None = None,
    valid: np.ndarray | None = None,
    alpha: float = ALPHA,
    beta: float = BETA,
    eps: float = EPS,
    r_pixels: float = R_PIXELS,
) -> DTIResult:
    """Official DTI.

    Parameters
    ----------
    prediction
        Probability/confidence raster, values in [0, 1]; NaN outside the footprint
        is treated as zero emission (the official format is NaN outside bounds).
    truth
        Binary ground-truth fault raster (1 = fault pixel).
    known_mask
        Binary raster of *known* catalogue fault pixels (``labels == 1``).  Those
        pixels are excluded from both the false-positive sum and the truth set —
        the pixel-exact mask of forum 11516 post 4.
    valid
        Boolean footprint mask (True where the pixel is scored at all).
    """
    pred = np.asarray(prediction, dtype=np.float32)
    pred = np.where(np.isfinite(pred), pred, 0.0)
    truth = (np.asarray(truth) > 0).astype(np.float32)
    if known_mask is not None:
        truth = truth * (1.0 - (np.asarray(known_mask) > 0).astype(np.float32))
    if valid is None:
        valid = np.ones(pred.shape, dtype=bool)
    else:
        valid = np.asarray(valid, dtype=bool)

    # Probabilities outside the valid footprint cannot score (NaN in a submission).
    pred = np.where(valid, pred, 0.0).astype(np.float32)
    truth = np.where(valid, truth, 0.0).astype(np.float32)

    dy, dx, w = kernel_offsets(r_pixels)

    # TP_w[g] = max_o p[g+o] * W[o] -> accumulate the max over all offsets.
    tp_map = np.zeros_like(pred)
    kn_map = np.zeros_like(pred)  # K[x] = max_g truth[g] k(d(x,g))
    for oy, ox, ww in zip(dy, dx, w):
        np.maximum(tp_map, _shift(pred * ww, -oy, -ox), out=tp_map)
        np.maximum(kn_map, _shift(truth * ww, oy, ox), out=kn_map)

    truth_px = int(truth.sum())
    tp_w = float(tp_map[truth > 0].sum())
    fn_w = float((1.0 - tp_map[truth > 0]).sum())

    emit = (pred > 0) & valid
    if known_mask is not None:
        emit = emit & ~(np.asarray(known_mask) > 0)
    fp_w = float((pred[emit] * (1.0 - kn_map[emit])).sum())

    denom = tp_w + alpha * fp_w + beta * fn_w + eps
    return DTIResult(
        dti=float(tp_w / denom) if denom > 0 else 0.0,
        tp_w=tp_w,
        fp_w=fp_w,
        fn_w=fn_w,
        truth_px=truth_px,
        mass=float(pred[emit].sum()),
        emission_px=int(emit.sum()),
        scored_px=int(valid.sum()),
    )


def blanket_floor(truth_px: int, fp_w: float) -> float:
    """DTI of a full-coverage unit prediction given its measured ``FP_w``."""
    return truth_px / (ALPHA * (truth_px + fp_w) + BETA * truth_px + EPS)


def margins(
    *, tp_w: float, fp_w: float, truth_px: int, dti: float, d_mass: float = 1.0
) -> dict:
    """Marginal value of one unit of mass: gained under a hit vs lost as a miss.

    With ``TP+FN = |G|`` the score is ``TP / (0.2*M + 0.8*|G|)`` where
    ``M = TP + FP`` is the emitted mass.  One extra unit of mass therefore:

    * costs ``0.2*d_mass`` in the denominator wherever it lands, and
    * if it lands on a truth pixel (k=1) it moves ``0.8`` from FN into TP.

    The ratio of the two is the exchange rate the submission policy is built on:
    a pixel is worth emitting only if ``P(new fault within 300 m)`` exceeds it.
    """
    denom = ALPHA * (tp_w + fp_w) + BETA * truth_px + EPS
    return {
        "cost_per_unit_mass": ALPHA * d_mass / denom,
        "gain_per_hit_unit_mass": (1.0 + BETA) * d_mass / denom,
        "break_even_probability": ALPHA / (1.0 + BETA),
        "current_dti": dti,
    }


class BlockResolvedScorer:
    """Fast, additive evaluation of the same metric over disjoint truth subsets.

    ``TP_w``, ``FP_w`` and ``FN_w`` are sums over disjoint sets of truth pixels,
    so their values for a union of blocks are the sums of the per-block values,
    and ``FN_w = |G| - TP_w`` holds inside every subset.  Pre-computing the
    kernel-max map of the *prediction* once per emission removes the cost that
    made the naive evaluation of 9 arms x 3 supports x 56 blocks infeasible.
    """

    def __init__(
        self,
        prediction: np.ndarray,
        *,
        valid: np.ndarray,
        known_mask: np.ndarray | None = None,
        block_id: np.ndarray | None = None,
        r_pixels: float = R_PIXELS,
    ):
        pred = np.asarray(prediction, dtype=np.float32)
        pred = np.where(np.isfinite(pred), pred, 0.0)
        self.valid = np.asarray(valid, dtype=bool)
        self.pred = np.where(self.valid, pred, 0.0).astype(np.float32)
        if known_mask is not None:
            self.known = np.asarray(known_mask, dtype=bool)
        else:
            self.known = np.zeros(self.pred.shape, dtype=bool)
        self.dy, self.dx, self.w = kernel_offsets(r_pixels)
        self.r_pixels = r_pixels
        self.block_id = block_id
        # A[g] = max_o p[g+o] * W[o]  (independent of which truth subset is scored)
        a = np.zeros_like(self.pred)
        for oy, ox, ww in zip(self.dy, self.dx, self.w):
            np.maximum(a, _shift(self.pred * ww, -oy, -ox), out=a)
        self.a_map = a
        emit = (self.pred > 0) & self.valid & ~self.known
        ys, xs = np.nonzero(emit)
        self.emit_y, self.emit_x = ys.astype(np.int32), xs.astype(np.int32)
        self.emit_p = self.pred[ys, xs].astype(np.float32)
        self.mass = float(self.emit_p.sum())
        self.emission_px = int(self.emit_p.size)

    def _offsets_for_emission(self) -> tuple[np.ndarray, np.ndarray]:
        return self.dy, self.dx

    def evaluate(self, truth: np.ndarray) -> DTIResult:
        t = np.asarray(truth) > 0
        t = t & self.valid & ~self.known
        tp = float(self.a_map[t].sum()) if t.any() else 0.0
        truth_px = int(t.sum())
        fn = float(truth_px - tp)
        fp = 0.0
        if self.emit_p.size:
            k = np.zeros(self.emit_p.shape, dtype=np.float32)
            for oy, ox, ww in zip(self.dy, self.dx, self.w):
                yy = self.emit_y + oy
                xx = self.emit_x + ox
                ok = (yy >= 0) & (yy < t.shape[0]) & (xx >= 0) & (xx < t.shape[1])
                contrib = np.zeros_like(k)
                if ok.any():
                    contrib[ok] = t[yy[ok], xx[ok]] * ww
                np.maximum(k, contrib, out=k)
            fp = float((self.emit_p * (1.0 - k)).sum())
        denom = tp + ALPHA * fp + BETA * fn + EPS
        return DTIResult(
            dti=float(tp / denom) if denom > 0 else 0.0,
            tp_w=tp,
            fp_w=fp,
            fn_w=fn,
            truth_px=truth_px,
            mass=self.mass,
            emission_px=self.emission_px,
            scored_px=int(self.valid.sum()),
        )

    def evaluate_subsets(
        self, truth: np.ndarray, block_id: np.ndarray, labels
    ) -> dict[int, DTIResult]:
        """Exact per-subset DTI (a subset = a set of contiguous blocks of truth).

        ``FP_w`` for a subset is the emitted mass *not* credited to that subset's
        own truth: ``FP = mass - sum_x p(x) * max_g k(d(x,g))``, with the maximum
        taken over that subset's truth pixels only.  Credits are computed with a
        KD-tree over the subset's truth coordinates, so no approximation is made
        for pixels whose best offset is not the nearest one.
        """
        from scipy.spatial import cKDTree

        t = (np.asarray(truth) > 0) & self.valid & ~self.known
        out: dict[int, DTIResult] = {}
        if self.block_id is None:
            raise ValueError("block_id required")
        rows, cols = np.nonzero(t)
        if rows.size == 0:
            return out
        block_of_truth = self.block_id[rows, cols]
        keep = np.isin(block_of_truth, np.asarray(labels, dtype=int))
        rows, cols, block_of_truth = rows[keep], cols[keep], block_of_truth[keep]
        if rows.size == 0:
            return out
        emit_xy = np.column_stack([self.emit_y, self.emit_x]).astype(np.float64)
        tree_emit = cKDTree(emit_xy) if emit_xy.size else None
        for b in np.unique(block_of_truth).tolist():
            sel = block_of_truth == b
            gy, gx = rows[sel], cols[sel]
            tp = float(self.a_map[gy, gx].sum())
            truth_px = int(sel.sum())
            fn = float(truth_px - tp)
            if tree_emit is None:
                credited = 0.0
            else:
                dist, idx = tree_emit.query(np.column_stack([gy, gx]).astype(np.float64), k=1,
                                            distance_upper_bound=self.r_pixels + 1e-9)
                ok = np.isfinite(dist) & (idx < self.emit_p.size)
                k = np.maximum(1.0 - (dist[ok] / self.r_pixels), 0.0)
                credited = float((self.emit_p[idx[ok]] * k).sum()) if ok.any() else 0.0
            fp = float(max(self.mass - credited, 0.0))
            denom = tp + ALPHA * fp + BETA * fn + EPS
            out[int(b)] = DTIResult(
                dti=float(tp / denom) if denom > 0 else 0.0,
                tp_w=tp, fp_w=fp, fn_w=fn, truth_px=truth_px,
                mass=self.mass, emission_px=self.emission_px,
                scored_px=int(self.valid.sum()),
            )
        return out
