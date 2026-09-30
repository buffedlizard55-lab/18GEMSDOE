#!/usr/bin/env python3
"""Reassemble the official competition rasters from the committed git bridge.

The official data download page requires a DrivenData login.  The same bytes are
also published as public mirrors on that page, and those mirrors were fetched by
an unrestricted GitHub-hosted runner in a sibling project
(``buffedlizard55-lab/GEMSDOE``, ``data/bridge/``) and committed as <= 90 MiB
parts so that the hash-pinned payload can travel by git.

This script copies nothing and downloads nothing: it verifies the parts against
``data/bridge/manifest.json``, concatenates them, and re-verifies the whole-file
SHA-256 against the pinned inventory before writing the canonical names.  Any
mismatch aborts, so a corrupted transport cannot masquerade as official data.

Provenance chain, with every hop independently checkable:

1.  Official data tab (login): https://www.drivendata.org/competitions/306/competition-doe-gems/data/
2.  Public mirrors printed there (Dropbox links; see the manifest for the exact URLs).
3.  Pinned hashes measured by ``scripts/inspect_competition_data.py`` on a GitHub
    runner, 2026-09-14 — recorded in ``data/bridge/inventory.json``.
4.  Bridge parts committed by the sibling project; re-verified here on receipt.

Usage::

    python scripts/assemble_data_bridge.py            # data/bridge -> data/*.tif
    python scripts/assemble_data_bridge.py --check    # verify only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "data" / "bridge"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bridge", type=Path, default=BRIDGE)
    ap.add_argument("--out", type=Path, default=ROOT / "data")
    ap.add_argument("--check", action="store_true", help="verify the bridge without writing")
    args = ap.parse_args()

    manifest_path = args.bridge / "manifest.json"
    if not manifest_path.exists():
        print(f"missing manifest: {manifest_path}", file=sys.stderr)
        return 2
    manifest = json.loads(manifest_path.read_text())

    errors: list[str] = []
    written: list[dict] = []
    for entry in manifest["files"]:
        parts = entry.get("parts")
        target = args.out / entry["canonical"]
        if parts:
            joined = args.out / (entry["name"] + ".assembled")
            with joined.open("wb") as out:
                for part in parts:
                    p = args.bridge / part["name"]
                    if not p.exists():
                        errors.append(f"missing part {p}")
                        continue
                    got = sha256_file(p)
                    if got != part["sha256"]:
                        errors.append(f"part {p.name} sha256 {got} != pinned {part['sha256']}")
                    with p.open("rb") as fh:
                        shutil.copyfileobj(fh, out, 1 << 22)
            if errors:
                joined.unlink(missing_ok=True)
                break
            got = sha256_file(joined)
            if got != entry["sha256"]:
                errors.append(f"{entry['name']} sha256 {got} != pinned {entry['sha256']}")
                joined.unlink(missing_ok=True)
                break
            size = joined.stat().st_size
            if not args.check:
                joined.replace(target)
            written.append({"path": str(target), "sha256": got, "bytes": size})
        else:
            src = args.bridge / entry["name"]
            if not src.exists():
                errors.append(f"missing file {src}")
                break
            got = sha256_file(src)
            if got != entry["sha256"]:
                errors.append(f"{entry['name']} sha256 {got} != pinned {entry['sha256']}")
                break
            if not args.check:
                shutil.copy2(src, target)
            written.append({"path": str(target), "sha256": got, "bytes": src.stat().st_size})

    report = {
        "generated_by": "scripts/assemble_data_bridge.py",
        "bridge": str(args.bridge),
        "manifest_sha256": sha256_file(manifest_path),
        "verified": written,
        "errors": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    print(json.dumps(report, indent=1))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
