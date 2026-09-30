# 18GEMSDOE — DOE GEMS Prize Challenge entry (repo 18)

> **Read this file at the start of every work session.** It is the standing mission
> brief for this repo. Nothing below is written from memory: every factual claim
> links to an official, verified source, collected in
> [`knowledge/sources_verified.md`](knowledge/sources_verified.md) and on the
> [References](docs/references.html) / [Data](docs/data.html) site pages.

## 1. Mission

Place at the top of the
[DOE GEMS Prize leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
(DrivenData competition 306, ends **Dec 3, 2026 23:59 UTC**, $300,000 prize pool)
by predicting **new, previously unmapped faults** in the GeoDAWN region of
northwestern Nevada / eastern California — not by re-fitting the known catalogue.

- Competition hub: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- Problem description (metric, format, structure):
  <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- About page (sponsor, data, task background):
  <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
- Official rules (PDF): <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>

## 2. Core values (binding on every decision)

- **Maximize P(Win).** In every decision, weigh tradeoffs, assess risk, and choose
  the path that maximizes the probability of winning. Set aside sunk cost and
  sentiment — including attachment to our own past submissions.
- **Own the Outcome.** We own results end to end: data verification, method
  soundness, format compliance, submission generation, and scored performance.
  When something is wrong (a duplicated payload, a broken citation, an
  unvalidated claim), we fix it without waiting for assignment.

## 3. Scientific discipline (binding on every hypothesis)

1. **Mechanism before resemblance.** State the specific physics that would make a
   signature indicate a fault (e.g. a normal fault juxtaposes rock of differing
   density/susceptibility, so Blakely & Simpson (1986) horizontal-gradient
   maxima and Miller & Singh (1994) tilt-derivative zero contours over RTP
   magnetics / isostatic gravity should peak over the fault's surface trace).
2. **Read the primary paper** behind every method before relying on it — never a
   half-remembered technique name. Verified citations live in
   [`docs/references.html`](docs/references.html).
3. **Name the confound.** For every candidate signature, name at least one
   specific non-fault process producing the same surface pattern (lithologic
   contact, playa/fan edge, road/canal/fence line, GeoDAWN Area 1 vs Area 2
   survey seam) and design the holdout test to distinguish the two. A test that
   can only confirm has told you nothing.
4. **Read the catalogue methodology, not just its raster.** Weight search density
   along-strike from known fault tips and inside known fault zones: staff
   confirmed on the record that "new fault" means "any fault pixel not already
   captured by USGS/INGENIOUS" and "can include newly mapped geometry of an
   existing fault system"
   ([forum 11536](https://community.drivendata.org/t/where-do-you-draw-the-line/11536)).
5. **Independent agreement is evidence.** A pixel where mechanistically
   independent layers agree (potential-field gradient + curvature break +
   strain/conductivity anomaly) is weighed as evidence — not blindly stacked
   into a blender.
6. **Pre-register, lock, and try to kill it.** Write the hypothesis and predicted
   direction *before* running; hold a locked slice of the holdout untouched
   until the end; count an improvement as real only if it survives the locked
   slice *and* your best attempt to explain it as artifact. That bar — not one
   promising run — earns a submission slot.
7. **No slot without a holdout win.** No idea spends one of the 3 rolling-weekly
   uploads until it beats the current holdout best under the locked protocol
   ([`knowledge/holdout_protocol.md`](knowledge/holdout_protocol.md)).

## 4. Standing facts (verified 2026-09-30; re-verify before relying)

| # | Fact | Source |
|---|------|--------|
| F1 | Metric is distance-weighted Tversky, α=0.2, β=0.8, triangular kernel R=300 m | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| F2 | Submission: single-band float32 GeoTIFF, EPSG:32611, 100 m, same bounds; values in [0,1]; outside = null/NaN | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| F3 | Known USGS/INGENIOUS fault pixels are **masked/excluded from scoring**, both rounds | [forum 11516 (staff)](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) |
| F4 | "New fault" = any fault pixel not already captured by USGS/INGENIOUS, incl. newly mapped geometry of existing systems | [forum 11536 (staff)](https://community.drivendata.org/t/where-do-you-draw-the-line/11536) |
| F5 | Organizers will **not** disclose test-fault data sources, fault types, or coverage | [forum 11527 (staff)](https://community.drivendata.org/t/how-were-the-new-test-faults-identified-data-sources-and-fault-types/11527/7) |
| F6 | Leaderboard top (2026-09-30 fetch): **0.3168** (DARD); group's best reported: **0.1855** (16GEMSDOE h16-1 file, linkage to account unverified) | [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) |
| F7 | The recurring **0.1563** = byte-identical payload reused across repos (sha `7f00890a…`, 172,974 px), not independent results | [8GEMSDOE duplicate audit](https://buffedlizard55-lab.github.io/8GEMSDOE/) + [16GEMSDOE](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html) |
| F8 | "Predicted values must be in range [0, 1]" = NaN **inside** the scored footprint (outside-footprint NaN is the official convention) | sibling-verified; re-validated by `scripts/validate_submission.py` in this repo |

See [`docs/audit.html`](docs/audit.html) for open flags (F08 multi-account
compliance question, unverified linkages, stale snapshots).

## 5. Repo map

```text
18GEMSDOE/
├── README.md                  ← you are here (standing brief)
├── docs/                      ← GitHub Pages site (enable Pages → /docs)
│   ├── index.html             ← overview + submission panel (honest status)
│   ├── executive_summary.html ← EXACT how-to-submit + error triage + naming
│   ├── hypotheses.html        ← 5 new candidates E1–E5, ranked, pre-registered
│   ├── strategy.html          ← metric math + what it implies for design
│   ├── results.html           ← group ledger + 0.1563 duplicate analysis
│   ├── data.html              ← data inventory, official links, obtainability
│   ├── references.html        ← primary-paper citations, all link-verified
│   └── audit.html             ← flags / irregularities for owner review
├── scripts/
│   ├── validate_submission.py ← 13-gate format checker (run before ANY upload)
│   ├── dti_metric.py          ← exact distance-weighted Tversky from the spec
│   └── README.md
├── knowledge/
│   ├── sources_verified.md    ← line-by-line verification log
│   └── holdout_protocol.md    ← locked validation protocol + E1 pre-registration
├── environment.yml
└── .gitignore
```

## 6. Current status (2026-09-30, this session)

- [x] Repo reviewed (was empty: single `Initial commit` + title README).
- [x] Official competition/method/data sources verified line by line with links.
- [x] 0.1563 duplication root-caused (same bytes, copied seed, repeated idea).
- [x] 5 new hypotheses (E1–E5) specified, ranked, pre-registered. **None validated.**
- [x] Rules PDF mined: 3 submissions/week (§3.2, §3.4), one final submission per entity (§3.4),
  generative-AI use must be disclosed in the finalist narrative (§3.2) — see flag F14.
- [x] Submission tooling scaffolded (validator + exact metric + how-to-submit).
- [ ] **BLOCKED — data placement.** Competition data requires a logged-in
  DrivenData download and is absent from this sandbox. No training, no holdout
  validation, and no submission raster can be honestly produced here until the
  owner places `training_features.tif`, labels, and the sample submission under
  `data/` (see `docs/data.html`). **No submission slot has been spent or is
  recommended by this repo.**
- [ ] E1 (Euler depth-gated lineaments) is the top candidate **to validate
  first** — validation is owed, not claimed.

## 7. Working agreement

- Work autonomously; no manual input required. Flag irregularities for review.
- No hallucinations: every factual claim carries a verifiable link; where
  evidence is missing, say so.
- Three passes before finishing: implement → review/fix → re-check against the
  original request.
- This session works on branch `arena/01a0f0a5-18gemsdoe` only.
