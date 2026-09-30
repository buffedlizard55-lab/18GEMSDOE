# 18GEMSDOE — download the submission, see the evidence

<div class="hero">
<strong>One click to a competition-ready file.</strong> The GeoTIFF below is a single-band float32
raster in the official submission format (EPSG:32611, 100 m, template bounds, finite values in [0, 1]
inside the footprint, NaN outside) and has passed the format validator against the official template.
Nothing is generated or uploaded in your browser.
</div>

<!-- DOWNLOAD_BLOCK -->

## Up to date, without anyone checking by hand

<!-- LEADERBOARD_BLOCK -->

## What you are downloading

A **candidate fault map (H19-C)** built from three components, each published with its size:

1. **The training catalogue** — the platform masks exactly these pixels out of scoring, so including
   them is free and makes the file a complete map rather than a partial one.
2. **State geologic map structure lines that the catalogue does not contain** (61,664 px with no
   training label within 300 m) — a *population* bet: if the experts' new faults are structures the
   state maps carry and the Quaternary catalogue does not, this is where they are.
3. **Multi-physics conjunction lineaments** — pixels where at least two of magnetics, gravity and
   topography have a ridge at the same place, thinned to one pixel.

The physics and the risk are on [the hypotheses page](hypotheses.html); the controls, the locked
holdout and the sealed read are on [the validation page](validation.html).

## Why this exists — the findings that changed the strategy

1. **The repeated 0.1563 is one file in several repositories.** `GEMSDOE` and `5GEMSDOE` commit
   byte-identical submissions (SHA-256 `7f00890a…`, 570,890 B) — recomputed here, not quoted.
   [Audit A-01](audit.html).
2. **Known-fault pixels are masked pixel-exactly, with no buffer**, so the catalogue is free to paint
   and the whole game is the *new* pixels — an arithmetic fact, not a hunch. [Sources S4](sources.html).
3. **The labels are the USGS QFaults network inside the footprint** (71,984 of 71,985 QFaults pixels
   inside the valid footprint lie within 300 m of a label), which says exactly what the scored truth
   is *not*. [Data §2](data.html).
4. **The metric's own algebra** reduces to `DTI = TP_w / (0.2·M + 0.8·|G|)`, so an emitted pixel costs
   0.2 and a newly covered truth pixel earns up to 0.8: sparse, thin, confident is arithmetic, not taste.

## Where to go next

| Page | What it answers |
|---|---|
| [Executive summary](executive_summary.html) | the file, the format requirements, the click-by-click upload path and the `[0, 1]` error triage |
| [Validation](validation.html) | the locked holdout, the arms, the controls, the sealed read — including what failed |
| [Hypotheses](hypotheses.html) | five candidates with mechanism, non-fault look-alikes, falsification tests and ranking |
| [Results](results.html) | the group's score history, the duplicate analysis, the leaderboard context |
| [Audit](audit.html) | irregularities, what was verified here, what was checked and abandoned |
| [Sources](sources.html) | every claim with its official link, for manual review |
| [Data](data.html) | the official rasters, their SHA-256 pins, and which release layers the stack omits |

## Honest status

No candidate has passed the locked-holdout review: the multi-physics conjunction beats its matched
random-lineament control on the tuning folds, but at the shipped file's own emitted mass it is only
marginally ahead of that control, and the arm the tuning folds promote loses on the sealed slice
(0.0003 vs 0.0085). The download is therefore published as a candidate, not as a validated winner,
and no verified model prediction beyond that is claimed anywhere on this site.

The shipped field is a **candidate**. Its physics component beats a matched random-lineament control
on the tuning folds; its state-map component **cannot be validated from here at all**, and that is
stated on the file's own page rather than buried. No leaderboard score is claimed for it, and no
submission is made automatically: this site prepares and validates the file, the team uploads it and
records the result in `registry/score-ledger.csv`.
