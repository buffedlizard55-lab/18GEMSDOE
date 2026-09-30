# Sources and claim registry

This page records the primary links behind the project’s factual claims. Official sources are separated from group self-reports. All accessed/reviewed for this project on **2026-09-30**, unless otherwise noted.

## Official competition sources

<a id="s1"></a>

### S1 — GEMS Prize competition page
[DrivenData competition #306](https://www.drivendata.org/competitions/306/competition-doe-gems/)

**Supports:** competition objective, data-tab workflow, submission navigation, external data encouragement, competition end date (Dec. 3, 2026 23:59 UTC). **Does not support:** any candidate’s score or hidden-label performance.

<a id="s2"></a>

### S2 — Problem description, metric, data and submission format
[DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

**Supports:** 100 m GeoTIFF features; GeoDAWN and INGENIOUS source families; 1 m DEM link list; single-band float32, EPSG:32611, same grid/bounds, `[0,1]`, null/NaN outside; distance-weighted Tversky α=0.2, β=0.8 and triangular 300 m support; labels are newly expert identified faults. **Does not identify:** hidden fault mapping method or complete hidden-label provenance.

<a id="s3"></a>

### S3 — Official NLR rules
[Official Rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

**Supports:** training/label context, up to three scored submissions per week, one final submission per entity across both prize rounds, same selected final submission scored in both rounds, reproducible code/documentation requirement for finalists. Read the rules directly before final submission.

<a id="s4"></a>

### S4 — DrivenData Terms of Use
[Terms of Use](https://www.drivendata.org/termsofuse/)

**Supports:** no robots, spiders, or other automatic devices to access the site. Project policy: no automated leaderboard polling absent written permission.

<a id="s5"></a>

### S5 — Organizer definition of “new fault”
[DrivenData staff reply](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2)

**Supports:** new pixels may be extensions, splays, or parallel strands of existing structures. **Does not reveal:** which methods or sources were used for hidden labels.

<a id="s6"></a>

### S6 — Organizer response about test-source details
[DrivenData staff reply](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7)

**Supports:** organizers will not share more about hidden-test data sources, fault types, or coverage beyond the problem description; later phase includes expert review of submissions.

<a id="s7"></a>

### S7 — Three-per-week reset window
[DrivenData staff clarification](https://community.drivendata.org/t/weekly-submissions/11524/2)

**Supports:** the submission allowance resets on a rolling window, not at a fixed calendar time. Combined with official rules §3.4.

<a id="s8"></a>

### S8 — Manual public leaderboard snapshot
[Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

**Supports:** the rows and scores displayed in the 2026-09-30 manual snapshot only. **Does not support:** account ownership or mapping scores to group artifacts. See [`registry/leaderboard_snapshot.json`](../registry/leaderboard_snapshot.json).

## Official mapping and geological data

<a id="s9"></a>

### S9 — USGS Quaternary Faults program
[USGS Faults / QFault methodology page](https://www.usgs.gov/programs/earthquake-hazards/faults) · [archived QFault example report (PDF)](https://earthquake.usgs.gov/static/lfs/nshm/qfaults/Reports/563b.pdf)

**Supports:** QFault is an archive compiled from thousands of mapped and published sources and used for seismic-hazard fault-source characterization. USGS says hazard traces/metadata are simplified representations based on geologic interpretation and that only a limited set of metadata fields has been maintained since 2017. Its methodology distinguishes evidence classes (including nontectonic Class D examples such as erosional/fluvial scarps), and archived reports preserve source citations and, for some records, mapping-scale/location-reliability notes. This is evidence of heterogeneous source history, not a claim that every present-day trace has a uniform or known positional error. **Caution:** QFault is not a complete, equally field-verified fault census.

<a id="s10"></a>

### S10 — Historical Nevada compilation limits
[NBMG, “Nevada’s Quaternary Fault Hazard” (1993)](https://nbmg.unr.edu/_docs/Newsletters/nl18.htm)

**Supports:** the first-cut 1993 statewide hazard data set included 304 faults/seismogenic sources and considered only the largest faults; the article says numerous smaller intrabasin Quaternary faults were not considered. Historical context only—not a claim about current QFault completeness.

<a id="s11"></a>

### S11 — Example of detailed INGENIOUS/QFault-era map methods
[USGS, Las Vegas Valley surficial geology and Quaternary fault map (2024)](https://www.usgs.gov/maps/surficial-geology-and-quaternary-fault-map-las-vegas-valley-clark-county-nevada)

**Supports:** a 1:50,000 compilation integrated 1:24,000 maps with new field/desktop work, lidar in undeveloped areas, historical photos in urban areas; existing traces were evaluated/modified; age work included published/new luminescence and radiocarbon ages. Example of a more detailed mapping workflow, not a statewide guarantee.

<a id="s12"></a>

### S12 — DOE GDR INGENIOUS dataset listing
[GDR submission 1391](https://gdr.openei.org/submissions/1391)

**Supports:** public access and CC BY 4.0 listing; dataset families include 2 m temperature, springs/wells and geochemistry, paleogeothermal sinter/tufa, Quaternary faults/volcanics, geodetic strain, conductance, gravity, magnetics and seismicity. The page lists a Quaternary Faults v1 file as an updated trace/age/slip-rate compilation whose attributes follow USGS QFault, and a v2 archive described as an updated compilation with a field-definition document. This listing does not describe per-trace positional accuracy, field-verification status, or all compilation decisions, and does not prove the archive was downloaded in this sandbox. A prior direct ZIP fetch returned HTTP 500; therefore v2 fields/bytes have not been inspected here.

<a id="s13"></a>

### S13 — USGS paleolake source
[USGS MF-2323, Extent of Pleistocene Lakes in the Western Great Basin](https://pubs.usgs.gov/mf/1999/mf-2323/)

**Supports:** publicly listed GIS downloads for western Great Basin paleolake extent. The [metadata](https://pubs.usgs.gov/mf/1999/mf-2323/mf2323_met.html) says shoreline locations were delineated using 3-arc-second (~90 m) DEM contour lines. Suitable as regional context; insufficient by itself for fine-scale 100 m fault offsets.

<a id="s14"></a>

### S14 — USGS 3DEP one-meter DEM collection
[Data.gov catalog](https://catalog.data.gov/dataset/1-meter-digital-elevation-models-dems-usgs-national-map-3dep-downloadable-data-collection) · [USGS 3DEP program](https://www.usgs.gov/3d-elevation-program)

**Supports:** public-domain 1 m DEM collection derived from high-resolution lidar. Catalog metadata warns products are seamless within projects, but not necessarily across projects. Exact GeoDAWN coverage is not checked in this checkout.

<a id="s15"></a>

### S15 — Official GeoDAWN survey specifications
[USGS GeoDAWN release page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)

**Supports:** survey date/extent, four acquisition blocks, overlapping Area 1/Area 2 surveys, line-spacing and flight-height differences, partial use of a Bell helicopter versus Cessna fixed-wing aircraft, and processing steps. In particular Area 1 line spacing is nominally 200 m and Area 2 nominally 400 m; not every acquisition block has a unique aircraft. Use for seam/confound controls.

<a id="s16"></a>

### S16 — Geothermal structural mechanisms
[Siler et al. (2019), USGS publication record](https://pubs.usgs.gov/publication/70202167) · [open-access DOI](https://doi.org/10.1186/s40517-018-0117-0)

**Supports:** in two Basin-and-Range geothermal systems, the authors use structural discontinuities (fault intersections/terminations) and stress state to examine upflow. This is mechanism context, not evidence that a particular 18GEMSDOE pixel is a fault.

<a id="s17"></a>

### S17 — Great Basin fault-mapping field example
[GBCGE Dixie Valley field site](https://gbcge.org/locations/dixie-valley/)

**Supports:** lidar/low-sun photos were used to identify traces, field mapping verified them, 2 m surveys identified possible anomalies, and one trenched candidate scarp had no stratigraphic offset and was interpreted as erosional. A specific false-positive example, not a rate estimate.

<a id="s30"></a>

### S30 — Nevada Bureau of Mines and Geology fault-layer scale warning
[NBMG Quaternary Faults MapServer metadata](https://gisweb.unr.edu/nbmg/rest/services/Geology/Faults/MapServer)

**Supports:** the regional layer is adapted/modified from NBMG M167 and USGS QFault; the service states the traces were originally digitized at 1:250,000, spatial error can be significant when viewed at larger scales, and site-specific fault presence needs qualified investigation. This is a direct Nevada-scale positional-accuracy warning, not a universal error radius for all catalog segments.

## Primary scarp-morphology references

<a id="s18"></a>

### S18 — Hanks et al. (1984)
[USGS publication record](https://www.usgs.gov/publications/modification-wave-cut-and-faulting-controlled-landforms) · [DOI](https://doi.org/10.1029/JB089iB07p05771)

**Supports:** diffusion-style morphology of wave-cut and faulting-controlled landforms; model outputs are products such as diffusivity × time under stated assumptions. The paper’s inclusion of shoreline forms is an important caution: shape/model fit does not establish tectonic origin.

<a id="s19"></a>

### S19 — Andrews & Hanks (1985)
[DOI/publisher record](https://doi.org/10.1029/JB090iB12p10193)

**Supports:** primary inverse solution for age from linearly diffusion-degraded scarps. Absolute age depends on diffusivity calibration; a morphology fit alone is not a calendar age.

<a id="s20"></a>

### S20 — Hilley et al. (2010)
[USGS publication record](https://pubs.usgs.gov/publication/70033862) · [DOI](https://doi.org/10.1029/2009GL042044)

**Supports:** high-resolution DEM method using the second derivative of modeled degraded scarp shape, least-squares height fit, and signal-to-noise to identify scarp-like topography. Does not make every matching landform a fault.

<a id="s21"></a>

### S21 — Sare et al. (2019)
[Open-access JGR article](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2018JB016886)

**Supports:** regional scarp extraction using a curvature template based on diffusion; template output includes false scarp-like landforms and their workflow used visual inspection to remove nontectonic features. This is a methodological warning, not a primary demonstration in the GeoDAWN region.

## Candidate-specific official data services

<a id="s22"></a>

### S22 — USGS ComCat
[ComCat documentation](https://earthquake.usgs.gov/data/comcat/) · [FDSN event API](https://earthquake.usgs.gov/fdsnws/event/1/)

**Supports:** official catalog contains source parameters and associated products including moment tensors/focal mechanisms; API supports event queries and specific event products. No GeoDAWN-area mechanism coverage count has been computed here.

<a id="s23"></a>

### S23 — NASA Sentinel-1 / ASF DAAC
[NASA Earthdata Sentinel-1](https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/sentinel-1) · [ASF search tool](https://www.earthdata.nasa.gov/data/tools/asf-search)

**Supports:** Sentinel-1 products are available via ASF DAAC, Vertex, `asf_search`, and Earthdata Search; NASA notes Earthdata Login is required to download/use some tools. No scene or coherence audit has been run for GeoDAWN.

## Group records — not official, not independently reproduced unless stated

<a id="s24"></a>

### S24 — 8GEMSDOE hypotheses and reported tests
[8GEMSDOE hypothesis page](https://buffedlizard55-lab.github.io/8GEMSDOE/docs/hypotheses.html)

**Supports only as a group record:** reported gravity/magnetic, scarp, strain, conductance, seismicity, linkage, valley-axis, and microseismicity hypotheses and their internal proxy numbers. Do not cite those scores as official competition results.

<a id="s25"></a>

### S25 — 16GEMSDOE public hypothesis register
[16GEMSDOE register](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/docs/research/hypothesis_register.md)

**Supports only as a group record:** prior proposals/tests including H18-5 thermal anchors (proposed, operator not built), H18-6 cultural suppression, H17 drainage/strain/alteration/basement ideas, and H18-1/3 arms. Useful to avoid duplication; not a complete audit of private work.

<a id="s26"></a>

### S26 — 16GEMSDOE holdout results and calibration
[Validation JSON](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/hypothesis_h18_validation.json) · [post-hoc proxy calibration](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/proxy_calibration_vs_lb.json) · [pre-registration](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/research/preregistration_h18.md)

**Supports only as a group report:** values and test rules as published by 16GEMSDOE. 18GEMSDOE has not rerun these files or code. The holdout uses known-catalogue and sparse proxy truth, not hidden new-fault labels.

<a id="s27"></a>

### S27 — 16GEMSDOE submission similarity registry
[Similarity evidence JSON](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/evidence/submission_similarity.json)

**Supports only as a group-computed file registry:** 21 entries and its pixel-level comparison claims. This repo independently checked exact Git blob identity for the two public files `GEMSDOE` and `5GEMSDOE`; it did not independently recreate all pixel comparisons.

<a id="s28"></a>

### S28 — Public GEMSDOE bridge manifest (team-maintained)
[Manifest](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE/main/data/bridge/manifest.json) · [data README](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE/main/data/README.md)

**Supports only:** what that repository asserts about its mirrored files and hashes. A hash match to this manifest is not an independent official source comparison.

## External software used for the browser-only builder

<a id="s29"></a>

### S29 — geotiff.js
[Project repository and license](https://github.com/geotiffjs/geotiff.js) · [npm package](https://www.npmjs.com/package/geotiff)

The browser builder uses the MIT-licensed `geotiff` package for local GeoTIFF reading/writing. It processes files locally in the browser; it does not send files to an external service. The Python/rasterio validator remains the independent format check.
