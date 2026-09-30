# Sources — every claim on this site, with the official link

Read each row as: *the claim*, *where it was read from*, *what the source actually says*.
Anything not listed here should be treated as unverified. Fetched 2026-09-30.

## Competition and scoring

| # | Claim | Source | What the source says (verbatim where quoted) |
|---|---|---|---|
| <a id="s1"></a> S1 | The test set is **new faults only** | [Problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | "we have consulted with fault experts who have manually identified faults that are not contained within the current public USGS database. These new faults will comprise the test dataset for the initial prize round" |
| <a id="s2"></a> S2 | Metric definition, α=0.2, β=0.8, R=300 m, worked example = 0.60 | [Problem description § Performance metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | triangular kernel `k(d)=max(1-d/R,0)`; `TP_w`, `FP_w`, `FN_w` as published; `DTI = TP_w/(TP_w+αFP_w+βFN_w+ε)` |
| <a id="s3"></a> S3 | Submission format | [Problem description § Submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | single-layer float32 GeoTIFF, EPSG:32611, 100 m, same bounds, values in [0, 1], NaN outside |
| <a id="s4"></a> S4 | Known-fault mask is **pixel-exact**, no buffer | [Forum 11516 post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4) (DrivenData staff) | "The mask is indeed pixel-exact - it is identical to the provided set of training fault labels." … "the buffer does not apply to known faults" … "A new-fault ground truth pixel can indeed lie within 300m of a known fault trace." |
| <a id="s5"></a> S5 | "New fault" includes extensions, splays, parallel strands | [Forum 11536 post 2](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2) (DrivenData staff) | "any fault pixel not already captured by USGS/INGENIOUS" and "can include newly mapped geometry of an existing fault system" |
| <a id="s6"></a> S6 | Three scored submissions per week; one final submission | [Official rules §3.4, §3.5](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | "up to three per week" … "Each participating entity … is allowed to have one final submission" |
| <a id="s7"></a> S7 | Labels come from INGENIOUS | [Official rules §3.3](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | "These labels were obtained from the INGENIOUS project's Great Basin Regional Dataset Compilation" (fn 4: Ayling et al. 2022, [doi:10.15121/1881483](https://doi.org/10.15121/1881483)) |
| <a id="s7b"></a> S7b | **The organizers will not disclose how the test faults were made**; the Phase-2 test set is updated by expert review of all Phase-1 submissions | [Forum 11527 post 7](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7) (DrivenData staff) | "We're not sharing details about the data sources, fault types, or coverage behind the test faults beyond what's in the problem description." / "the largest prize pool (Phase 2) will use a test set that is updated by expert review of all Phase 1 submissions" |
| <a id="s8"></a> S8 | Public score ≠ the score that wins the first round | [Official rules §3.6.1–3.6.2](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | "The competitor's score on the private test dataset will be used for the first prize round" … "you must make your decision without knowledge of your scores on the private test set" |
| <a id="s9"></a> S9 | Live leaderboard state | [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) | 2026-09-30 snapshot: #1 DARD 0.3168, #2 alexoktaba 0.3042, #3 joeyfezster 0.2919; `extradr19` 0.1855 at #22 |
| <a id="s10"></a> S10 | Allowed external data | [Problem description § External datasets](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | "Participants are allowed to use any additional data sources, provided that the participants possess a license that permits the data to be used in this challenge" |

## Data

| # | Dataset | Official source | Licence | Used here |
|---|---|---|---|---|
| <a id="s11"></a> S11 | GeoDAWN airborne magnetic & radiometric surveys | [ScienceBase 657e1d85…](https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7), [doi:10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ), [USGS overview](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | US public domain | yes — via a pinned public mirror (see S14) |
| <a id="s12"></a> S12 | USGS State Geologic Map Compilation (SGMC) — the proxy catalogue | [doi:10.3133/ds1052](https://doi.org/10.3133/ds1052), data [doi:10.5066/F7WH2N65](https://doi.org/10.5066/F7WH2N65), service `SB_5888bf4fe4b05ccb964bab9d_USGS_SGMC_feature` | US public domain | yes (raster staged) |
| <a id="s13"></a> S13 | INGENIOUS Great Basin Regional Dataset Compilation | [GDR submissions/1391](https://gdr.openei.org/submissions/1391), [doi:10.15121/1881483](https://doi.org/10.15121/1881483) | CC BY 4.0 | as the label source only |
| <a id="s14"></a> S14 | Native-resolution GeoDAWN grids (mirror) | `codeload.github.com/jklinck/geothermal_research` (public repository distributing the USGS rasters) | redistributed US public domain | yes — area 22103 `upcont_tmi150` for the deep-gradient arm; area 2 grid verified identical to the competition grid |
| <a id="s15"></a> S15 | USGS 3DEP 1 m DEM (from the competition's `1m_DEM_links.csv`) | [3DEP](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services), [National Map downloader](https://apps.nationalmap.gov/downloader/), [AWS Open Data](https://registry.opendata.aws/usgs-lidar/) | US public domain, no use restrictions | **not obtainable from this sandbox** (S3 host blocked) — flagged as a limitation, not used |
| <a id="s16"></a> S16 | USGS Quaternary Fault and Fold Database (QFaults) | [doi:10.5066/P9BCVRCK](https://doi.org/10.5066/P9BCVRCK), [ArcGIS service](https://earthquake.usgs.gov/arcgis/rest/services/haz/Qfaults/MapServer) | US public domain | measured to be ≈ the training labels, therefore **not** a source of novel faults |

## Method literature (for the physics, not for the scores)

| # | Reference | Used for |
|---|---|---|
| <a id="s17"></a> S17 | Hanks, Bucknam, Lajoie & Wallace (1984), *Modification of wave-cut and faulting-controlled landforms*, JGR 89, 5771–5790, [doi:10.1029/JB089iB07p05771](https://doi.org/10.1029/JB089iB07p05771) | scarp morphology degrades by diffusion — a scarp is a *young* step, a shoreline is not |
| <a id="s18"></a> S18 | Andrews & Hanks (1985), *Scarp degraded by linear diffusion*, JGR 90, 10193–10208, [doi:10.1029/JB090iB12p10193](https://doi.org/10.1029/JB090iB12p10193) | inversion returns κt, not an age, without an independent diffusivity calibration |
| <a id="s19"></a> S19 | Hilley, DeLong, Prentice, Blisniuk & Arrowsmith (2010), *Morphologic dating of fault scarps using airborne laser swath mapping*, JGR 115, B04404, [doi:10.1029/2009JB006668](https://doi.org/10.1029/2009JB006668) | curvature-template scarp detection with signal-to-noise — and its rate of false positives on non-tectonic steps |
| <a id="s20"></a> S20 | Hermant, Kiersnowski & Bellanger (2025), *Using Deep Learning to Map Quaternary Faults in Western USA*, Stanford SGW, [PDF](https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf) | the closest published study on this exact task: topography inputs, 128×128 tiles at 10 m, no empty tiles, catalogue offsets up to 400 m |
| <a id="s21"></a> S21 | Mattéo et al. (2021), *Automatic fault mapping … with deep learning*, JGR Solid Earth 126, [doi:10.1029/2020JB021269](https://doi.org/10.1029/2020JB021269) | recommended on the competition About page; cited, not used |
| <a id="s22"></a> S22 | Horton, San Juan & Stoeser (2017), [SGMC report](https://pubs.usgs.gov/ds/1052/ds1052.pdf) | what the proxy catalogue's features mean (structure layer attribute dictionary) |
| <a id="s22b"></a> S22b | Glen & Earney (2024), *GeoDAWN: airborne magnetic and radiometric surveys of the northwestern Great Basin*, USGS data release, [doi:10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ) | the K/Th/U/ratio grids that are **not** in the provided stack (H19-D), and the grids that *are* (`rtp`, `tmi`, `tmi_hg`, `tmi_vg`, and `tc` under a misleading tag) |
| <a id="s22c"></a> S22c | Faulds & Hinz (2015), *Favorable tectonic and structural settings of geothermal systems in the Great Basin*, [OSTI 1724082](https://www.osti.gov/servlets/purl/1724082) | step-overs and fault terminations host a large share of Great Basin geothermal systems (mechanism behind H19-E) |
| <a id="s22d"></a> S22d | Siler, Zhang, Spycher et al. (2019), [USGS pub 70202167](https://pubs.usgs.gov/publication/70202167) | fault intersections and terminations control upflow — the structural reason to weight search density near tips |

## Group material (reported, not re-run here)

| # | Source | Used for |
|---|---|---|
| <a id="s23"></a> S23 | [`16GEMSDOE/evidence/submission_similarity.json`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/submission_similarity.json) | the 21 registered files, byte-identity of the repeated 0.1563 entry |
| <a id="s24"></a> S24 | [`16GEMSDOE/evidence/proxy_calibration_vs_lb.json`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/proxy_calibration_vs_lb.json) | ρ = +0.52 (SGMC-gap) vs +0.17 (known-fault) against public score, n = 15 |
| <a id="s25"></a> S25 | [`16GEMSDOE/evidence/lb_signal_attribution.json`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/lb_signal_attribution.json) | the feature-enrichment prior (magnetic worms positive, basin-margin gradients negative) |
| <a id="s26"></a> S26 | [`GEMSDOE/docs/METRIC_STRATEGY.md`](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE/main/docs/METRIC_STRATEGY.md) | the measured metric baselines (blanket 0.0956 on their window; thin beats blobby) |
| <a id="s27"></a> S27 | [`16GEMSDOE/docs/research/hypothesis_register.md`](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/docs/research/hypothesis_register.md) | the novelty screen: what the group has already proposed, tested or failed |

**Terms of use.** DrivenData's terms prohibit robots and automated access; this project links
to the leaderboard and stores dated manual snapshots only ([terms](https://www.drivendata.org/termsofuse/)).
