from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("href"):
            self.links.append(attrs["href"])
        if attrs.get("id"):
            self.ids.add(attrs["id"])


def test_all_local_html_navigation_targets_and_fragments_exist():
    pages = list(ROOT.rglob("*.html"))
    assert pages, "site pages were not created"
    page_ids = {}
    parsed_pages = {}
    for page in pages:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        parsed_pages[page] = parser
        page_ids[page.resolve()] = parser.ids

    for page, parser in parsed_pages.items():
        for href in parser.links:
            parsed = urlsplit(href)
            if parsed.scheme in {"https", "http", "mailto", "tel"}:
                continue
            target_path = parsed.path or page.name
            target = (page.parent / target_path).resolve()
            assert target.exists(), f"missing local link target in {page.relative_to(ROOT)}: {href}"
            if parsed.fragment and target.suffix == ".html":
                assert parsed.fragment in page_ids.get(target, set()), f"missing fragment #{parsed.fragment} in {target.relative_to(ROOT)}"


def test_markdown_internal_links_and_explicit_fragments_exist():
    for page in [ROOT / "README.md", *(ROOT / "docs").rglob("*.md")]:
        text = page.read_text(encoding="utf-8")
        for target_ref in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            parsed = urlsplit(target_ref)
            if parsed.scheme in {"https", "http", "mailto", "tel"}:
                continue
            target_path = parsed.path or page.name
            target = (page.parent / target_path).resolve()
            assert target.exists(), f"missing Markdown link target in {page.relative_to(ROOT)}: {target_ref}"
            if parsed.fragment and target.suffix == ".md":
                target_text = target.read_text(encoding="utf-8").lower()
                fragment = parsed.fragment.lower()
                assert f'id="{fragment}"' in target_text or f"id='{fragment}'" in target_text, f"missing Markdown fragment #{fragment} in {target.relative_to(ROOT)}"


def test_site_does_not_embed_or_automate_drivendata():
    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8").lower()
        assert "<iframe" not in text, page
        assert "setinterval(" not in text, page
    for script in (ROOT / "assets" / "js").glob("*.js"):
        if script.name == "submission-builder.bundle.js":
            # geotiff.js contains unused URL-source support, but the UI only passes local File/Blob objects.
            continue
        text = script.read_text(encoding="utf-8").lower()
        assert "fetch(" not in text, script
        assert "setinterval(" not in text, script


def test_release_status_is_explicit_and_builder_disclaims_prediction_generation():
    index = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    submission = (ROOT / "docs" / "submission.html").read_text(encoding="utf-8").lower()
    assert "no candidate has passed the locked-holdout review" in index
    assert "no verified model prediction" in index
    assert "does not generate fault predictions" in submission
    assert "do not submit from this repository" in submission
