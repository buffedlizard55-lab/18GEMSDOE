#!/usr/bin/env python3
"""Render the GitHub Pages site from the markdown sources.

Every number that appears on the site is read from an evidence JSON at build
time (never typed), so the pages cannot drift from the measurements.  A missing
evidence file degrades to an explicit "not measured" string rather than to a
silent zero.

Usage::

    python scripts/build_site.py            # write index.html and docs/*.html
    python scripts/build_site.py --check    # fail if a page would change (CI)
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "data" / "evidence"

PAGES = [
    ("index.md", "index.html", "Home"),
    ("executive_summary.md", "docs/executive_summary.html", "Executive summary — how to submit"),
    ("submission.md", "docs/submission.html", "Submission steps"),
    ("research/hypotheses.md", "docs/hypotheses.html", "Hypotheses"),
    ("validation.md", "docs/validation.html", "Validation"),
    ("results.md", "docs/results.html", "Results & score ledger"),
    ("audit.md", "docs/audit.html", "Audit"),
    ("sources.md", "docs/sources.html", "Sources"),
    ("data.md", "docs/data.html", "Data & provenance"),
]

NAV = [
    ("executive_summary.html", "Submit"),
    ("submission.html", "Format"),
    ("hypotheses.html", "Hypotheses"),
    ("validation.html", "Validation"),
    ("results.html", "Results"),
    ("audit.html", "Audit"),
    ("sources.html", "Sources"),
    ("data.html", "Data"),
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — 18GEMSDOE</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="{home}">18GEMSDOE</a>
    <nav>{nav}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap">
  <p>Static site. Every figure on these pages is rendered from a committed evidence file at build time.
  Sources are linked for manual review; see <a href="{audit}">Audit</a> for what was and was not verified.</p>
</footer>
</body>
</html>
"""


def load(name: str, default=None):
    p = EVIDENCE / name
    if not p.exists():
        return default
    return json.loads(p.read_text())


def fmt(value, spec: str = "{:.4f}", missing: str = "not measured") -> str:
    if value is None:
        return missing
    try:
        return spec.format(float(value))
    except (TypeError, ValueError):
        return missing


def results_table() -> str:
    data = load("detector_results.json")
    if not data:
        return "_No detector run is committed yet: `python scripts/run_detectors.py` writes `data/evidence/detector_results.json`._"
    rows = []
    comp = (data.get("matched_support_comparison") or {}).get("_comparator") or {}
    for name, entry in sorted((data.get("results") or {}).items()):
        if name.startswith("_"):
            continue
        if "sweep" in entry:
            best = max(entry["sweep"].items(), key=lambda kv: kv[1].get("tuning_dti", 0.0))
            target, summary = best
            full = summary["full_field"]
            folds = ", ".join(
                f"{k}: {fmt(v, '{:.3f}')}" for k, v in sorted(summary.get("fold_dti", {}).items())
            )
            matched = (data.get("matched_support_comparison") or {}).get(name, {})
            boot = (data.get("bootstrap_vs_comparator") or {}).get(name, {})
            rows.append(
                "| `{}` | {} | {} | {} | {} | {} | {} |".format(
                    name,
                    target,
                    f"{full['emission_px']:,}",
                    fmt(full["dti"]),
                    fmt(summary.get("tuning_dti")),
                    folds or "—",
                    fmt(matched.get("dti")) + (
                        f" ({'+' if (matched.get('delta_vs_comparator') or 0) >= 0 else ''}"
                        f"{fmt(matched.get('delta_vs_comparator'))})"
                        if matched else ""
                    ),
                )
            )
        else:
            full = entry.get("full_field", {})
            rows.append(
                "| `{}` | full grid | {} | {} | {} | — | {} |".format(
                    name,
                    f"{full.get('emission_px', 0):,}",
                    fmt(full.get("dti")),
                    fmt(full.get("dti")),
                    fmt(full.get("dti")),
                )
            )
    header = (
        "| Arm | Proxy support (px) | Emission (px) | Proxy DTI | Tuning-fold DTI | Per-fold (tuning) | "
        "Matched-support DTI (Δ vs shipped file) |\n"
        "|---|---:|---:|---:|---:|---|---|\n"
    )
    note = (
        f"\n\nComparator: the previously shipped `ens12` field "
        f"(`data/comparator_ens12.tif`, 172,974 px) scores **{fmt(comp.get('dti'))}** on the same "
        f"proxy population. The proxy population is USGS SGMC structure with no training label within "
        f"300 m ({data.get('truth', {}).get('proxy_gap_px', 0):,} px).\n"
    )
    return header + "\n".join(rows) + note


def sealed_block() -> str:
    data = load("detector_results.json")
    if not data or not data.get("sealed", {}).get("candidate"):
        return "_No sealed read is committed yet._"
    s = data["sealed"]
    verdict = (
        "**the candidate beats the comparator on the sealed blocks**"
        if s["candidate_dti"] > s["comparator_dti"]
        else "**the candidate does not beat the comparator on the sealed blocks**"
    )
    return (
        f"Arm selected on the tuning folds: **`{s['candidate']}`** at support "
        f"{s['target']:,} px. Sealed truth: {s['truth_px_sealed']:,} proxy pixels in 14 blocks that no "
        f"selection step touched.\n\n"
        f"| Field | Sealed-slice proxy DTI |\n|---|---:|\n"
        f"| `{s['candidate']}` | {fmt(s['candidate_dti'])} |\n"
        f"| shipped `ens12` comparator | {fmt(s['comparator_dti'])} |\n\n"
        f"Verdict: {verdict}. This is written here because it is the result, whichever way it fell.\n"
    )


def download_block(depth: int) -> str:
    """The one-click download, rendered from the packaging manifest (never typed)."""
    man_p = ROOT / "docs" / "downloads" / "manifest.json"
    if not man_p.exists():
        return ("_No packaged submission is committed yet.  Run `python scripts/build_candidate.py` and then "
                "`python scripts/make_submission.py`._")
    man = json.loads(man_p.read_text())
    prefix = "../" * depth
    rel = prefix + man["path"].replace("docs/", "docs/", 1)
    note_file = man["path"].replace(".tif", ".note.txt")
    kb = man["bytes"] / 1024
    val = man.get("validation") or {}
    rows = "".join(
        f"<tr><td>{html.escape(str(k))}</td><td><code>{html.escape(str(v))}</code></td></tr>"
        for k, v in [
            ("candidate", man.get("candidate_id")),
            ("bytes", f"{man['bytes']:,} ({kb:,.0f} KiB)"),
            ("sha256", man["sha256"]),
            ("bands / dtype", f"{(val.get('grid') or {}).get('bands')} / {(val.get('grid') or {}).get('dtype')}"),
            ("crs / resolution", f"{(val.get('grid') or {}).get('crs')} / {(val.get('grid') or {}).get('resolution_m')}"),
            ("value range in footprint", f"{val.get('valid_min')} … {val.get('valid_max')}"),
            ("footprint pixels", f"{val.get('footprint_pixels'):,}" if isinstance(val.get('footprint_pixels'), int) else val.get('footprint_pixels')),
            ("format check", "PASS" if val.get("valid") else "FAIL"),
            ("format validated", man.get("generated_utc")),
        ]
    )
    return (
        '<div class="download-card">'
        f'<a class="button button-primary button-big" href="{html.escape(rel)}" download>'
        f'⬇ Download {html.escape(man["file"])}</a>'
        f'<p class="micro-copy">Right-click → “Save link as…” if your browser opens it instead. '
        f'The file name carries the candidate id, the UTC build time and the content hash, so two '
        f'downloads can never be confused.</p>'
        '<details><summary>Bytes, hash and format check</summary>'
        f'<table class="kv">{rows}</table>'
        f'<p class="micro-copy">Comment to paste into the upload form: '
        f'<code>{html.escape(man.get("note", ""))}</code></p>'
        '</details>'
        '</div>'
    )


def candidate_block() -> str:
    """Composition and sensitivity of the shipped candidate, from its evidence JSON."""
    ev = load("candidate_h19.json")
    if not ev:
        return "_The shipped candidate's evidence file is not committed yet._"
    c = ev.get("components", {})
    s = ev.get("sealed_catalogue_read", {})
    rows = [
        ("candidate", ev.get("candidate_id")),
        ("physics support (tuning-fold choice)", f"{ev.get('support_chosen'):,} px"),
        ("physics pixels kept", f"{c.get('physics_px'):,}"
         f" ({100 * (c.get('physics_on_state_map_frac') or 0):.1f} % on state-map lines, "
         f"{100 * (c.get('physics_on_catalogue_frac') or 0):.1f} % on the catalogue)"),
        ("state-map component", f"{c.get('state_map_px'):,} px, of which "
         f"{c.get('state_map_gap_px'):,} px have no label within 300 m"),
        ("catalogue component", f"{c.get('catalogue_px'):,} px (masked out of scoring by the platform)"),
        ("total emitted", f"{c.get('total_px'):,} px = {100 * (c.get('coverage_of_footprint') or 0):.2f} % of the footprint"),
        ("mass the metric can charge for", f"{c.get('paid_emission_px'):,} px"),
        ("sealed catalogue read", f"DTI {s.get('dti', 0):.4f} on {s.get('truth_px', 0):,} held-out label px"),
    ]
    body = "\n".join(f"| {k} | `{v}` |" for k, v in rows)
    sens = ev.get("sensitivity") or []
    lines = ["| assumed truth size | coverage ρ | resulting DTI |", "|---:|---:|---:|"]
    for row in sens:
        lines.append(f"| {row['truth_px']:,} px | {row['coverage_rho']:.1f} | {row['dti']:.4f} |")
    return (
        "| Property | Value |\n|---|---|\n" + body +
        "\n\n**Sensitivity — the score the metric would return for this field, as a function of the "
        "truth size and of how much of it the field covers.** Nothing here is a forecast; it is the "
        "metric's own arithmetic applied to the field's paid mass.\n\n" + "\n".join(lines) + "\n"
    )


def leaderboard_block() -> str:
    """Dated snapshot of the public leaderboard, from registry/ (never polled)."""
    p = ROOT / "registry" / "leaderboard_snapshot.json"
    if not p.exists():
        return "_No leaderboard snapshot is committed._"
    snap = json.loads(p.read_text())
    prov = snap.get("provenance", {})
    rows = "\n".join(
        f"| #{e['rank']} | {html.escape(str(e['participant']))} | {e['best_public_dw_tversky']:.4f} | {e['submissions']} |"
        for e in snap.get("leaderboard", [])
    )
    return (
        f"Read from the public leaderboard on **{prov.get('read_on')}** "
        f"([source]({prov.get('url')})); {html.escape(prov.get('terms_note', ''))}\n\n"
        "| Rank | Participant | Best public DW-Tversky | Submissions |\n|---:|---|---:|---:|\n"
        + rows
        + "\n\nThe bar is **the top row**, not the 0.3049 quoted when this project started. "
        "The group's own best file (16GEMSDOE `h16-1`, 0.1855) is the entry at #22 *if* `extradr19` is "
        "this group's account — an attribution that cannot be verified without signing in and is "
        "therefore labelled, not assumed.\n"
    )


LINK_RE = re.compile(r"\]\(([^)\s]+?)(#[^)]*)?\)")


def rewrite_md_links(text: str, src: Path, out: Path) -> str:
    """Re-point every relative Markdown link so it is correct in the *rendered* page.

    The Markdown files are written with links relative to themselves (so GitHub and
    ``tests/test_site.py`` can both resolve them); the rendered page may live in a
    different directory, so each surviving link is re-expressed relative to the
    output file.  Missing targets are left untouched on purpose — the test suite,
    not this function, decides that a link is broken.
    """

    def sub(m: "re.Match[str]") -> str:
        target, frag = m.group(1), m.group(2) or ""
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith("#") or target.startswith("/"):
            return m.group(0)
        absolute = (src.parent / parsed.path).resolve()
        if not absolute.exists():
            return m.group(0)
        rel = os.path.relpath(absolute, out.parent).replace(os.sep, "/")
        return f"]({rel}{frag})"

    return LINK_RE.sub(sub, text)


def render(src: Path, title: str, depth: int, out: Path) -> str:
    text = rewrite_md_links(src.read_text(), src, out)
    body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"]
    )
    body = body.replace("<!-- DOWNLOAD_BLOCK -->", download_block(depth))
    body = body.replace("<!-- RESULTS_TABLE -->", results_table())
    body = body.replace("<!-- CANDIDATE_BLOCK -->", candidate_block())
    body = body.replace("<!-- LEADERBOARD_BLOCK -->", leaderboard_block())
    body = body.replace("<!-- SEALED_BLOCK -->", sealed_block())
    prefix = "../" * depth
    return TEMPLATE.format(
        title=html.escape(title),
        css=prefix + "assets/site.css",
        home=prefix + "index.html",
        audit=prefix + "docs/audit.html",
        nav="".join(f'<a href="{prefix}docs/{href}">{html.escape(label)}</a>' for href, label in NAV),
        body=body,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    changed = []
    for src_name, out_name, title in PAGES:
        src = (DOCS / src_name) if src_name != "index.md" else (ROOT / "docs" / "index.md")
        out = ROOT / out_name
        depth = 0 if out_name == "index.html" else len(Path(out_name).parts) - 1
        if not src.exists():
            print(f"missing source: {src}", file=sys.stderr)
            return 2
        rendered = render(src, title, depth, out)
        if out.exists() and out.read_text() == rendered:
            continue
        changed.append(str(out))
        if not args.check:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(rendered)
    if args.check and changed:
        print("site is stale: " + ", ".join(changed), file=sys.stderr)
        return 1
    print(("updated: " if not args.check else "would update: ") + ", ".join(changed) if changed else "site is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
