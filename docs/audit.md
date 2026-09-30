# Audit and irregularities

Statuses distinguish **DIRECTLY VERIFIED** (checked in this session), **OFFICIAL SOURCE** (official statement/page), **GROUP-REPORTED** (a sibling project’s published result), and **OPEN** (not resolved).

<a id="a-01"></a>

## A-01 — No project data or validation artifacts in this checkout — OPEN / BLOCKER

**Finding:** this branch started with only `README.md`. There is no official feature stack, sample template, label raster, model, locked split, holdout output, or candidate GeoTIFF in 18GEMSDOE. No model was trained or evaluated here. A public-mirror label file was hash-matched to that mirror’s manifest in a prior session, but not compared with an official download or opened as a raster.

**Impact:** the new hypotheses cannot be scored; the holdout is not locked; no 18GEMSDOE submission is ready. Do not submit or report a candidate score until resolved.

**Next evidence:** stage authorized source files outside Git, verify bytes/metadata/provenance, then lock a basin/fault-system holdout before coding. [Data status](data.md) · [preregistration](research/preregistration.md).

<a id="a-02"></a>

## A-02 — Repeated 0.1563 artifact — DIRECTLY VERIFIED IN PART

**Finding:** the public `GEMSDOE` and `5GEMSDOE` repositories both store a 570,890-byte `submission.tif` with Git blob SHA `812e61b74050d1350cc2bde1fab0c76ead32e0c4`; both sidecar fields also have the same blob SHA `6a89b64e01a7c11b8235449c538390ac3435605d`. This is exact byte identity for those tracked files. The public 16GEMSDOE registry maps the display name `GEMSDOE1` to the `GEMSDOE` repo and reports that it/5GEMSDOE scored 0.1563; it also reports 8GEMSDOE is pixel-identical on the scored mask. The latter comparisons and the upload mapping have not been recomputed here.

**Impact:** copying the same tracked prediction into a second site is not a new candidate; same pixels would ordinarily produce the same deterministic score. Score equality alone does not prove two other entrants share a file. GitHub lookup for a repository literally named `GEMSDOE1` returned 404; this may be a display name rather than a repo.

**Next evidence:** reconcile platform submission IDs and file hashes in the account; never infer upload mapping from a site’s displayed artifact. [Results](results.md).

<a id="a-03"></a>

## A-03 — Public mirror is not independent official provenance — OPEN

**Finding:** a public `GEMSDOE` bridge manifest pins a hash for `existing_faults.tif`; the local file hash matched that manifest. The manifest asserts a link to official data-tab mirrors, but no original official data download was available for byte comparison. The full feature stack remains undownloaded in this checkout.

**Impact:** hash agreement proves identity with the bridge manifest, not source provenance, raster semantics, or an eligible validation input.

**Next evidence:** compare every bridge file to the official source download and record raster metadata. Keep bridge artifacts out of production until then. [Data status](data.md).

<a id="a-04"></a>

## A-04 — Current leaderboard vs historical group status — OPEN ATTRIBUTION

**Finding:** a manual official leaderboard snapshot on 2026-09-30 shows DARD 0.3168 at rank 1 and `extradr19` 0.1855 at rank 22, with four submissions shown. The public 16GEMSDOE README still describes 0.1563 as the group’s best public score. This checkout does not establish whether `extradr19` is the group’s entrant, whether the README is stale, or how any live submission maps to a local file.

**Impact:** the prior `.1563` may no longer be the best group public result. Do not repeat it as the current top score without resolving account ownership and submission history. The user’s previously cited leader score 0.3049 is also stale relative to this manual snapshot.

**Next evidence:** compare the signed-in team account, submission IDs, timestamps, filenames, and hashes manually; update `registry/score-ledger.csv`. No automated polling is used. [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) · [snapshot](../registry/leaderboard_snapshot.json).

<a id="a-05"></a>

## A-05 — Prior holdout is a weak, group-reported proxy — OPEN REPRODUCTION

**Finding:** 16GEMSDOE reports H18-3a means of 0.21319 dense / 0.09401 sparse, a pass over H16-1’s 0.21272 / 0.08541 on a four-quadrant known-fault/sparse-proxy protocol. It is not hidden-label performance and has not been rerun in this checkout. Its own post-hoc calibration reports no detectable dense-proxy rank relationship to 15 historical public scores (ρ=0.171, p=0.5413).

**Impact:** use H18-3a only as a provisional comparator; reproduce the evaluator and disclose proxy limitations. No candidate has passed any 18GEMSDOE gate.

<a id="a-06"></a>

## A-06 — No automatic DrivenData leaderboard feed — COMPLIANCE CONTROL

**Finding:** DrivenData Terms of Use prohibit robots, spiders, or other automatic devices from accessing the site. The platform has no approved API/permission established in this checkout.

**Impact:** automatic monitoring cannot be implemented responsibly now. The site links to the official board and stores manually read, dated snapshots. Seek written permission before any automation. [Terms](https://www.drivendata.org/termsofuse/).

<a id="a-07"></a>

## A-07 — GeoDAWN acquisition boundaries can mimic geophysical edges — CONTROL REQUIRED

**Finding:** USGS describes four north-to-south acquisition blocks. Area 1 and Area 2 have different flight specifications, including nominal line spacing of 200 m vs 400 m; the Tonopah block’s Area 1 and part of Area 2 were flown with a Bell helicopter, while other Area 2 portions used fixed-wing aircraft. Do not simplify this to “each block had a different aircraft.” 3DEP one-meter products may also have inter-project seams.

**Impact:** gradient/edge hypotheses must predict an edge at the actual fault trace and include lithologic contacts, acquisition block boundaries, flight-spec changes, and DEM-project seams as controls. No detector should reward data-processing stripes. [USGS GeoDAWN survey page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [3DEP catalog](https://catalog.data.gov/dataset/1-meter-digital-elevation-models-dems-usgs-national-map-3dep-downloadable-data-collection).

<a id="a-08"></a>

## A-08 — Scarp morphology is not a fault label — SCIENCE CONTROL

**Finding:** Hanks et al. (1984) applied diffusion-style morphology to both wave-cut shoreline and fault-controlled landforms. Hilley et al. (2010) match a modeled curvature template to *scarp-like* DEM topography. Sare et al. (2019) report roads/channels/other scarp-like features in results and use review to remove false detections. GBCGE documents a trenched scarp that proved erosional.

**Impact:** do not call a template match or inferred `κt` an absolute fault age or tectonic proof. Any geomorphic detector needs explicit roads, canals, channels, shoreline, fan-margin, and erosional controls. [Scarp literature and primary sources](research/hypotheses.md#scarp-diffusion-science).

<a id="a-09"></a>

## A-09 — Candidate source access/coverage remains conditional

**Finding:** USGS MF-2323 shoreline GIS, the 3DEP 1 m catalog, ComCat documentation, NASA ASF Sentinel-1 access, and GDR 1391 listings are available to review. This checkout has not downloaded/checked the exact DEM tiles, queried ComCat mechanism coverage, processed Sentinel-1 scenes, or verified the GDR ZIP bytes. Some NASA products/tools require Earthdata login; GDR direct ZIP requests returned HTTP 500 in the earlier sandbox session.

**Impact:** the shortlist is not a declaration that data is immediately usable. Run an access/coverage audit before claiming a candidate is feasible. [Sources](sources.md) · [data status](data.md).

<a id="a-10"></a>

## A-10 — Submission tools have not seen the official template — OPEN / ENGINEERING LIMITATION

**Finding:** the Python validator/packager, evidence gate, and browser GeoTIFF writer have been implemented and exercised using synthetic rasters. No official competition sample template or full-size user prediction was available for a real-file round trip. The release gate validates required evidence fields and recomputes fold thresholds, but hashes and boolean flags do not authenticate that the scientific evidence is genuine or correctly computed.

**Impact:** passing synthetic tests establishes tool behavior for the tested fixtures only; it does not certify compatibility with the competition file, validate scientific performance, or authorize an upload.

**Next evidence:** run both tools against the authorized official template; inspect output in an independent GeoTIFF reader; have a reviewer audit the source logs, split lock, baseline, controls, uniqueness comparison, and evidence artifacts.

<a id="a-11"></a>

## A-11 — Fault-catalogue positional confidence is heterogeneous — CONTROL REQUIRED

**Finding:** USGS describes QFault traces/attributes as simplified geologic interpretations for hazard characterization and says only a limited set of metadata fields has been maintained since 2017. Archived reports and Nevada compilation metadata illustrate differing source scales/reliability; NBMG warns that some regional Nevada traces were digitized at 1:250,000 and may be inaccurate at larger viewing scales. The GDR listing describes INGENIOUS Faults v1/v2 as an updated, QFault-related compilation, but v2 ZIP bytes/field definitions were not inspected here after a prior download error. Historical Nevada work documented omitted smaller intrabasin Quaternary faults, but that does not identify current competition labels.

**Impact:** never treat catalogue traces as equal-accuracy, field-verified ground truth or unmapped space as confirmed non-fault. Use per-segment source/scale/certainty fields where available, document label uncertainty, spatially group source campaigns, and treat catalogue-derived validation as a proxy with known completeness and location limits.

**Next evidence:** inspect the exact authorized/catalogue release and each segment’s provenance/quality fields before constructing folds or controls. See [QFault/INGENIOUS sources](sources.md#s9) and [data caveats](data.md#fault-catalogue-coverage-and-mapping-quality).
