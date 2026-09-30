# Data access and provenance status

**No competition raster has been placed in this repository. No candidate can be tested here yet.** Do not infer data access from another project’s status or from a public mirror’s manifest.

## Official competition data

The official problem description says registered competitors receive a 100 m multiband `training_features.tif`, training fault labels, an example submission, and a list of links for 1 m DEM tiles. The official data tab is account-gated; this checkout does not contain or independently verify those original files. [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [official data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/).

The `18GEMSDOE` directory currently contains no `data/`, `training_features.tif`, official sample template, vector/raster labels, DEM mosaic, holdout masks, or manifest. Nothing has been trained or scored in this repository.

## Small public mirror artifact checked earlier

A prior session fetched `existing_faults.tif` from the public `GEMSDOE` GitHub bridge into `/tmp/gems_existing_faults.tif`:

- 425,830 bytes; SHA-256 `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093`.
- The digest matches that bridge repository’s `manifest.json` and its TIFF header was checked.
- The bytes were **not** compared to a fresh official DrivenData download; raster values, transform, nodata, and label semantics were not opened/verified with a raster library.
- The public manifest’s claim that files originated from the official data-tab mirrors is a team assertion, not independent provenance.

This file is outside the repo and is not a holdout, hidden label set, or submission. It has not been copied into the project.

The public bridge also lists five pieces of a GeoDAWN feature stack totaling 418,912,844 bytes. That larger stack has not been downloaded in this checkout. The 16GEMSDOE evidence JSON publishes expected hashes for its stack/labels/template, but those are group-reported values until matched against official-source bytes.

<a id="fault-catalogue-coverage-and-mapping-quality"></a>

## Fault-catalogue coverage and mapping quality

The USGS QFault documentation describes a hazard-oriented compilation built from many published maps and studies; its fault surface traces and attributes are simplified geologic interpretations for seismic-hazard characterization. USGS says only a limited set of metadata fields has been maintained since 2017. QFault also distinguishes evidence classes, including Class D examples that are demonstrably nontectonic (such as erosional or fluvial scarps). Archived reports preserve reference trails and, for some traces, a stated reliability/compilation scale; those scales and source maps are not uniform. One report is an example, not a region-wide accuracy estimate. The older Nevada hazard compilation also explicitly focused on larger sources and omitted numerous smaller intrabasin Quaternary faults; that is historical context, not proof of which traces the current hidden labels add. See [USGS QFault methodology and report example](sources.md#s9), [NBMG 1993](sources.md#s10), the [detailed Las Vegas mapping example](sources.md#s11), and the [Nevada 1:250,000 scale warning](sources.md#s30).

The GDR listing says INGENIOUS Faults v1 is an updated compilation whose attributes follow QFault; v2 is described as an updated compilation with a field-definition document. The v2 archive was not downloaded or inspected here (prior ZIP retrieval returned HTTP 500), so we do not claim its per-trace positional accuracy or field-verification history. For any future analysis, inspect the actual per-segment source and whatever scale, location-certainty, and evidence fields the downloaded archive supplies; preserve the provenance and model location uncertainty explicitly where possible. **Do not treat every mapped trace as equally precise or field-verified; do not treat unmapped ground as a confirmed negative.** [INGENIOUS GDR listing](sources.md#s12)

## External candidate data checked

### USGS paleolake mapping (H18-N1 context)

USGS MF-2323 publicly lists downloadable GIS packages (about 3.23 MB) and a georeferenced relief package. Its metadata says shoreline positions were delineated using approximately 3-arc-second (~90 m) DEM contours. The listing proves that a public download is advertised; this checkout has **not** downloaded the package, verified its hash, or established that it contains marker detail suitable for the GeoDAWN footprint. Use it as regional context only until inspected. [USGS map page](https://pubs.usgs.gov/mf/1999/mf-2323/) · [metadata](https://pubs.usgs.gov/mf/1999/mf-2323/mf2323_met.html).

### USGS 3DEP one-meter DEM

The USGS/Data.gov catalog identifies a public-domain 1 m DEM collection. The catalog notes that DEM surfaces are seamless within collection projects but not necessarily across projects. The competition’s exact 1 m tile list is on its gated data tab. This checkout has not confirmed which 1 m projects cover which GeoDAWN blocks or whether their seams align with GeoDAWN acquisition boundaries. [Catalog](https://catalog.data.gov/dataset/1-meter-digital-elevation-models-dems-usgs-national-map-3dep-downloadable-data-collection) · [3DEP landing page](https://www.usgs.gov/3d-elevation-program).

### INGENIOUS GDR (not selected as a “new” idea)

The official DOE Geothermal Data Repository listing for INGENIOUS is public, states CC BY 4.0, and lists 9 resources totaling 116.98 MB, including 2 m temperature probes, spring/well temperature and chemistry, and paleogeothermal sinter/tufa data. Direct ZIP fetches from this agent sandbox returned HTTP 500 in a prior session. The listing is verified; archive bytes are not. The 16GEMSDOE page says a runner downloaded the data, but that is a sibling-project claim. Also, thermal-anchor linking already appears as H18-5 in that public register, so it is not novel here. [GDR 1391](https://gdr.openei.org/submissions/1391) · [16GEMSDOE register](https://raw.githubusercontent.com/buffedlizard55-lab/16GEMSDOE/main/docs/research/hypothesis_register.md).

### USGS ComCat and NASA ASF Sentinel-1 (conditional candidates)

Official documentation confirms that USGS ComCat exposes source parameters and moment-tensor/focal-mechanism products through an event service; the GeoDAWN-area event count has not been checked. NASA Earthdata confirms global Sentinel-1 data access through ASF DAAC, but downloads/some tools require an Earthdata login; no credentials, scenes, or interferograms are present here. [ComCat](https://earthquake.usgs.gov/data/comcat/) · [FDSN API](https://earthquake.usgs.gov/fdsnws/event/1/) · [NASA Sentinel-1](https://www.earthdata.nasa.gov/data/platforms/space-based-platforms/sentinel-1).

## Required data placement checklist

When the authorized files become available, place them outside Git and point `GEMS_DATA_DIR` to the directory. Before model work:

1. Hash each original download and record exact source URLs, retrieval times, license, and file sizes.
2. Open every raster and verify CRS, dimensions, pixel size, transform, valid-mask/nodata, dtype, and band descriptions against the official competition documentation/template.
3. Compare original official bytes with any existing bridge copy by SHA-256; do not substitute a manifest claim for this check.
4. Verify label raster semantics against vector labels and the official sample footprint.
5. Construct and commit the split/holdout manifest before implementing or tuning H18-N1.
6. Keep private/hidden labels, credentials, and raw data out of Git.

Until those checks are complete, the status is **blocked**. See [preregistration](research/preregistration.md) and [audit flags](audit.md).
