# Line-by-line verification log (2026-09-30 session)

Every row: claim → verdict → evidence link → how verified (fetched page / search record).

## Competition & scoring

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| V1 | Task = predict faults; test = new expert-mapped faults absent from USGS; two prize rounds, same file rescored | VERIFIED | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) (fetched) |
| V2 | Metric = distance-weighted Tversky, α=0.2, β=0.8, triangular kernel R=300 m; fixture 0.60 | VERIFIED | same (fetched); transcribed + self-tested in `scripts/dti_metric.py` |
| V3 | Submission = single-band float32 GeoTIFF, EPSG:32611, 100 m, same bounds, [0,1], outside null/NaN | VERIFIED | same (fetched) |
| V4 | Known USGS/INGENIOUS pixels masked from scoring, both rounds | VERIFIED (staff post) | [forum 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) (fetched) |
| V5 | "New fault" = any fault pixel not already captured by USGS/INGENIOUS, incl. newly mapped geometry of existing systems | VERIFIED (staff post) | [forum 11536](https://community.drivendata.org/t/where-do-you-draw-the-line/11536) (fetched) |
| V6 | Organizers will not disclose test-fault sources/types/coverage | VERIFIED (staff post) | [forum 11527](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7) (fetched) |
| V7 | Leaderboard top = 0.3168 (DARD) at fetch; SDCF9 = smashi34 = 0.1563; extradr19 = 0.1855 | VERIFIED (snapshot) | [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) (fetched 2026-09-30) |
| V8 | Ends Dec 3, 2026 23:59 UTC; $300k ($50k initial + $250k final) | VERIFIED | [competition hub](https://www.drivendata.org/competitions/306/competition-doe-gems/) (fetched) |
| V9 | External data allowed with proper license | VERIFIED | hub rules summary (fetched); full [rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) (fetched ch.0–3) |
| V38 | 3 submissions per week; one final submission per entity; team members no separate finals | VERIFIED | rules PDF §3.2 + §3.4 (fetched) |
| V39 | Generative-AI use must be disclosed in finalist narrative; finalists deliver reproducible code+docs | VERIFIED | rules PDF §3.2 (fetched) |
| V40 | Training labels = INGENIOUS Great Basin Regional Dataset Compilation (Ayling et al. 2022, doi:10.15121/1881483) | VERIFIED | rules PDF §3.3 fn.4 (fetched) |
| V41 | Metric "penalizes false negatives … more than false positives" (recall game) | VERIFIED | rules PDF §3.6.1 (fetched) |

## Group history & duplicates

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| V10 | GEMSDOE1 ≡ 5GEMSDOE bytes (sha 7f00890a…, 172,974 px @1.0) | VERIFIED | both build panels fetched live (identical pins + census) |
| V11 | 8GEMSDOE = 0.1563 pattern ∪ catalogue (masked ⇒ equal); GEMSDOE2 94.6% overlap | VERIFIED | [8GEMSDOE](https://buffedlizard55-lab.github.io/8GEMSDOE/) + [16GEMSDOE](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html) audits (fetched) |
| V12 | Implemented family: H1–H10, H-A–H-E, H16-1, H18-3a/4, Sato, HGB, Pindrop, scarp/ridge/alteration arms | VERIFIED | [8GEMSDOE hypotheses](https://buffedlizard55-lab.github.io/8GEMSDOE/hypotheses.html) (fetched, 3 chunks) + 16GEMSDOE index (fetched) |
| V13 | H8 tip-corridors falsified (0.0001 vs random 0.049) | VERIFIED as sibling-measured | same hypotheses page |
| V14 | 0.1855 ↔ h16-1 file linkage | UNVERIFIED (flag F07) | owner record vs "not yet live-scored" page snapshot conflict |

## Primary methods

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| V15 | Blakely & Simpson 1986, Geophysics 51, 1494–1498, doi:10.1190/1.1442197 | VERIFIED | bibliographic record (search) |
| V16 | Miller & Singh 1994, J. Applied Geophysics 32, 213–217 (tilt derivative) | VERIFIED | Springer reference record (search) |
| V17 | Thompson 1982 EULDPH, Geophysics 47(1), 31–37, doi:10.1190/1.1441278 | VERIFIED | bibliographic record (search) |
| V18 | Reid et al. 1990, Geophysics 55, 80–91, doi:10.1190/1.1442774; contact SI=0 | VERIFIED | Springer + Reid–Thurston records (search) |
| V19 | Hanks et al. 1984, JGR 89(B7), 5771–5790, doi:10.1029/JB089iB07p05771 | VERIFIED | AGU reference record (search) |
| V20 | Andrews & Hanks 1985 inverse age solution, JGR 90(B12) | VERIFIED | Seismica reference record (search) |
| V21 | Hanks & Wallace 1985 Lahontan shorelines, BSSA 75, 835–846 | VERIFIED | reference record (search) |
| V22 | Hack 1973 SL index, USGS J. Research 1, 421–429 | VERIFIED | Springer reference record (search) |
| V23 | Burbank & Anderson 2011, Tectonic Geomorphology 2e, ISBN 978-1-4443-3887-4 | VERIFIED | publisher-record mirrors (search) |
| V24 | Tchalenko 1970, GSA Bull. 81, 1625–1640; R-shears ~12–17° | VERIFIED | ScienceDirect reference record (search) |
| V25 | Faulds & Henry 2008 Walker Lane dextral transtension, AGS Digest 22, 437–470 | VERIFIED | OSTI citing record (search) |
| V26 | Zevenbergen & Thorne 1987, ESPL 12, 47–56, doi:10.1002/ESP.3290120107 | VERIFIED | Semantic Scholar record (search) |

## Data sources

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| V27 | GeoDAWN release doi:10.5066/P93LGLVQ; Area 1: 200 m lines/helo; Area 2: 400 m lines | VERIFIED | [USGS release page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) (search excerpt) |
| V28 | "Four survey blocks / four aircraft" | UNVERIFIED (flag F09) | release text names Area 1 + Area 2 only |
| V29 | INGENIOUS GDR 1391, doi:10.15121/1881483, CC-BY; paleo-geothermal + wells/springs + faults + strain | VERIFIED | [GDR 1391](https://gdr.openei.org/submissions/1391) (fetched) |
| V30 | MT conductance maps span 2–200 km from ~800 stations → too coarse for traces | VERIFIED | [doi:10.5066/P9TWT2LU metadata](https://data.usgs.gov/datacatalog/metadata/USGS.62979746d34ec53d276c113b.xml) (search) |
| V31 | SGMC seamless 48-state DB, doi:10.5066/F7WH2N65, ~1:1M | VERIFIED | [ScienceBase record](https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d) (search) |
| V32 | 3DEP 1/3″ DEM free public domain | VERIFIED | [data.gov listing](https://catalog.data.gov/dataset/1-3rd-arc-second-digital-elevation-models-dems-usgs-national-map-3dep-downloadable-data-co) (search) |
| V33 | NHDPlus HR free public domain (GDB by HU4), built on 3DEP 10 m | VERIFIED | [USGS access page](https://www.usgs.gov/national-hydrography/access-national-hydrography-products) (search) |
| V34 | QFault DB: M>6 Quaternary archive; NV entries often reconnaissance photogeology, no trench/scarp studies | VERIFIED | [USGS faults page](https://www.usgs.gov/programs/earthquake-hazards/faults) + [example report PDF](https://landslides.usgs.gov/static/lfs/nshm/qfaults/Reports/1307.pdf) (search) |
| V35 | USGS DS 234: isostatic patterns reveal buried faults | VERIFIED | [NV gravity memo](https://pubs.usgs.gov/ds/2006/234/nv_iso.htm) (cited; page not re-fetched — sibling-verified quote) |
| V36 | Competition data behind login; absent here | VERIFIED (long-standing blocker) | data tab login redirect (prior sessions); data/ empty here |
| V37 | 716 1 m tiles / ≈130 GB census | SIBLING-MEASURED, not re-verified (flag F10) | 8GEMSDOE session notes |
