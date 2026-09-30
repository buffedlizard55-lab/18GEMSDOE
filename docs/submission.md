# Submission steps

## Current state

**There is no validated 18GEMSDOE submission file to download.** The site’s browser builder is a format tool: it can package an existing local prediction raster only after you provide a passing holdout-evidence JSON and the official sample template. It does not generate a fault model, does not submit anything, and does not imply that a candidate can beat the hidden test. No file has been submitted from this repository.

## Correct file format

According to the [official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format), the submission must be:

- a single-band GeoTIFF (`.tif`), or a ZIP with one GeoTIFF;
- the same bounds, dimensions, transform, projected CRS **EPSG:32611**, and 100 m resolution as the official training/template raster;
- `float32`;
- finite probability/confidence values in `[0,1]` throughout the valid scored footprint; and
- null/NaN outside the footprint.

The official metric is distance-weighted Tversky (α=0.2, β=0.8; triangular support 300 m). The format check is not a performance test.

## Run the local checker

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_submission.py path/to/prediction.tif --template path/to/sample_submission.tif
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1` before running the Python commands.

Optional explicit footprint mask:

```bash
python scripts/validate_submission.py path/to/prediction.tif \
  --template path/to/sample_submission.tif \
  --footprint path/to/valid_footprint_mask.tif
```

The validator checks grid alignment, CRS, 100 m resolution, single-band `float32`, finite `[0,1]` values in-footprint, no masked cells in the footprint, and null/masked values outside it. It never rescales, clips, or silently reprojects a candidate.

## Build a unique GeoTIFF and short note

Only run this after the locked-holdout/release evidence has passed and been independently reviewed:

```bash
python scripts/package_submission.py \
  --prediction path/to/prediction.tif \
  --template path/to/sample_submission.tif \
  --evidence path/to/passing_holdout_evidence.json \
  --candidate-id H18-N1

# Add this only when the template does not encode its scored footprint:
python scripts/package_submission.py \
  --prediction path/to/prediction.tif \
  --template path/to/sample_submission.tif \
  --evidence path/to/passing_holdout_evidence.json \
  --candidate-id H18-N1 \
  --footprint path/to/valid_footprint_mask.tif
```

The package script refuses missing, unregistered, or non-passing evidence. It copies the official template grid, writes NaN outside the footprint, reopens the resulting file, validates it, and assigns a unique filename containing the candidate ID, UTC time, content hash, and random nonce. It writes a short sidecar note with the candidate/holdout ID and hash. Generated output is written under `build/` and ignored by Git.

The browser tool on the website reads local files only and packages a user-supplied prediction TIFF; it does not upload data or generate predictions. It requires a passing evidence record and accepts an optional explicit footprint mask when the template does not expose a nodata value. Browser processing holds several raster-sized buffers and can exhaust memory on large grids; after downloading its TIFF, run the Python/rasterio validator against the actual official template as an independent check. A format pass alone does **not** satisfy the holdout gate. The browser builder currently has no validated model output to offer.

## Upload on DrivenData (manual; no credentials are handled here)

1. Sign in to the account registered for the competition and open the [GEMS Prize Challenge](https://www.drivendata.org/competitions/306/competition-doe-gems/).
2. In the competition sidebar select **Submit**, then **Make new submission** (the official competition page uses those labels).
3. Choose the unique `.tif` produced by the gated builder. Do not upload the research TIFF, a previous project’s file, or a ZIP with multiple rasters.
4. Paste the generated short note into the submission comment/note field. It records the candidate ID and hash so entries remain distinguishable.
5. Review the confirmation and the resulting score manually, then record the date, submission identifier, score, and account in `registry/score-ledger.csv`. Never record a proxy DTI as a leaderboard score.
6. Do not exceed three scored submissions in a rolling seven-day window per entity. The official rules require choosing one final submission per entity for both prize rounds; see [rules §3.4–3.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf) and the [staff clarification](https://community.drivendata.org/t/weekly-submissions/11524/2).

## If the platform reports “Predicted values must be in range [0, 1]”

Do not clip or rescale blindly. First check that you selected the intended file and its SHA-256; compare against the exact official template; run the validator; inspect valid-mask/nodata behavior; and ensure every valid pixel is finite and between 0 and 1. The checker intentionally fails if a valid pixel is NaN/Inf or if an in-footprint pixel is masked. This checkout has not accessed the actual file that triggered the user’s prior error, so the root cause is not yet independently established.
