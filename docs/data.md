# Data — the official rasters, their hashes, and where they come from

## 1. The three official files

**[VERIFIED-HERE]** Assembled and verified by `scripts/assemble_data_bridge.py` (status PASS on
2026-09-30); every hash below was recomputed in this checkout from the bytes actually on disk.

| Canonical name | Bytes | SHA-256 | Grid |
|---|---:|---|---|
| `data/training_features.tif` | 418,912,844 | `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5` | 3292 × 3730 × 19 bands, EPSG:32611, 100 m, float32, nodata `-3.4028235e38`, bounds (243350, 4135550, 572550, 4508550) |
| `data/labels.tif` | 425,830 | `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093` | 3292 × 3730, int8, `-1` = outside footprint (7,111,787 px), `0` = no fault (5,106,385 px), `1` = fault (60,988 px) |
| `data/sample_submission.tif` | 1,599,597 | `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc` | 3292 × 3730, float32, NaN outside the footprint (57.92 %) |

**Provenance chain** (each hop is checkable by hand):

1. Official data tab (login required): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
2. The public Dropbox mirrors printed there — URLs recorded verbatim in `data/bridge/manifest.json`.
3. The pinned inventory (`data/bridge/inventory.json`) measured on a GitHub-hosted runner with
   unrestricted egress, 2026-09-14; the sibling project's transport workflow aborts on any drift.
4. Committed as ≤ 90 MiB parts in the sibling repository `buffedlizard55-lab/GEMSDOE` (`data/bridge/`),
   because GitHub rejects blobs ≥ 100 MB.
5. Re-verified here part-by-part and whole-file before the canonical names were written.

**Caveat, stated plainly:** hop 3–4 was performed by a sibling project; this sandbox cannot reach
Dropbox or DrivenData. What *is* verified here is that the bytes match the pinned inventory, and that
the rasters' own metadata (19 bands with the documented names, EPSG:32611, 100 m, the stated bounds,
int8 labels with the `-1/0/1` coding) matches the official description of the data.

## 2. Band inventory (read from the file's band tags)

| # | Band tag | Category | # | Band tag | Category |
|---:|---|---|---:|---|---|
| 1 | `mag_anom` | magnetic | 11 | `iso_grav_anom_vg` | gravity |
| 2 | `rtp` | magnetic | 12 | `det_elev` | topographic |
| 3 | `tmi_hg` | magnetic | 13 | `iso_grav_anom` | gravity |
| 4 | `geod_2ndinv` | geodetic strain | 14 | `tmi` | magnetic |
| 5 | `iso_grav_anom_slope` | gravity | 15 | `depth_to_base_surf` | subsurface |
| 6 | `tc` | magnetic (tilt/curvature) | 16 | `ieq_n100a15` | seismic |
| 7 | `geod_shearrate` | geodetic strain | 17 | `cond_surf` | subsurface |
| 8 | `geod_dilaterate` | geodetic strain | 18 | `iso_grav_anom_hg` | gravity |
| 9 | `tmi_vg` | magnetic | 19 | `det_elev_slope` | topographic |
| 10 | `deq_n100a15` | seismic | | | |

**[INFERENCE]** The stack holds **no fault-catalogue band**, which matters: a model cannot leak the
labels through its inputs. Every band is a physical measurement or a derivative of one, so any fault
signal in the outputs is learned from physics, not from the answer.

## 2b. Fingerprint check: which release layers the provided stack actually contains

**[MEASURED-HERE]** `scripts/audit_checks.py` check C compares every GeoDAWN area-2 layer with every
provided band by exact statistics (count, min, max, sum, sum of squares) and, where masks differ, by
value:

| GeoDAWN release layer | in the provided 19-band stack? |
|---|---|
| `rtp`, `tmi`, `tmi_hg`, `tmi_vg` | **yes** — identical values, identical masks |
| `tc` (radiometric total count) | **yes** — values identical, shipped under the misleading tag "tilt angle or total curvature" (Audit A-03) |
| `k`, `th`, `u`, `uk`, `uth`, `thk` | **no** |
| `dem` | **no** (the shipped `det_elev` is a *detrended* elevation, not the release DEM) |
| `upcont_tmi150` | **no** |

**[INFERENCE]** The radiometric channels are therefore a real, unused, same-grid, public-domain input —
the basis of hypothesis H19-D — rather than a re-slicing of data already provided.

## 3. Auxiliary data used, and its licence

| Data | Source | Licence | Use here |
|---|---|---|---|
| GeoDAWN native-resolution grids, area 22103 (50 m area 1, 100 m area 2) | public mirror of the [USGS GeoDAWN release](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7) ([doi:10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)) distributed at `codeload.github.com/jklinck/geothermal_research` | US public domain (redistributed) | the `upcont_tmi150` deep-gradient arm; the area-2 grid is **identical** to the competition grid (verified) |
| SGMC structure (proxy catalogue) | [doi:10.3133/ds1052](https://doi.org/10.3133/ds1052) / data [doi:10.5066/F7WH2N65](https://doi.org/10.5066/F7WH2N65) | US public domain | the only available stand-in for "faults the labels lack": 61,664 px with no training label within 300 m |
| QFaults | [doi:10.5066/P9BCVRCK](https://doi.org/10.5066/P9BCVRCK) | US public domain | **not usable** as a novel-fault source — measured overlap with the labels is 99.997 % |

## 4. What is deliberately **not** committed

Raw rasters, credentials and large derived rasters stay out of Git (`.gitignore` blocks `data/`,
`*.tif`). What *is* committed: the bridge parts (the transport), the manifests, the evidence JSONs, the
provenance records and the single packaged submission in `docs/downloads/`. Regenerate everything with
`scripts/assemble_data_bridge.py`. If `data/` is ever empty again, that script plus
`scripts/prepare_data.py` is the whole recovery path.
