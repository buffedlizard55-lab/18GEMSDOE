# Locked holdout protocol (binding on E1–E5)

## 1. Folds

- **Leave-one-fault-system-out**: connected components of the catalogue (8-connectivity)
  grouped by fault system; 3 folds minimum.
- **300 m (3 px) train-exclusion buffer** around every test-truth pixel: no train pixel
  inside the metric kernel of test truth (else the kernel leaks).
- **Two truths reported**: (a) held-out known faults (monitor — wrong population, rewards
  clustering by construction); (b) catalogue-complementary pseudo-truth regimes:
  buried-regime (SGMC faults > 300 m from catalogue, weighted to basin fill),
  splay-regime (synthetic tip-fan corridors on HELD-IN systems only, never the test system).
- **Locked slice**: a further 1/3 of each test fold, sealed before any experiment; evaluated
  exactly once per hypothesis, at the end. An improvement counts only if it survives the
  locked slice.

## 2. Controls (every hypothesis, every fold)

1. Budget-matched random control at the exact top-k budget (exact-k partition, deterministic
   tie-break — never `>=` thresholding, which over-selects 2–10× on plateaus).
2. One mechanism-specific control that must LOSE to the hypothesis for the win to mean anything:
   - E1: amplitude-only HGM/TDR edges (depth-gating must carry the gain; kill if rank-corr > 0.9 with no DTI gain).
   - E2: mirror-angle fans (kinematically forbidden); must score ≤ random.
   - E3: unaligned knickpoint density (alignment must carry the gain).
   - E4: each arm alone (intersection must beat both — super-additivity of independent evidence).
   - E5: undated H3 steps (dating must carry the gain via FP eviction on road/shoreline masks).

## 3. Metric

Exact kernel DTI from `scripts/dti_metric.py` (self-tested: official fixture 0.60, perfect 1.0,
zero 0.0, masking verified). Report masked (known faults excluded, forum 11516) as primary;
unmasked as diagnostic. Emission: binary {0,1} top-k at budgets {1%, 2%, 2.5%, 3%} — budget
curve re-derived, never assumed.

## 4. Pre-registration (E1 — top candidate; locked 2026-09-30, before any run)

**Hypothesis**: shallow-contact Euler solution density (SI=0, clustered, depth < cover
threshold) skeletonised to 1-px traces recalls buried-regime pseudo-truth better than
amplitude-only edges at matched budget.
**Predicted direction**: E1 top-k DTI > budget-matched random AND > HGM-amplitude field on
≥2 of 3 folds in the buried regime.
**Falsification**: E1 ≤ random on ≥2 folds, OR E1 wins only where HGM wins (redundant), OR
the win vanishes when the GeoDAWN Area 1/2 seam band (1 km) is excluded, OR the win vanishes
on the locked slice.
**Artifact argument to beat**: "Euler density just re-ranks HGM amplitude" (tested by the
rank-correlation kill rule) and "solutions cluster on survey seams, not faults" (tested by
the seam-exclusion rerun).

## 5. Slot rule

A hypothesis earns a submission slot only if: pre-registered direction confirmed on open
folds → survives the locked slice → survives the investigator's best artifact argument →
validator 13-gate PASS → unique content-id note. One hypothesis per slot.
