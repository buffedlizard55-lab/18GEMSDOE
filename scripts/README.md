# scripts/

| Script | Purpose | Needs data? |
|---|---|---|
| `dti_metric.py` | Exact distance-weighted Tversky (α=0.2, β=0.8, R=300 m) + known-fault masking, transcribed from the [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). Self-test: `python scripts/dti_metric.py --selftest` | No (self-test runs anywhere with numpy+scipy) |
| `validate_submission.py` | 13-gate format checker for any candidate `.tif` against the official sample template. Usage: `python scripts/validate_submission.py candidate.tif --template sample_submission.tif` | Yes — candidate + template (both absent here; see `../docs/data.html`) |

Environment: `conda env create -f environment.yml` (python, numpy, scipy, rasterio).
