# Hypothesis register — 18GEMSDOE (H19 pass, 2026-09-30)

**Evidence labels used on every page of this site.**

| Tag | Meaning |
|---|---|
| **[OFFICIAL]** | read from the primary source (competition page, rules PDF, a DrivenData-staff forum post) — link given. |
| **[MEASURED-HERE]** | recomputed in this checkout from the official rasters by a named script; the evidence JSON is named. |
| **[GROUP-REPORTED]** | stated by a sibling project; its evidence file is linked but was not re-run here. |
| **[INFERENCE]** | reasoning, explicitly not a measurement. |

## 1. The five facts that decide the strategy

| # | Fact | Class | Source |
|---|---|---|---|
| 1 | Known USGS/INGENIOUS fault pixels are masked **pixel-exactly** in both rounds — identical to the provided training labels — so a prediction on them can neither earn nor cost anything, and there is **no buffer** around them. | [OFFICIAL] | forum 11516 [post 4](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/4) |
| 2 | A predicted pixel near a known trace but far from a **new**-fault pixel is fully penalised; a new-fault pixel *can* sit within 300 m of a known trace ("corrections or modifications"). | [OFFICIAL] | same |
| 3 | "New fault" = any fault pixel not captured by USGS/INGENIOUS, **including newly mapped geometry of an existing system** (extensions, splays, parallel strands). | [OFFICIAL] | forum 11536 [post 2](https://community.drivendata.org/t/where-do-you-draw-the-line/11536/2) |
| 4 | The organizers will not disclose the data sources, fault types or coverage of the test faults; the Phase-2 test set is **updated by expert review of all Phase-1 submissions**. | [OFFICIAL] | forum 11527 [post 7](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7) |
| 5 | The training labels are the **USGS Quaternary Fault & Fold database inside the survey footprint**: of the 71,985 QFaults line pixels that fall inside the valid footprint, **71,984 (100.00 %) lie within 300 m of a training label**, and 60,988 label pixels exist. | [MEASURED-HERE] | `data/evidence/audit_checks.json`, rasterised from the public 2023-06-27 INGENIOUS QFaults release |

**[INFERENCE]** Taken together: the scored truth is *faults that QFaults does not contain*; every emission must therefore be a candidate the catalogue is missing, and the emission policy — not the detector's prettiness — is what the metric pays for.

**Metric algebra [MEASURED-HERE, `gems18/metric.py`, anchored to the official worked example].**
`DTI = TP_w / (0.2·M + 0.8·|G|)` with `M` the emitted mass and `G` the truth. Consequences used below:

* raising every value to 1 can only help (the `0.8·|G|` term is fixed);
* adding a candidate population helps iff its *covered-truth mass per emitted mass* exceeds `0.2 × DTI`, i.e. ≈ 0.03–0.06 for the scores this group is getting — false positives are cheap, misses are 4× more expensive;
* one pixel wide, uniform, on the structure beats a shaded blob of the same recall.

## 2. What the group has already tried — the novelty screen

**[GROUP-REPORTED]** From `16GEMSDOE`'s register and `5GEMSDOE`'s status: topography+magnetics+gravity ridge blends (H16-1, the group's best public score), fault-tip/junction density priors (H18-3a: passed its gate, but a plain fault-density control recovered most of the lift — i.e. the gain was fault clustering), SGMC state-map faults as *proxy truth* (H18-4: "cannot test *new*"), geothermal-disk priors (GDR-355: ρ ≈ −0.6 against the board — rejected as an instrument), radiometric K/Th/U added bands (+0.002 on their paired fold test), catalogue-adjacent top-k emissions (0.0286/0.0202/0.0461), oblique-strike and product-of-experts fusion (failed).

**[INFERENCE]** Nothing in that list is a *population* claim about what the hidden set contains. The three hypotheses below are, and the fourth is a data claim that the others have not used.

## 3. Candidates, ranked by expected gain per unit of cost

### H19-A — multi-physics conjunction lineaments (implemented, validated)

| | |
|---|---|
| **Layers** | `rtp`, `tmi`, `tmi_hg` (magnetics) × `iso_grav_anom`, `iso_grav_anom_hg` (gravity) × `det_elev`, `det_elev_slope` (topography) |
| **Signature** | multi-scale horizontal-gradient magnitude and tilt-derivative ridges on the potential fields, Laplacian curvature ridges on the detrended DEM; **kept only where ≥2 of the 3 families have a ridge within one pixel** |
| **Mechanism** | a fault plane juxtaposes rock of different density and magnetic susceptibility, so the potential-field gradient peaks over the trace of the plane; a surface-breaking fault also breaks the slope. Two independent physical origins agreeing at one pixel is far less likely by chance than either alone |
| **Why it should find a fault the catalogue lacks** | the catalogue is hazard-oriented and Quaternary in scope; the physics does not know that. Older, shorter, buried and mis-located structures produce the same gradient signature |
| **Non-fault look-alikes** | lithologic and volcanic-flow contacts (magnetic + gravity both step across them), playa/alluvial-fan edges (topographic + gravity), roads/canals/fences (topographic only), and the GeoDAWN survey seams and data-boundary edge (any family) |
| **Separating test** | a **matched random lineament network** at the same support — measured on the SGMC-gap proxy: at 250,000 px the conjunction scores 0.1229 against the random network's 0.0930, but at the shipped file's own mass (172,974 px) it scores 0.0926 against 0.0882, i.e. barely above its null; plus a single-family ablation (topography 0.1204, magnetics 0.0459 at 250,000 px) and the boundary mask |
| **Differs from** | H16-1 blends families arithmetically into one scalar; H18-1 multiplied experts and failed. This is a conjunction with a control, and it is emitted under the metric's own algebra |
| **Cost** | one CPU pass over the raster, no new data |
| **Status** | **implemented** (`scripts/run_detectors.py`, `scripts/build_candidate.py`); tuning folds choose the support, sealed blocks read once — and the sealed read did **not** confirm a win (the promoted arm scored 0.0003 against the shipped file's 0.0085) |

### H19-B — state-map structures the catalogue does not contain (implemented; unverifiable premise, stated as such)

| | |
|---|---|
| **Layers** | USGS State Geologic Map Compilation structure lines (external, US public domain) vs the training labels |
| **Signature** | the *population* of mapped fault lines with **no training label within 300 m**: 61,664 px inside the footprint **[MEASURED-HERE]** |
| **Mechanism** | state geologic maps record bedrock structures mapped from field geology; the Quaternary fault database records only structures with evidence of surface rupture in the last 1.6 Myr. A fault can be in the first and not the second |
| **Why it should find a fault the catalogue lacks** | by construction every pixel of the component is outside the pixel-exact scoring mask, so it cannot be "already known" in the competition's sense |
| **Non-fault look-alikes** | map compilation artefacts, coast/terrain lines, 1:1,000,000 generalisation offsets (hundreds of metres), mining and volcanic contacts |
| **Separating test** | the honest one: it **cannot** be validated against the hidden truth from here, and no proxy in this repository can decide it. What *is* tested is whether the component's pixels are physically expressed (fraction coincident with H19-A ridges) — a weak consistency check, not a validation |
| **Differs from** | the group used SGMC as a *proxy truth* (H18-4) and one sibling rasterised SGMC faults as an input band; neither **emitted** the gap population as the predicted fault network |
| **Cost** | one rasterisation; data already staged |
| **Status** | **implemented**; the premise is published with the component's exact size and its cost in the denominator, so the risk is visible |

### H19-C — the composite actually shipped (implemented)

`catalogue ∪ state-map structures ∪ H19-A physics`, all at value 1, one pixel wide, NaN outside the
footprint. Rationale: the catalogue is free, the state-map network is a population bet whose downside
is a known number of false-positive pixels, and the physics adds the case the catalogue cannot see.
Composition, cost and a sensitivity table (score as a function of the assumed truth size and coverage)
are written to `data/evidence/candidate_h19.json` and rendered on the [Validation](../validation.html)
page.

### H19-D — radiometric alteration lineaments (proposed; source verified available)

| | |
|---|---|
| **Layers** | the GeoDAWN airborne radiometric channels `k`, `th`, `u`, `tc`, `thk`, `uk`, `uth` — **absent from the 19 provided bands** |
| **Signature** | ridges and edges on the K channel and on the Th/K and U/Th ratios (ratios cancel soil-moisture and elevation gain), required to co-locate with a potential-field gradient |
| **Mechanism** | fault damage zones are pathways for fluids; K-feldspar/clay alteration enriches K along them, and U is mobile in oxidising fluids — the classic radiometric alteration signature used in geothermal exploration |
| **Why it should find a fault the catalogue lacks** | alteration haloes mark *buried* faults that have no scarp and no Quaternary rupture record, which is exactly the class the hazard catalogue is thin on |
| **Non-fault look-alikes** | lithology (rhyolite vs basalt K contrast), soil/vegetation cover, mine dumps, and the radiometric survey's own flight-line corrugation |
| **Separating test** | the ratio channels must beat the raw channels (if they do not, the signal is soil/lithology, not alteration); and the ridge must be co-located with a magnetic or gravity gradient |
| **Differs from** | the K/Th/U grids are **not** among the 19 provided bands — verified by exact signature matching: of the 13 GeoDAWN area-2 layers, only `rtp`, `tmi`, `tmi_hg`, `tmi_vg` (and `tc`, under a misleading tag) appear in the competition stack **[MEASURED-HERE]** |
| **Cost** | one external download (USGS public domain; a pinned public mirror is reachable from this sandbox) |
| **Status** | **proposed**, not run in this pass: a sibling measured only +0.002 for radiometrics in a paired fold test **[GROUP-REPORTED]**, so it ranks below the implemented arms |

### H19-E — along-strike continuation from mapped tips, with a rotation control (proposed)

| | |
|---|---|
| **Layers** | `labels.tif` geometry × H19-A magnetic/gravity ridges |
| **Signature** | a ridge that continues a mapped fault's strike beyond its tip, or parallels it inside the same zone |
| **Mechanism** | the organizers state that new faults include extensions, splays and parallel strands of known systems [OFFICIAL, fact 3], and the structural literature puts a large share of Great Basin geothermal systems at step-overs and terminations (Faulds & Hinz 2015, [OSTI 1724082](https://www.osti.gov/servlets/purl/1724082)) |
| **Non-fault look-alikes** | any ridge that happens to point away from any fault tip — which is why the control is a **random rotation** of the mapped-fault field: the aligned population must beat its own rotated surrogates, or the "continuation" is an artefact of drawing lines near lines |
| **Separating test** | rotate the fault-tip field by 100 random angles and re-measure; the real alignment must sit in the tail |
| **Status** | **proposed**; a sibling tested a *kernel-density* version of this idea (H18-3a) and found most of its lift came from generic fault clustering, which is why this version is per-lineament and rotation-controlled |

## 4. Validation protocol (preregistered before the numbers were seen)

1. Every arm is evaluated inside a spatially blocked holdout: 512 px (51.2 km) blocks, folds balanced
   on fault mass, **14 sealed blocks** that no selection step may touch, split digest
   `41332369d7dd448b…` (`data/evidence/holdout_manifest.json`).
2. Two truths are used, and they are never confused:
   * the **catalogue holdout** — training-label pixels in held-out blocks, unmasked. It answers "can
     this arm find faults it was not shown at all?", and it is the only truth in this repository that
     is *not* an external map;
   * the **SGMC-gap proxy** — state-map fault pixels with no label within 300 m. It stands in for
     "faults the catalogue lacks", with the caveat that it is a 1:1,000,000 map product.
3. Controls run *before* the promoted arm is described: matched random lineament network, blanket
   field, single-family ablation, catalogue copy (which must score exactly 0 on the gap proxy).
4. The sealed slice is read once, after the support is fixed, and reported whichever way it falls.
5. An improvement counts only if it survives the sealed slice **and** the strongest attempt to argue
   it away as an artefact (boundary mask, single-family ablation, mass-matched comparison).

## 5. Results

<!-- RESULTS_TABLE -->

## 6. Sealed read (single, pre-registered)

<!-- SEALED_BLOCK -->

## 7. What would change our mind

* If the mass-matched comparison shows an arm only wins because it emits more pixels, it is not a
  better detector.
* If the random-lineament control reaches the promoted arm's proxy score, the conjunction is
  decoration and H19-A must be withdrawn.
* If the state-map component turns out to be pure false-positive mass in the live A/B, H19-B is
  refuted for this competition and the next submission must drop it.

## 8. The prior register (this repository's pre-H19 shortlist)

The three hypotheses screened before this pass are kept verbatim in
[`hypotheses-h18.md`](hypotheses-h18.md) rather than deleted, because a register that only ever grows
forward is how a group ends up re-proposing its own ideas:

| ID | One-line mechanism | Status after this pass |
|---|---|---|
| **H18-N1** | multi-level paleolake shoreline displacement: same-sense offset of two independently correlated shoreline markers | screened, **conditional** — needs 3DEP 1 m DEM, which this sandbox cannot fetch (Audit A-08.3); not implemented |
| **H18-N2** | focal-mechanism fault-plane projection from reviewed moment tensors | screened, **conditional** — needs a ComCat event-quality audit inside the footprint; not implemented |
| **H18-N3** | Sentinel-1 InSAR displacement discontinuity | screened, **conditional** — needs Earthdata login and multi-date coherence work; not implemented |

None of the three is re-proposed as new in H19-A…E, and none was validated.
