# Results — the board, the group's history, and why four entries were one file

## 1. The live board (dated manual snapshot)

<!-- LEADERBOARD_BLOCK -->

## 2. The group's own history

The numbers below are **[GROUP-REPORTED]** public scores, read from the group's own similarity audit
(`16GEMSDOE/evidence/submission_similarity.json`, 21 entries, generated 2026-09-30T01:14Z) which pins
each file's bytes and counts its pixels. Emission is "positive pixels in the file / positive pixels
that the pixel-exact known-fault mask leaves in the score".

| File | Public score | Emission (all / scored px) | Note |
|---|---:|---:|---|
| `GEMSDOE1` — `ens12-adopted-floor0.1-w0` | 0.1563 | 172,974 / 166,519 | reference file; SHA-256 `7f00890a…`, 570,890 B |
| `5GEMSDOE` — same name | 0.1563 | 172,974 / 166,519 | **exact byte duplicate of the row above** |
| `8GEMSDOE` — `Hedge-v2 = max(ens12, catalogue)` | 0.1563 | 227,507 / 166,519 | the extra 60,988 px are the catalogue, all masked → score unchanged |
| `GEMSDOE2` — dual-family union | 0.1560 | 183,642 / 175,949 | Jaccard ≈ 0.95 with `ens12` |
| `7GEMSDOE` — lidar scarp ridge, top 2 % | 0.1461 | 76,859 / 76,859 | none of its emission is on known faults |
| `12GEMSDOE` — `r7-nms3-dem10-scarp` | 0.1294 | 103,347 / 103,347 | the group's highest SGMC-gap proxy score — and one of its lowest public scores |
| `GEMSDOE3` — `pindrop-v4-nodes` | 0.1193 | 155,021 / 155,021 | point-like emission |
| `GEMSDOE3` — `pindrop-v4-ridge` (control) | 0.1152 | 155,021 / 155,021 | same mass, different geometry |
| `GEMSDOE10-H20` | 0.0921 | 153,957 / 143,657 | |
| `GEMSDOE3` — `pindrop-v4-discovery` | 0.0830 | 155,021 / 155,021 | |
| `15GEMSDOE` | 0.0782 | 99,999 / 98,736 | |
| `GEMSDOE10-H16` | 0.0461 | 310,042 / 283,532 | |
| `GEMSDOE4` — combined | 0.0343 | 264,247 / 258,323 | thick union blob |
| `6GEMSDOE` — `hgb88-topk03` | 0.0286 | 155,021 / 131,416 | catalogue-adjacent |
| `11GEMSDOE` — structural area 06 | 0.0202 | 343,526 / 282,538 | near-catalogue |
| `GEMSDOE9` — placeholder | 0.0107 | 147,684 / 145,610 | |
| `14GEMSDOE` — `r5-geom-horse-ensemble` | 0.0020 | 116,225 / 116,219 | |
| `16GEMSDOE` — `h16-1-topo-geophys-baseline-ridges` | 0.1855 | *not in the audit's 21 entries* | the group's best; reported to this project, and the leaderboard's #22 entry is 0.1855 under `extradr19` |

**[INFERENCE]** Two regimes are visible: thin line networks over real structures land at 0.12–0.19;
emissions that sit on or beside the catalogue collapse to ≤0.05. Nothing in the group's history exceeds
0.19, and four of the entries are one prediction.

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
