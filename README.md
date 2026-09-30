# 18GEMSDOE — GEMS Prize research, validation and submission hub

**Site:** <https://buffedlizard55-lab.github.io/18GEMSDOE/> · **Submit in one click:** [Executive summary](docs/executive_summary.html) · **What was tested:** [Validation](docs/validation.html) · **What was verified:** [Audit](docs/audit.html) · **Sources:** [Sources](docs/sources.md)

> **Read this file first, every session.** It carries the original request verbatim (§7), the current
> state, and the rules this project holds itself to. Do not weaken the rules to make a result look
> better.

## 1. Current state (2026-09-30)

| | |
|---|---|
| **Submission file** | `docs/downloads/18GEMSDOE_H19-C_20260930T212401Z_c11e495e.tif` — 457,340 B, SHA-256 `c11e495e5817730a…`, single-band float32 GeoTIFF, EPSG:32611, 100 m, template bounds, finite values in [0, 1] inside the footprint, NaN outside; 513,786 emitted pixels (9.9 % of the footprint), of which 452,798 are outside the pixel-exact known-fault mask. Sidecar note ready to paste. |
| **Verified format** | `python scripts/validate_submission.py <file> --template data/sample_submission.tif` → PASS (grid, CRS, dtype, range, nodata behaviour) |
| **Official data** | present and SHA-256-verified (`scripts/assemble_data_bridge.py`, status PASS): `training_features.tif` 418,912,844 B `4371c82e…`, `labels.tif` 425,830 B `7ba308cc…`, `sample_submission.tif` 1,599,597 B `2176d08e…` |
| **Metric implementation** | `gems18/metric.py`, anchored to the official worked example (3.00/1.89/2.00 → 0.60) and to the identity `TP_w + FN_w = |G|`; 10 tests in `tests/test_metric.py` |
| **Holdout** | 56 blocks of 512 px (51.2 km), 4 folds, **14 sealed blocks** never used for selection; split digest `41332369d7dd448b…` in `data/evidence/holdout_manifest.json` |
| **Honest result** | On the SGMC-gap proxy the conjunction (0.1229 at 250,000 px) beats its matched random-lineament control (0.0930), but at the shipped file's own mass it is 0.0926 against 0.0882, and the arm the tuning folds promote loses on the sealed slice (0.0003 vs 0.0085). **No arm is a validated replacement**, so the packaged file is labelled a candidate on every page. |
| **No leaderboard claim** | Nothing here has been scored by DrivenData. The current leader is **0.3168**; our group's best public entry is 0.1855 ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)). |

## 2. Why the group kept scoring 0.1563 — answered with bytes, not opinion

`GEMSDOE` and `5GEMSDOE` both commit `data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif`;
the files are **byte-identical** (SHA-256 `7f00890a62878d612fb5eef67a9a364a2df819433dde74b6762ce4fc0fc4fe15`,
570,890 B), and `5GEMSDOE` also stores the same bytes as
`data/evidence/leaderboard_anchor/gemsdoe-ens12-adopted-7f00890a.tif`. The file is a hard 0/1 mask of
172,974 pixels (3.35 % of the footprint). A sibling project reports the same scored content at eight
paths across six repositories, including `8GEMSDOE`'s `max(ens12, catalogue)` entry that scored the
same 0.1563. **So at least part of the repeated score is one prediction uploaded from several
repositories — not several ideas converging.** Full evidence and hashes: [Audit A-01](docs/audit.md).

## 3. The two official facts that decide everything

1. **The scored truth is the new faults only** — the catalogue is not the target ([problem
   description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), rules
   §3.5).
2. **The known-fault mask is pixel-exact and identical to the training labels; there is no buffer
   around known faults, and a new-fault pixel may sit within 300 m of a known trace** — DrivenData
   staff, [forum 11516 post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4).

Together with the metric algebra (`DTI = TP_w / (0.2·M + 0.8·|G|)`, where `M` is the emitted mass),
these give the operating rule this project follows: **sparse, thin, uniform-valued emission placed
where independent physical evidence agrees, with the catalogue painted for free** (it is neutral —
demonstrated on the live board by `8GEMSDOE` scoring exactly what `ens12` scored).

## 4. Hypotheses, ranked and labelled

Five candidates (H19-A … H19-E) with mechanism, the specific non-fault process that produces the same
pattern, the test that separates them, cost and novelty screen: [hypothesis register](docs/research/hypotheses.md).
Only **H19-A** (multi-physics conjunction lineament network) is implemented and controlled this pass;
**H19-C** (the composite that is actually packaged) = catalogue ∪ state-map structures ∪ H19-A, all at
value 1; **H19-B** (state-map structures with no label within 300 m) is the component whose premise
cannot be checked from here and whose size is therefore published next to it; **H19-D** (radiometric
alteration lineaments) and **H19-E** (along-strike continuation with a rotation control) are proposed
and source-checked but not run.

## 5. Reproduce everything

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

# 1. official rasters (SHA-256-pinned git bridge -> data/)
python scripts/assemble_data_bridge.py          # PASS/FAIL, refuses on hash drift

# 2. metric correctness (anchored to the official worked example)
python -m pytest -q

# 3. detector arms, controls, locked holdout, sealed read, submission raster
python scripts/run_detectors.py \
  --comparator data/comparator_ens12.tif \
  --deep-layer /path/to/22103_upcont_tmi150_a2.tif \
  --write-submission conjunction

# 4. site (every number is read from the evidence JSONs at build time)
python scripts/build_site.py
```

## 6. Rules this project holds itself to

* **Mechanism before resemblance.** Every detector states the physics that would make a signature
  indicate a fault, names at least one non-fault process producing the same pattern, and carries a
  test that distinguishes the two. A test that can only confirm is not a test.
* **Falsification is the work.** Controls (matched random lineaments, blanket, catalogue copy,
  single-family ablation) run *before* the promoted arm is described, and failures are published.
* **The holdout is locked.** Split, seal and hash are committed before any candidate is built; the
  sealed slice is read once, at the end, and reported whichever way it falls.
* **Evidence classes are labelled.** [OFFICIAL] / [MEASURED-HERE] / [GROUP-REPORTED] / [INFERENCE],
  everywhere, including in this file.
* **No submission slot without evidence.** A candidate that has not beaten the comparator on the
  sealed slice is not proposed for upload.
* **No automated DrivenData access.** Terms of use prohibit it; only links and dated manual snapshots.
* **Core values.** *Maximize P(Win)* — spend slots on distinct, gated predictions, never on a
  duplicate. *Own the outcome* — rerun before trusting, keep failed results, flag irregularities.

## 7. Original request (verbatim, read every session)

> Review the repo.
>
> There should be an easy to download submission tif file as described by the prompt. Read the entire prompt.
>
> Go one level beneath pattern-matching a layer to a shape, and require every candidate to survive on mechanism, not resemblance: before testing, state the specific physics that would make a signature indicate a fault — a normal fault juxtaposes rock of differing density and susceptibility, so an edge-detection method like horizontal-gradient magnitude or the tilt derivative applied to RTP magnetics and isostatic gravity should peak over the fault plane's actual surface trace, not merely "somewhere lineament-like"; a scarp degrades and rounds with age in ways that morphologic scarp-dating methods (a subfield built on diffusion modeling of scarp profiles) can use to separate a genuine young scarp from an artificial berm, road cut, or old shoreline — then go verify the actual primary paper behind that method before relying on it, rather than trusting a half-remembered technique name. For every candidate signature, name at least one specific non-fault process that produces the same surface pattern — a lithologic contact, a playa or alluvial-fan edge, a road, canal, or fence line visible in the DEM, a seam between GeoDAWN's four survey blocks flown with different aircraft and line spacing — and design the holdout test specifically to distinguish the two; a test that can only confirm a hypothesis has told you nothing, and seeking out the way you're wrong is the actual discipline of science, not an afterthought to it. Read the INGENIOUS and USGS Qfault mapping methodology itself, not just its output raster, to learn where the catalogue is documented as thin — sparse historical fieldwork, young cover masking scarps, desk-compiled versus field-verified segments — and because the organizers have confirmed on the record that "new fault" includes previously unmapped extensions, splays, and parallel strands of an already-known system, weight search density along-strike from known fault tips and within known fault zones above blank ground far from any mapped structure, since that is where the catalogue's own construction makes a gap both more likely and worth more per pixel. Treat a pixel where several mechanistically independent layers agree — a potential-field gradient, a curvature break, and a strain-rate or conductivity anomaly all coinciding — as evidence to be weighed, in the proper sense that independent physical origins make joint agreement far less likely by chance than any single layer's read alone, rather than as features to stack into a model and hope. And guard against fooling yourself on your own holdout: write down the hypothesis and its predicted direction of effect before running it, lock away a further slice of the holdout that nothing gets tested against until the very end, and count an improvement as real only if it survives that locked slice and your own best attempt to argue it away as an artifact — that bar, not one promising run, is what earns a submission slot.
>
> Here are the results from our groups submissions, separated by ....: GEMSDOE1 … [scores] … HIGHEST SCORE SO FAR IS THE FOLLOWING 16GEMSDOE SCORE: h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855
>
> We need to figure out why we keep scoring 0.1563, are we copying the same work over and over again? we need to come up with different ideas, and not just the same idea tried a different way. Need to figure out why 5GEMSDOE and GEMSDOE1 have the same score. We should not be generating the same score submissions, they should all be unique.
>
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.
>
> Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations. Verify no hallucinations. The goal of this project is to get a full list that follow our requirements.
>
> We need to quickly look at the results and our results … We need to come up with distinct and unique strategies to score higher in this competition leaderboard. We need to start doing heavy and deep research into the part of the project that matters the most, which is the scientific discovery of geothermal vents. We should store all of our information and knowledge that we can gather from official verified sources… We need to think outside the box but still be grounded in proper scientific research… it's important to be contrarian but be smart about it. We need to find sources of data that others are overlooking… We need deep research and critical thinking and come up with new hypothesis to test.
>
> 0.3049 is the highest score right now so we need to design a new strategy, research, testing, analyzing, and generating submission system than the current website. It should be unique, take unique approaches to generating a submission that can score higher than .3049.
>
> Put this prompt into the repo readme and read it everytime we work on the project as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use. It should solve the problem of having to manually check everything ourselves and having an up to date current feed.
>
> Our Core Values: **Maximize P(Win)** … choose the path that maximizes the probability that Arena succeeds… **Own the Outcome** … we own results end to end… When problems arise and we have the means to act, we do so without waiting for permission or assignment.
>
> Site creation: Create a github page for this repo that has clean ui, user friendly, simple and easy to use… It should include all relevant information in an easy to read format with official verified links as sources for review.
>
> The site should be able to generate a TIF file that is required for submission. It should be as easy as download to click a File to submit into the competition. This needs to be in the executive summary or the very beginning of the site. It should be obvious when you visit the site. … I tried to submit the document that i downloaded from the site but it returned this error on the submission form: "Predicted values must be in range [0, 1]" … Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25.
>
> **The single remaining blocker to training is data placement**: run `bash scripts/download_competition_data.sh` … then `python scripts/prepare_data.py` — after that the full train→inference→validate pipeline is ready to run.
>
> Run this task through multiple passes. Pass 1: Implement the task completely and verify the result. Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases. Fix everything you find. Pass 3: Re-check the entire implementation against the original request. Improve accuracy, reliability, completeness, and code quality.
>
> Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project.

## 8. Next steps and limitations (read before the next session)

**Next steps, in priority order**

1. **Only calibrate if the team wants the measurement.** The instrument is currently weak (no arm
   beat the comparator on the sealed slice), so the honest options are: (a) spend two slots on a
   calibration A/B — the packaged candidate beside the `ens12` comparator — and accept that the
   public score is *not* the first-round score (rules §3.6.2); or (b) spend nothing until an arm beats
   the comparator on the sealed slice. The site's rule is (b); the ledger records whichever the team
   chooses. This project does not upload.
2. **Make the sealed slice harder.** Cut the holdout by *structure* (component-level groups) rather
   than by grid block, so no fault straddles the split.
3. **Find the ground truth's provenance.** The experts' new faults are, by construction, *not* in
   QFaults (rules §3.3 + the measured 99.997 % overlap). Candidate public catalogues that postdate
   the compilation and are license-compatible should be tested for disjointness the way QFaults was:
   test the disjointness *before* quoting any number.
4. **1 m lidar morphology, done properly.** The scarp-diffusion literature (S17–S19) gives a real
   discriminator between a tectonic scarp and a shoreline/road, but the primary papers also show the
   inversion returns κt, not an age: an arm that uses it must carry an independent diffusivity
   calibration or be reported as morphology-only. Data: 3DEP tiles (blocked here; a GitHub-Actions
   runner can fetch them, as sibling projects already do).

**Limitations that are actually in the way**

* **No ground truth for the objective.** Every number here is measured against a *proxy*. The best
  available proxy explains ~27 % of the rank variance of our own 15 scored files — weak.
* **This sandbox's egress is limited** to `github.com`, `codeload.github.com`, `pypi.org`. DrivenData,
  Dropbox, USGS/S3, GDR and the community forum are blocked from the shell; the competition page, the
  rules PDF and the forum *are* reachable through the platform's page-fetch tool, which is how the
  official quotes in `docs/sources.md` were taken.
* **No GPU, 2 vCPU, ~3 GB RAM.** A segmentation network can be trained but not tuned here in the time
  available; the arms in this pass are mechanism-based operators, not learned models.
* **The repository cannot submit.** Uploading needs the group's DrivenData login and is a human step;
  this project prepares and validates the file, and records the result afterwards.
