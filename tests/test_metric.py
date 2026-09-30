"""Metric tests anchored to sources, not to the implementation.

Anchor 1 — the official worked example (DrivenData problem description,
"Scoring example"): TP_w = 3.00, FP_w = 1.89, FN_w = 2.00 with alpha = 0.2 and
beta = 0.8 gives 0.60.  Reproduced here from the published numbers alone.

Anchor 2 — the algebraic identity TP_w + FN_w = |G|, which follows directly from
the two published definitions and is asserted on synthetic rasters.

Anchor 3 — mask semantics stated in writing by DrivenData staff (forum 11516
posts 2 and 4): the known-fault mask is pixel-exact, so a prediction on those
pixels is neither penalised nor credited.
"""

from __future__ import annotations

import numpy as np
import pytest

from gems18.metric import ALPHA, BETA, blanket_floor, margins, score


def test_official_worked_example_arithmetic():
    """3.00 / (3.00 + 0.2*1.89 + 0.8*2.00) = 0.6027 ~= the published 0.60."""
    dti = 3.00 / (3.00 + ALPHA * 1.89 + BETA * 2.00)
    assert dti == pytest.approx(0.6027, abs=5e-4)
    assert round(dti, 2) == 0.60


def test_perfect_prediction_scores_one():
    rng = np.random.default_rng(0)
    truth = np.zeros((64, 64), dtype=np.float32)
    truth[20:44, 30] = 1.0
    truth[10, 15:40] = 1.0
    pred = truth.copy()
    res = score(pred, truth)
    assert res.dti > 0.999
    assert res.fp_w == pytest.approx(0.0, abs=1e-6)
    assert res.tp_w == pytest.approx(res.truth_px, abs=1e-4)


def test_zero_prediction_scores_zero():
    truth = np.zeros((32, 32), dtype=np.float32)
    truth[5, 5:25] = 1.0
    res = score(np.zeros_like(truth), truth)
    assert res.dti == 0.0
    assert res.fn_w == pytest.approx(res.truth_px)


def test_tp_plus_fn_equals_truth_count():
    """TP_w + FN_w == |G| identically (both are the same maximised term)."""
    rng = np.random.default_rng(1)
    truth = (rng.random((48, 48)) < 0.02).astype(np.float32)
    for field in (rng.random((48, 48)).astype(np.float32), np.full((48, 48), 0.3, np.float32)):
        res = score(field, truth)
        assert res.tp_w + res.fn_w == pytest.approx(res.truth_px, abs=1e-3)


def test_dti_identity_form():
    """DTI == TP_w / (0.2*(TP_w + FP_w) + 0.8*|G|)."""
    rng = np.random.default_rng(2)
    truth = (rng.random((40, 40)) < 0.05).astype(np.float32)
    pred = (rng.random((40, 40)) < 0.1).astype(np.float32)
    res = score(pred, truth)
    expected = res.tp_w / (0.2 * (res.tp_w + res.fp_w) + 0.8 * res.truth_px + 1e-7)
    assert res.dti == pytest.approx(expected)


def test_known_mask_is_pixel_exact_and_free():
    """Predicting known-fault pixels neither helps nor hurts (forum 11516/4)."""
    truth = np.zeros((32, 32), dtype=np.float32)
    truth[16, 4:28] = 1.0
    known = np.zeros((32, 32), dtype=np.float32)
    known[8, :] = 1.0
    pred = np.zeros((32, 32), dtype=np.float32)
    pred[16, 4:28] = 1.0
    base = score(pred, truth, known_mask=known)
    with_known = pred.copy()
    with_known[known > 0] = 1.0
    masked = score(with_known, truth, known_mask=known)
    assert masked.dti == pytest.approx(base.dti, abs=1e-9)
    # ... and a prediction 1 px off the known fault is NOT buffered: it is penalised.
    off = np.zeros((32, 32), dtype=np.float32)
    off[9, :] = 1.0
    assert score(off, truth, known_mask=known).fp_w > 0.0


def test_distance_weighting_degrades_with_offset():
    truth = np.zeros((32, 32), dtype=np.float32)
    truth[16, 16] = 1.0
    on = np.zeros((32, 32), dtype=np.float32)
    on[16, 16] = 1.0
    one_px = np.zeros((32, 32), dtype=np.float32)
    one_px[16, 17] = 1.0
    three_px = np.zeros((32, 32), dtype=np.float32)
    three_px[16, 19] = 1.0
    assert score(on, truth).tp_w == pytest.approx(1.0)
    assert score(one_px, truth).tp_w == pytest.approx(1.0 - 1.0 / 3.0, abs=1e-6)
    assert score(three_px, truth).tp_w == pytest.approx(0.0, abs=1e-6)


def test_blanket_floor_matches_score_of_all_ones():
    truth = np.zeros((50, 50), dtype=np.float32)
    truth[10:20, 25] = 1.0
    pred = np.ones((50, 50), dtype=np.float32)
    res = score(pred, truth)
    assert res.dti == pytest.approx(blanket_floor(res.truth_px, res.fp_w), rel=1e-6)


def test_scale_is_not_free():
    """DTI is NOT scale invariant: for a fixed shape, DTI(c*p) = cT/(0.2cM+0.8|G|).

    This is the algebra the emission policy rests on (``docs/research/hypotheses.md``
    H19-D): raising a floor adds mass everywhere and only pays where the kernel
    already had a maximum, so a *thin* field at high value beats the same field
    diluted by a floor.
    """
    rng = np.random.default_rng(3)
    truth = (rng.random((40, 40)) < 0.03).astype(np.float32)
    pred = rng.random((40, 40)).astype(np.float32)
    base = score(pred, truth)
    scaled = score(pred * 0.25, truth)
    c = 0.25
    expected = c * base.tp_w / (0.2 * c * (base.tp_w + base.fp_w) + 0.8 * base.truth_px + 1e-7)
    assert scaled.dti == pytest.approx(expected, rel=1e-4)
    assert scaled.dti < base.dti


def test_margins_break_even_is_alpha_over_one_plus_beta():
    m = margins(tp_w=10.0, fp_w=10.0, truth_px=20, dti=0.25)
    assert m["break_even_probability"] == pytest.approx(0.2 / 1.8)
