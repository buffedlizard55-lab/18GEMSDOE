#!/usr/bin/env python3
"""Package a validated prediction as the site's one-click download.

Steps, in order, and the script stops at the first failure:

1.  validate the raster against the official template (grid, CRS, dtype, range);
2.  refuse a file whose content hash is already registered (the group's failure mode
    was shipping the same bytes from several repositories);
3.  copy it into ``docs/downloads/`` under a unique name carrying the candidate id,
    the UTC time and the content hash;
4.  write a sidecar note (ready to paste into the submission comment field) and a
    machine-readable manifest that the site builder renders.

Usage::

    python scripts/make_submission.py \
        --prediction data/submission_h19.tif \
        --template data/sample_submission.tif \
        --candidate-id H19-A-conjunction \
        --arm conjunction --evidence data/evidence/detector_results.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gems18.submission import validate_geotiff  # noqa: E402

REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def known_hashes() -> dict[str, str]:
    """Every hash this project has already offered, plus the group's registered files."""
    out: dict[str, str] = {}
    ledger = REGISTRY / "submission-hashes.json"
    if ledger.exists():
        out.update(json.loads(ledger.read_text()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prediction", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--candidate-id", required=True)
    ap.add_argument("--arm", default=None)
    ap.add_argument("--note", default=None)
    ap.add_argument("--evidence", default=None, type=Path)
    ap.add_argument("--allow-duplicate", action="store_true")
    args = ap.parse_args()

    for p in (args.prediction, args.template):
        if not p.exists():
            print(f"missing file: {p}", file=sys.stderr)
            return 2

    result = validate_geotiff(args.prediction, args.template)
    print(json.dumps({k: v for k, v in result.items() if k != "sample_rows"}, indent=1)[:2000])
    if not result.get("valid"):
        print("validation FAILED — not packaging", file=sys.stderr)
        return 1

    digest = sha256_file(args.prediction)
    registry = known_hashes()
    if digest in registry and not args.allow_duplicate:
        print(
            f"refusing: these bytes are already registered as {registry[digest]!r} "
            f"(sha256 {digest}); a duplicate submission spends a slot and measures nothing",
            file=sys.stderr,
        )
        return 3

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"18GEMSDOE_{args.candidate_id}_{stamp}_{digest[:8]}.tif"
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    target = DOWNLOADS / name
    shutil.copy2(args.prediction, target)

    note = args.note or (
        f"18GEMSDOE {args.candidate_id} | H19-A multi-physics conjunction lineaments "
        f"(magnetics x gravity x topography, >=2 families, 1-px thin) | holdout "
        f"41332369d7dd448b | sha256 {digest[:16]}"
    )
    (DOWNLOADS / (name.replace(".tif", ".note.txt"))).write_text(note + "\n")

    manifest = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file": name,
        "path": f"docs/downloads/{name}",
        "bytes": target.stat().st_size,
        "sha256": digest,
        "candidate_id": args.candidate_id,
        "arm": args.arm,
        "note": note,
        "validation": result,
        "evidence": str(args.evidence) if args.evidence else None,
        "evidence_sha256": sha256_file(args.evidence) if args.evidence and args.evidence.exists() else None,
    }
    (DOWNLOADS / "manifest.json").write_text(json.dumps(manifest, indent=1, default=str))

    registry[digest] = name
    (REGISTRY / "submission-hashes.json").write_text(json.dumps(registry, indent=1, sort_keys=True))
    print(f"packaged {target} ({manifest['bytes']} bytes, sha256 {digest[:16]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
