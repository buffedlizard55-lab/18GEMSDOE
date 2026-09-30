#!/usr/bin/env python3
"""Validate a GEMS submission GeoTIFF against the official template."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gems18.submission import validate_geotiff  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", help="single-band candidate GeoTIFF")
    parser.add_argument("--template", required=True, help="official sample-submission/template GeoTIFF")
    parser.add_argument("--footprint", help="optional one-band valid-footprint mask on the template grid")
    args = parser.parse_args()

    result = validate_geotiff(args.submission, args.template, args.footprint)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
