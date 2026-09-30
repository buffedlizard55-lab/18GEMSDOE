# Audit — irregularities, duplicates, and checks that failed their own test

Classes of statement: **[VERIFIED-HERE]** recomputed in this checkout from bytes or from a primary
source fetched during this session; **[GROUP-REPORTED]** asserted by a sibling project with its
evidence file linked; **[INFERENCE]** reasoning.

Every check below is reproducible with `python scripts/audit_checks.py` (writes
`data/evidence/audit_checks.json`, including the checks whose inputs were absent — those are recorded
as **SKIPPED**, never as a pass).

## A-01 · Why the group kept scoring 0.1563 — one file, several repositories

**[VERIFIED-HERE]** `buffedlizard55-lab/GEMSDOE` and `buffedlizard55-lab/5GEMSDOE` both commit
`data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif`; the files are **byte-identical**,
SHA-256 `7f00890a62878d612fb5eef67a9a364a2df819433dde74b6762ce4fc0fc4fe15`, 570,890 bytes. The file is
a hard 0/1 mask with 172,974 positive pixels (3.35 % of the valid footprint). `5GEMSDOE` also stores
the same bytes as `data/evidence/leaderboard_anchor/gemsdoe-ens12-adopted-7f00890a.tif`.

**[GROUP-REPORTED]** The same scored content (`scored_content_sha256 6e6f23c6…`) sits at eight paths
across six repositories; `8GEMSDOE`'s entry is `max(ens12, catalogue)` and scored the same 0.1563;
`GEMSDOE2` overlaps it at Jaccard ≈ 0.95
([16GEMSDOE `submission_similarity.json`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/submission_similarity.json)).

**[INFERENCE]** So the repeated public score is, at least in part, **the same prediction uploaded from
different repositories**, not four independent ideas converging. This repository therefore refuses to
package a file whose hash is already registered (`scripts/make_submission.py`).

## A-02 · A check that failed and was abandoned: "63 % of the USGS fault database is missing from the labels"

**[VERIFIED-HERE — abandoned]** Rasterising the public QFaults shapefile gives 197,294 line pixels in
the footprint's bounding box, of which only 72,245 (36.6 %) lie within 300 m of a training label.
Read carelessly that says: *the labels omit two-thirds of the USGS fault network — a free 125,053-pixel
fault population for the submission.*

That reading is **wrong**, and the check that killed it is in `scripts/audit_checks.py` (check B):
the valid survey footprint is only **42.1 %** of the grid, and **71,984 of the 71,985 QFaults pixels
that fall inside that footprint (99.999 %) are within 300 m of a training label**. The "missing"
pixels are simply outside the survey, where nothing is scored. The correct statement, and the one used
everywhere on this site, is: *the labels are the QFaults network inside the footprint.*

*Recorded because it is the exact self-deception the brief warns about: a large, exciting number that
came from forgetting to intersect with the scored area.*

## A-03 · Provided band 6 is not what its tag says

**[VERIFIED-HERE]** Band 6 of `training_features.tif` is tagged
`tc — "Tilt angle or total curvature - magnetic field derivative for edge detection"`. Its values are
**identical** to the GeoDAWN release layer `22103_tc_a2.tif` (max absolute difference 0 over the
5,165,840 pixels valid in both), and in that release the `tc` grid belongs to the **radiometric**
family alongside `k`, `th`, `u`, `uk`, `uth`, `thk`. A sibling project reached the same conclusion
independently (Pearson = Spearman = 1.0; "band 6 IS the GeoDAWN radiometric total count (tag
description is wrong)") **[GROUP-REPORTED]**.

**[INFERENCE]** Two consequences: (1) the feature stack is the GeoDAWN release, so the release's other
layers are legitimate, same-grid, public-domain inputs — not another survey; (2) four of the nineteen
provided bands are exactly release layers `rtp`, `tmi`, `tmi_hg`, `tmi_vg`, while **`k`, `th`, `u`,
`uk`, `uth`, `thk` are absent** from the stack, which is what makes hypothesis H19-D a genuine data
gap rather than a re-slicing of the given bands.

## A-04 · Mask semantics were undocumented here until this pass

**[VERIFIED-HERE]** The staff answer is unambiguous: the known-fault mask is **pixel-exact and
identical to the provided training labels, with no buffer**, and the buffer around known faults does
not apply
([forum 11516 post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4)).

**[VERIFIED-HERE]** The previous contents of this repository never stated those semantics: a search of
the committed README for "mask" and "known fault" returns nothing about scoring behaviour, so the
operating rule (is painting the catalogue neutral, helpful, or fatal?) was left ambiguous for whoever
packaged a file. It is now written down in `gems18/metric.py` (`known_mask` is applied to both the
prediction and the truth) and in `tests/test_metric.py::test_known_mask_is_pixel_exact_and_free`.

## A-05 · What the organizers will not say (recorded, because it bounds what a proxy can prove)

**[VERIFIED-HERE]** Asked which data sources, fault types and coverage produced the new test faults,
DrivenData staff replied: *"We're not sharing details about the data sources, fault types, or coverage
behind the test faults beyond what's in the problem description."* The same post states that the
largest prize pool (Phase 2) uses a test set **updated by expert review of all Phase 1 submissions**
([forum 11527 post 7](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7)).

**[INFERENCE]** No proxy in this repository can be validated against the hidden truth. Every holdout
number here is weak evidence and is labelled as such on the page that shows it.

## A-06 · The group's proxies do not predict the board

**[GROUP-REPORTED]** Post-hoc calibration over 15 distinct scored files: SGMC-gap proxy
ρ = +0.52 (p = 0.048), SGMC-off-catalogue ρ = +0.39 (p = 0.15), known-fault proxy ρ = +0.17
(p = 0.54) ([16GEMSDOE `proxy_calibration_vs_lb.json`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/proxy_calibration_vs_lb.json)).
The file's own per-file table shows the correlation is fragile: the file with the *highest* SGMC-gap
score (0.1439) has the *lowest* public score of the five pinned entries (0.1294).

**[INFERENCE]** A proxy that explains ~27 % of rank variance is not a gate; it is a weak prior. It is
used here to compare arms, never to forecast a leaderboard number.

## A-07 · Format failure that was reported and could not be reproduced

**[GROUP-REPORTED]** "Predicted values must be in range [0, 1]" was reported after downloading a file
from a sibling site; neither sibling could reproduce it from the files they published. The plausible
causes are a wrong file being picked, values above 1 or below 0 inside the footprint, or
`NaN`/`Inf` inside it. **[MEASURED-HERE]** this repository's validator
(`scripts/validate_submission.py`, `gems18/submission.py::validate_geotiff`) refuses all four cases and
is run against the official template before any file is offered for download.

## A-08 · Provenance caveats that must travel with the numbers

1. The official rasters reach this checkout through a **git bridge** committed by a sibling project
   from the public mirror URLs printed on the competition data tab. The bytes are SHA-256-pinned and
   re-verified here (`scripts/audit_checks.py` check A: PASS against all three pins), and the
   rasters' own metadata — 19 bands, EPSG:32611, 100 m, the stated bounds, int8 labels with the
   `-1/0/1` coding — matches the official description **[MEASURED-HERE]**. The mapping from the mirror
   URLs to the DrivenData data tab was performed by that sibling and is not re-checkable from here.
2. The GeoDAWN native grids come from a public mirror of the USGS release; the area-2 grid is
   identical to the competition grid (3292 × 3730, EPSG:32611, 100 m, same bounds)
   **[MEASURED-HERE]**, consistent with the competition rasters being derived from that release.
3. USGS 3DEP 1 m lidar — which the problem description explicitly points participants to — is **not
   obtainable from this sandbox** (the host is blocked). Two sibling projects fetched it on GitHub
   runners; this repository does not use it, and hypotheses that need it are marked as such.

## A-09 · Not verified here, and therefore not claimed

* Any live leaderboard score of any 18GEMSDOE file (none has been submitted).
* That the hidden new-fault population resembles any proxy on this site.
* The internal computation of sibling projects' evidence JSONs (linked, not re-run).
* That `extradr19` on the leaderboard is this group's account.
