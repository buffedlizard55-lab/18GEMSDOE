# Executive summary — the file, and exactly how to submit it

## The file

**`docs/downloads/`** holds the ready-to-upload prediction. Click the `.tif`, save it, upload it.
Nothing is generated in your browser and nothing is uploaded anywhere by this site — the file is a
static artefact whose bytes are pinned by SHA-256 below, and it has already passed the format check
against the official template.

<!-- DOWNLOAD_BLOCK -->

## What it contains, in one paragraph

A **H19-A conjunction field**: every emitted pixel is a place where at least two *physically
independent* evidence families — magnetic horizontal gradient / tilt derivative, isostatic-gravity
horizontal gradient, and topographic curvature of the detrended elevation — have a lineament ridge,
thinned to one pixel, at uniform value 1, plus the known USGS/INGENIOUS catalogue traces (which the
platform masks out of scoring, so including them is free). The physics: a fault plane juxtaposes rock
of different density and magnetic susceptibility, so potential-field gradients peak over the trace of
the plane, and a surface-breaking fault also breaks the slope. The non-fault look-alikes — lithologic
contacts, volcanic flow boundaries, playa and alluvial-fan edges, roads and canals, survey-block seams
and the data-footprint boundary — are the reason the arm requires agreement between independent
families rather than any single edge, and why a matched random-lineament control is reported beside it.
Read [Validation](validation.html) before you believe any of it. The honest headline: the conjunction
beats its matched random-lineament control on the tuning folds (0.1229 vs 0.0930 at 250,000 px), is
only marginally ahead of that control at the shipped file's own mass (0.0926 vs 0.0882), and the arm
the tuning folds promote **loses** on the sealed slice (0.0003 vs 0.0085). This file is a candidate,
not a validated winner.

## Format requirements (verified against the official problem description)

| Requirement | Official wording |
|---|---|
| Projected CRS | "same projected coordinate reference system as the training data … UTM zone 11N, EPSG 32611" |
| Resolution | "same resolution as the training data (100 m)" |
| Extent | "same bounds as the training data, and data outside the bounds is null or nan" |
| Bands and dtype | "a single layer with datatype of 32-bit float (`float32`)" |
| Values | "values between 0 and 1 indicating the confidence or probability of fault presence" |

Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format>
(fetched 2026-09-30). A ZIP containing a single GeoTIFF is also accepted: "You can submit a
single-band GeoTIFF (.tif) file, or a .zip file containing a single GeoTIFF."

## Submit — step by step

1. **Download** the `.tif` at the top of this page and keep the file name as it is (it carries the
   candidate id, the UTC time and the content hash so that two entries can never be confused).
2. **Sign in** to the account registered for the competition and open
   [the GEMS Prize Challenge](https://www.drivendata.org/competitions/306/competition-doe-gems/).
3. Open **Submit → Make new submission**.
4. **Choose the file** you downloaded. Do not pick a research raster, a previous project's file, or a
   ZIP containing more than one GeoTIFF.
5. **Paste the note** from the file's sidecar (`docs/downloads/*.note.txt`) into the comment field —
   it records the candidate id, the holdout id and the SHA-256.
6. **Upload.** If you see *"Predicted values must be in range [0, 1]"*, work through the triage below
   rather than clipping the file.
7. **Record the score**: date, submission id, score, account → `registry/score-ledger.csv`. A proxy
   DTI is never recorded as a leaderboard score.

**Budget:** rules §3.4 allows *up to three scored submissions per week per entity*, and each entity
must then choose **one** final submission for both prize rounds ([rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf),
p. 10). Spend them on distinct, informative files — not on the same field from several repositories.

## Format check before you upload (30 seconds, no data needed)

```bash
python scripts/validate_submission.py docs/downloads/<file>.tif \
  --template data/sample_submission.tif
```

The checker verifies grid, CRS, resolution, single band, `float32`, finite values in [0, 1] inside the
footprint and NaN outside it. It never rescales, clips or reprojects: if it fails, the file is wrong,
not the checker.

## If the platform reports "Predicted values must be in range [0, 1]"

That message is about the bytes, and the bytes are checkable:

1. **Confirm which file you selected.** A research TIFF (probability maps before packaging, a
   multi-band stack, a mask) is the most common cause.
2. **Check the range inside the footprint only** — a file can be NaN outside and still hold values
   above 1, or `Inf`, inside.
3. **Check for `NaN`/`Inf` inside the valid footprint.** The competition expects finite values there;
   `NaN` belongs *outside* the bounds.
4. **Re-run the validator above** and compare the reported SHA-256 with the one on this page.
5. **Re-download** rather than editing the file by hand — clipping changes the metric's behaviour and
   invalidates the recorded hash.

## What this file is **not**

It is not a leaderboard result and no score is claimed for it. It is one candidate, built on the
official layers only, with its controls and its sealed-slice outcome published beside it — because a
file that has not survived the locked slice is not allowed to claim a submission slot on this site.
