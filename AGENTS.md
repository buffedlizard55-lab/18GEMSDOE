# Instructions for future agents

1. Read `README.md` first on every session, then inspect the current files and `git status`.
2. Work only on `arena/01a0f380-18gemsdoe`; do not switch branches. The project is a research-and-submission workflow, not permission to submit on the user's behalf.
3. Before proposing a geological idea, compare it with the public `8GEMSDOE` and `16GEMSDOE` registers linked in `docs/research/hypotheses.md`. State whether the idea is new, adjacent, previously proposed, tested, or already failed. Do not rebrand H18-5 thermal anchoring or any other prior proposal as novel.
4. Use direct official sources for science, format, licensing, data coverage, and competition rules. Label group repository results as group-reported unless this checkout independently reproduces them. Never call a proxy score a leaderboard score.
5. Do not tune against a sealed spatial holdout. No submission artifact may be released until the preregistration, provenance, holdout gate, independent controls, uniqueness check, and GeoTIFF validator pass. If data are unavailable or provenance is unresolved, stop and record the blocker.
6. Do not scrape, poll, iframe, or automatically monitor DrivenData. Its Terms of Use prohibit automated site access. Link to the official page; update only through a dated manual snapshot unless written permission is obtained.
7. Keep raw data, credentials, and generated large artifacts out of Git. Run `.venv/bin/python -m pytest -q`, `npm test`, and `npm run build`; update the evidence/score ledgers and audit, and disclose limitations before opening a PR.
8. The browser builder packages a user-supplied prediction raster only; it is not a model or upload client. Its holdout-evidence booleans require independent reviewer verification. Never present a format-only pass as scientific validation.
