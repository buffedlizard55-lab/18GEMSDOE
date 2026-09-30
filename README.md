# 18GEMSDOE — GEMS Prize research and release hub

**GitHub Pages:** <https://buffedlizard55-lab.github.io/18GEMSDOE/>  ·  **[Submission steps](docs/submission.md)**  ·  **[Research shortlist](docs/research/hypotheses.md)**  ·  **[Evidence audit](docs/audit.md)**

> **Current release status — 2026-09-30:** no competition data, locked holdout, validated 18GEMSDOE prediction, or submission GeoTIFF is present in this checkout. **Do not submit an 18GEMSDOE file yet.** The site has a gated GeoTIFF builder and validator, but there is no model raster to package and no candidate has cleared the release gate.

## Read this first every session

Read this README and [AGENTS.md](AGENTS.md) before changing the project. Treat the repository as the source of truth for work done here; sibling-repository claims must be labeled as group-reported until independently reproduced in this checkout. Update the status, evidence ledger, and audit when facts change.

## User's initial project brief — preserved scope

Improve 18GEMSDOE through a deep, scientifically grounded review of the GEMS Prize task. Explain the repeated 0.1563 scores without assuming that equal leaderboard values mean identical submissions. Propose three to five genuinely distinct fault-mapping hypotheses, with physical mechanisms, layers and trusted sources, expected value/cost, novelty against 8GEMSDOE and 16GEMSDOE, specific non-fault alternatives, and falsifying spatial-holdout tests. Prefer extensions, splays, and parallel strands where the organizers permit them, but do not assume hidden-source methods. Lock the holdout before tuning, preregister predictions, seek falsification, and spend no weekly submission slot until a candidate beats the best reproducible blocked-holdout comparator. Keep a transparent evidence/leaderboard ledger that distinguishes group claims, independent checks, and official results. Validate a passing candidate before submission; provide a compliant, uniquely named GeoTIFF and short note, make submission instructions obvious, and put the project aims and Core Values in this README. Review the work in multiple passes, flag irregularities and limitations, and request a PR/merge only when evidence and tests support it.

This is the durable project brief reconstructed from the user's original request; scientific, data, and competition claims below must still be independently sourced and verified.

## Project charter and acceptance criteria

The purpose is to improve our GEMS Prize fault predictions using **reproducible geology, not leaderboard folklore**. The objective is to maximize the chance of winning while contributing credible new fault interpretations—not to optimize a proxy, copy a prior output, or claim a result that has not been measured.

For each proposed detector, record: the physical mechanism; the layers and official source; why it could identify unmapped fault geometry; how it differs from every public group register; at least one specific non-fault process that could create the same pattern; a test that distinguishes the two; source licensing/access; cost; and a pre-registered spatial holdout. Rank expected value and cost qualitatively unless there is defensible evidence for a numeric estimate. Call a candidate “new” only after checking the public 8GEMSDOE and 16GEMSDOE registers; distinguish *proposed*, *tested*, *failed*, *passed a proxy*, and *officially scored*.

**No submission slot is spent** until the candidate:

1. is preregistered before model/threshold tuning;
2. is evaluated on a genuinely spatially blocked, locked holdout with all inputs and split hashes recorded;
3. beats the best reproducible holdout comparator on the dense and sparse proxy metrics, passes the registered fold/negative-control gate, and is not just a different rendering of an existing artifact;
4. has a unique-content check against the group’s prior predictions; and
5. passes the official GeoTIFF grid/range validator.

A proxy score is **not** a public leaderboard score and does not establish skill on the hidden new-fault labels. The official organizers do not disclose the hidden labels’ source methods. Preserve failures and limitations; do not tune on the sealed holdout. Use independent physical evidence as corroboration, not as an unexplained feature stack.

### Core values

- **Maximize P(Win):** preserve the limited submission budget for distinct, gated predictions; use an A/B only when it tests a preregistered decision; do not submit a duplicate or a candidate that fails the holdout.
- **Own the Outcome:** rerun before trusting, record the exact inputs and hashes, report failed tests, flag irregularities, and do not hide uncertainty or attribution conflicts.

## What is known now (and what is not)

| Evidence | Current finding | Evidence class |
|---|---|---|
| Official live leaderboard (manual snapshot, 2026-09-30) | Leader **DARD: 0.3168** (rank 1). `extradr19` is listed at **0.1855** (rank 22, four submissions); this checkout has not verified that account belongs to our entrant. | Official platform snapshot; account attribution unresolved. [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| Repeated historical 0.1563 | The tracked `ens12-adopted-floor0.1-w0/submission.tif` in public `GEMSDOE` and `5GEMSDOE` has the same Git blob SHA (`812e61b74050d1350cc2bde1fab0c76ead32e0c4`) and size (570,890 bytes); their `submission_field.bin` files also match exactly. This is strong evidence of a duplicate artifact, not proof of the upload-to-score mapping. No public repository named `GEMSDOE1` was found; the 16GEMSDOE registry uses that display name for the `GEMSDOE` repository. See [the audit](docs/audit.md#a-02). | Independently checked public GitHub blob identity; historical score mapping is group-reported. |
| 16GEMSDOE holdout | Its public evidence reports H18-3a at dense DTI **0.21319** and sparse DTI **0.09401**, slightly above its H16-1 comparator (0.21272 / 0.08541). It is a four-quadrant known-label / sparse-proxy result, **not hidden-test validation** and not independently reproduced in this repo. | Group-reported; use as a provisional benchmark only. [Evidence JSON](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/hypothesis_h18_validation.json) |
| 18GEMSDOE code and data | This repository began with only this README. The official training stack, sample template, source labels, holdout, model, and output are not in the checkout. A public mirror manifest has been hash-checked for one small label raster in a prior session, but its official provenance and raster semantics were not independently verified. | Direct workspace inspection plus provenance caveat. See [data status](docs/data.md). |
| Next research direction | Three physically distinct candidates are documented in [the shortlist](docs/research/hypotheses.md). The leading idea—fault displacement of multiple paleolake shoreline markers—has **not** been tested. Its exact DEM coverage and holdout are not yet verified, so it is not release-ready. | Hypothesis, not result. |

The latest public leaderboard snapshot differs from the 16GEMSDOE README’s historical “best public 0.1563” statement. If `extradr19` is our entry, update the group ledger from the signed-in competition account and reconcile submission IDs before making any claim. See [A-04](docs/audit.md#a-04).

## Competition constraints that shape the workflow

- The task is to predict fault probability for the GeoDAWN study region. The official format is one-band `float32`, EPSG:32611, 100 m, matching the training raster’s dimensions/transform/bounds; valid-footprint values must be in `[0,1]`, with null/NaN outside. The official metric is distance-weighted Tversky with α=0.2, β=0.8, and a 300 m triangular distance support. [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- Organizer staff confirm “new” pixels may be extensions, splays, or parallel strands of a known fault system. They will not disclose additional hidden-label sources or fault types. [Definition](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2) · [test-source response](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7).
- The official rules allow up to three scored submissions per rolling week (DrivenData staff clarified the rolling window) and require one final submission per entity across both rounds. The competition page lists an end date of **2026-12-03 23:59 UTC**. [Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · [staff clarification](https://community.drivendata.org/t/weekly-submissions/11524/2) · [competition page](https://www.drivendata.org/competitions/306/competition-doe-gems/).
- DrivenData’s Terms of Use prohibit robots, spiders, or other automatic devices from accessing the site. **This project does not scrape or poll its leaderboard.** The site links to the official live board and stores dated manual snapshots only. Seek written permission before adding any automated DrivenData access. [Terms](https://www.drivendata.org/termsofuse/).

## Submission workflow

The executive instructions are on [Submission steps](docs/submission.md). The core checks are automated locally:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_submission.py path/to/prediction.tif --template path/to/sample_submission.tif
```

After—and only after—a candidate’s release evidence passes the locked-holdout gate, the packager can create a uniquely named GeoTIFF and a short note:

```bash
python scripts/package_submission.py \
  --prediction path/to/prediction.tif \
  --template path/to/sample_submission.tif \
  --evidence path/to/passing_holdout_evidence.json \
  --candidate-id H18-N1
```

The web builder performs local grid/value checks and a GeoTIFF round trip without uploading files; it also refuses a release record that has not passed the evidence gate. After downloading its output, run the Python/rasterio validator against the actual official template as an independent format check. Neither builder can create a geological prediction from nothing. **No passing evidence file or candidate prediction currently exists**, so no ready-to-upload TIFF is offered.

## Reproducibility and data policy

- Never commit DrivenData credentials, private labels, or large raw data. Keep local competition files outside Git and record their SHA-256, source, license, CRS, transform, dimensions, and nodata/mask behavior in a provenance manifest.
- The public DOE GDR listing for INGENIOUS is freely accessible and CC BY 4.0; the specific ZIP bytes still need to be downloaded and checked in a reproducible run before a candidate relies on them. The official USGS 3DEP one-meter DEM collection is public domain but not necessarily seamless across acquisition projects. Exact coverage in the competition footprint is not yet checked.
- Do not treat the public GitHub bridge manifest as an official source. A matching hash proves byte identity with that manifest—not independently with DrivenData, and not label meaning.
- The only holdout values currently available in this repo are references to group-published evidence. The holdout design for 18GEMSDOE remains **not locked** until the authorized input files and their provenance are in hand. No candidate has been tuned or validated here.

## Local development and tests

Python tools use `rasterio`/NumPy; the static browser packager uses the pinned `geotiff.js` dependency. Raw competition data are never needed for synthetic unit tests.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q

npm ci
npm run build
npm test
```

The browser builder bundle is committed under `assets/js/` so GitHub Pages serves a ready static site. Rebuild it with `npm run build` after editing `web/submission-builder.js`. The Python validator/packager can be run using the commands in [submission steps](docs/submission.md).

## Review checklist

Before publishing any claim or artifact, review it in at least three passes:

1. **Science:** mechanism, resolution, non-fault alternatives, controls, and relevant primary paper verified.
2. **Evidence/compliance:** direct official links; clear distinction between official snapshot, independent measurement, group report, and inference; data license/provenance; no prohibited automation.
3. **Engineering/submission:** tests pass; grid, nodata, mask, dtype, range, unique name, note, evidence gate, and generated-file round trip pass; status and audit updated.

If a required source, training file, holdout, or account attribution cannot be verified, mark the work **blocked** rather than filling the gap with an assumption.
