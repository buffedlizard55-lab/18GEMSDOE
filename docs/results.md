# Results — the board, the group's history, and why four entries were one file

## 1. The live board (dated manual snapshot)

<!-- LEADERBOARD_BLOCK -->

## 2. The group's own history

| File (as reported to this project) | Public score | Emission | Note |
|---|---:|---:|---|
| `GEMSDOE1` / `5GEMSDOE` — `ens12-adopted-floor0.1-w0` | 0.1563 | 172,974 px | **byte-identical files** — SHA-256 `7f00890a…`, recomputed here |
| `8GEMSDOE` — `max(ens12, catalogue)` | 0.1563 | 172,974 px | same scored content; adding the catalogue changed nothing, exactly as the pixel-exact mask predicts |
| `GEMSDOE2` — dual-family union | 0.1560 | 175,949 px | overlap with `ens12` Jaccard ≈ 0.95 |
| `7GEMSDOE` — lidar scarp ridge, top 2 % | 0.1461 | 76,859 px | none of its emission is on known faults |
| `12GEMSDOE` — `r7-nms3-dem10-scarp` | 0.1294 | 103,347 px | the group's highest SGMC-gap proxy score — and one of its lowest public scores |
| `GEMSDOE3` — nodes / catalogue-gap / dense-ridge control | 0.1193 / 0.0830 / 0.1152 | point-like | three distinct fields |
| `16GEMSDOE` — H16-1 topo-geophys baseline ridges | **0.1855** | 123,939 px | the group's best; sits at leaderboard #22 if `extradr19` is the group's account |
| `6GEMSDOE`, `11GEMSDOE`, `GEMSDOE9`, `14GEMSDOE` | 0.0286, 0.0202, 0.0107, 0.0020 | — | catalogue-adjacent top-k and failed arms |

**[INFERENCE]** Two regimes are visible: thin line networks over real structures land at 0.12–0.19;
emissions that sit on or beside the catalogue collapse to ≤0.05. Nothing in the group's history
exceeds 0.19, and four of the entries are one prediction.

## 3. Why the repeat happened

**[VERIFIED-HERE]** One byte sequence (`7f00890a…`, 570,890 B, a hard 0/1 mask, 172,974 positive
pixels) is committed as the submission in more than one repository; **[GROUP-REPORTED]** the same
scored content appears at eight paths across six repositories. Repositories were seeded from earlier
repositories' evidence folders, whose default `submission.tif` *is* `ens12` — so uploading "the
submission" again produced the same score and taught nobody anything. This repository's packager
therefore refuses any hash it has already offered (`registry/submission-hashes.json`).

## 4. What the metric rewards (measured, not asserted)

`DTI = TP_w / (0.2·M + 0.8·|G|)` with `M` the emitted mass. Consequences:

* each emitted pixel the metric can charge for costs **0.2** of the denominator; each newly covered
  truth pixel returns up to **0.8** — false positives are cheap, misses are 4× dearer;
* raising all values toward 1 can only help (the `0.8·|G|` term is fixed), so a field should be
  emitted at uniform 1, not shaded;
* therefore a one-pixel-wide line on a true structure beats a broad anomaly of the same recall, and a
  candidate population is worth adding whenever more than ≈ 3–6 % of its pixels sit within 300 m of a
  truth pixel.

The sensitivity table on the [Validation](validation.html) page applies that arithmetic to the shipped
field's actual paid mass, for assumed truth sizes from 30,000 to 240,000 pixels.

## 5. Score ledger

`registry/score-ledger.csv` is the machine-readable record (date, scope, participant, rank, score,
evidence class, source, note). Rules: an **official** row requires a signed-in read and records the
account; a **group-reported** row records the repository and file hash; a **proxy** row is never
written as a leaderboard score.
