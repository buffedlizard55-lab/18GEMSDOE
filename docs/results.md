# Results and score history

**Evidence labels:** `OFFICIAL SNAPSHOT` means manually read from the DrivenData public leaderboard; `DIRECTLY VERIFIED` means bytes/hash were checked in this session; `GROUP-REPORTED` means a sibling repository reports a calculation we have not reproduced in 18GEMSDOE; `INFERENCE` is a reasoned interpretation.

## Current public leaderboard snapshot — 2026-09-30

The [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) was read manually. It showed:

| Rank | Participant | Public DTI | Status |
|---:|---|---:|---|
| 1 | DARD | 0.3168 | **OFFICIAL SNAPSHOT**; higher than the user’s previously reported 0.3049. |
| 22 | extradr19 | 0.1855 | **OFFICIAL SNAPSHOT**, four submissions shown. Whether this is our entrant is **unresolved** in this checkout. |
| 33 | SDCF9 | 0.1563 | Separate displayed participant. |
| 34 | smashi34 | 0.1563 | Separate displayed participant. |

This is a dated snapshot, not an automated feed. DrivenData’s Terms of Use prohibit automated site access; there is no scraper in this project. See [the score ledger](../registry/score-ledger.csv) and [A-04](audit.md#a-04).

## Why the group saw repeated 0.1563 scores

**Directly verified:** GitHub’s Contents API reports the exact same Git blob for the tracked TIFF in `GEMSDOE` and `5GEMSDOE`:

- Path in both repositories: `data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif`
- Git blob SHA-1: `812e61b74050d1350cc2bde1fab0c76ead32e0c4`
- Size: 570,890 bytes
- Sidecar `docs/submission_field.bin`: blob `6a89b64e01a7c11b8235449c538390ac3435605d`, 532,072 bytes

Review the [GEMSDOE artifact](https://github.com/buffedlizard55-lab/GEMSDOE/blob/main/data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif) and the [5GEMSDOE artifact](https://github.com/buffedlizard55-lab/5GEMSDOE/blob/main/data/evidence/runs/ens12-adopted-floor0.1-w0/submission.tif). The 16GEMSDOE public evidence registry reports that `GEMSDOE1` and `5GEMSDOE` were this byte-identical artifact with historical score 0.1563, and that `8GEMSDOE` differed only on pixels excluded by its scored-pixel definition. We did not independently recompute the latter pixel comparison or prove which upload produced each score.

**Interpretation:** identical prediction pixels would be expected to receive the same deterministic public score. The matching files explain a repeated score between those two artifacts far better than a novel model gain. They do **not** prove that every entrant showing 0.1563 submitted the same raster. In this public GitHub account, `GEMSDOE1` is not a current repository name (the repository lookup returned 404); the 16GEMSDOE registry uses it as a display label for the `GEMSDOE` repository.

## Holdout results: prior evidence, not 18GEMSDOE validation

The 16GEMSDOE site publishes a preregistered four-quadrant evaluation on known catalogue faults and a 20%-of-components sparse proxy. Its evidence JSON reports:

| Candidate | Mean dense DTI | Mean sparse-proxy DTI | Group-reported gate |
|---|---:|---:|---|
| H16-1 comparator | 0.21272 | 0.08541 | baseline |
| H18-3a endpoint/junction complexity | 0.21319 | 0.09401 | passed that project’s stated gate |
| H18-1 product-of-experts | 0.20389 | 0.08062 | failed |
| H18-3b oblique-strike prior | 0.15681 | 0.03694 | failed |
| H18-3c combined prior | 0.15014 | 0.04966 | failed |

These figures are **group-reported, not independently rerun here**, and known-fault reconstruction is only a proxy for the hidden new-fault task. The 16GEMSDOE post-hoc analysis further reports that its dense known-fault proxy did not correlate detectably with public scores across 15 unique files (Spearman ρ=0.171, p=0.5413); this does not prove all holdouts are useless, but it weakens confidence in treating that proxy as a leaderboard predictor. See [the validation JSON](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/hypothesis_h18_validation.json), [the proxy calibration JSON](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/proxy_calibration_vs_lb.json), and [the preregistration](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/research/preregistration_h18.md).

**18GEMSDOE result:** none. No official feature stack or validated holdout is in this checkout; no new score is claimed, and no new file has been submitted.
