# Preregistration — H18-N1 paleoshoreline displacement

**Status: DRAFT / NOT LOCKED / NO RESULTS.** This document freezes the physical hypothesis and test logic before an operator is implemented. It is not a claim that the final spatial holdout has been locked: the authorized competition feature raster, official sample template, verified labels, and exact DEM coverage are absent from this checkout. No predictions have been computed and no thresholds have been tuned.

## Hypothesis

Within the GeoDAWN footprint that intersects mapped Pleistocene lake deposits, a Quaternary fault strand may produce a narrow, approximately linear discontinuity that vertically offsets or warps **at least two independently correlatable shoreline/terrace marker levels in the same sense**. This relationship-based signature should be more specific to fault displacement than a generic scarp, ridge, or shoreline edge.

**Falsifying observation:** candidate breaks occur only on one shoreline, follow the shoreline’s natural curvature, align with mapped roads/canals/channels or acquisition seams, show broad smooth tilt without a narrow break, or fail to remain spatially coherent across independent marker levels. Any of these outcomes rejects or materially narrows the mechanism.

## Inputs and information rules

1. **Detector inputs:** 1 m bare-earth DEM tiles with source metadata, derived multi-level paleoshoreline/terrace markers, and non-fault negative-control layers (roads, rails, canals, hydrography). No QFault/INGENIOUS traces, fault-distance rasters, earthquake locations, geothermal anchors, or labels may be used by the detector.
2. **Evaluation-only truth:** authorized, hash-verified competition label raster and official sample footprint. Catalog traces are used only to form held-out truth/metadata where the protocol explicitly requires them; they do not enter the prediction surface.
3. **Context source:** USGS MF-2323 paleolake GIS may define candidate basins, but its metadata describes shoreline positions generalized from 3-arc-second (~90 m) DEM contours. It is not a substitute for 1 m marker extraction.
4. **Provenance gate:** all files must have official source URL, retrieval date, SHA-256, license, CRS, dimensions, pixel size, transform, and nodata/valid-mask summary recorded. A team GitHub bridge hash alone is not independent official-source verification.
5. **Survey/DEM seam gate:** map the GeoDAWN acquisition blocks and 1 m DEM collection boundaries before making gradients or lineaments. USGS reports different Area 1/Area 2 flight specifications (200 m vs 400 m line spacing) and different aircraft in portions of the survey; do not infer that every block has a different aircraft. The 3DEP 1 m collection is not necessarily seamless between projects. Exclude or explicitly model seams as negative controls.

## Split design — pending the data needed to lock it

The final split will be **fault-system/basin-blocked**, not pixel-random. Entire mapped fault systems and shoreline marker groups will be assigned together; a buffer will prevent adjacent pieces of the same fault/shoreline from crossing folds. One spatial region will be sealed for a one-time confirmatory evaluation. No feature selection, threshold choice, or error analysis may use that sealed region.

Before any model code is written, the run must:

- identify the candidate basins and mapped systems from the verified official data;
- assign whole systems/basins to development folds and the final sealed slice using a deterministic, recorded seed;
- write the split polygons/masks and SHA-256 to a committed lock file;
- verify that no component of a held-out fault system or shoreline group leaks into development; and
- reproduce the comparator on the same split.

**This split is not yet locked.** Naming a final region without the authorized rasters would create a false claim of preregistration.

## Fixed candidate rule (to be implemented only after the split is locked)

A candidate trace is eligible only when (a) at least two independently identified shoreline/terrace markers show a same-sense discontinuity, (b) the discontinuities overlap within the registration uncertainty, and (c) the linear trace is stable under the DEM/marker uncertainty. A single scarp, a shoreline edge, a DEM gradient, or a topographic template match alone is ineligible. Registration tolerances will be derived from source metadata and measured georeferencing error—not tuned on held-out labels.

Predictions will be scored on the official 100 m grid at the official distance-weighted Tversky metric (α=0.2, β=0.8, triangular support R=300 m). Candidate emission budget must match the reproduced comparator; any operating threshold is selected only within development folds and frozen before the sealed slice is opened.

## Comparator and promotion gate

The current best **reported** result in the public 16GEMSDOE evidence is H18-3a: mean dense DTI 0.21319 and sparse-proxy DTI 0.09401, with four folds. This is not independently reproduced here and is not hidden-label evidence. H16-1’s reported comparator was 0.21272 / 0.08541. See [`registry/holdout-baseline.json`](../../registry/holdout-baseline.json) and the [source evidence](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/hypothesis_h18_validation.json).

Before any release decision, reproduce H18-3a and its exact evaluator on the locked data/split. If that cannot be done, the benchmark is unresolved and the candidate cannot pass. Once reproduced, require all of the following on a preregistered candidate run:

1. Candidate mean dense **and** sparse DTI exceed the reproduced H18-3a comparator.
2. Sparse DTI is higher in at least 3 of 4 spatial development folds; neither dense nor sparse DTI loses more than 0.01 in any fold.
3. A paired bootstrap over independent basins/fault systems (not pixels) has a positive 95% lower confidence bound for both metrics on the sealed confirmatory slice.
4. The multi-marker detector beats shoreline-only, road/canal, channel, and randomized-lineplacebo controls at the same prediction budget.
5. All results, including failures, are saved with input hashes, software version, split hash, preregistration commit, and output hashes. The sealed slice is evaluated once.
6. The output is unique on scored pixels against the public group artifact registry and passes the format validator.

A holdout pass is necessary, not proof of leaderboard gain. No public score is predicted from the proxy.

## Release status

- Training raster in this repository: **absent**.
- Verified official template/labels in this repository: **absent**.
- Exact high-resolution source coverage: **unchecked**.
- Locked spatial holdout: **no**.
- Candidate operator or holdout result: **none**.
- Submission slot spent: **no**.
