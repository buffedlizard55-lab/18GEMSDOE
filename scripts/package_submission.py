#!/usr/bin/env python3
"""Create a uniquely named GEMS GeoTIFF after the spatial holdout gate passes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gems18.submission import SubmissionError, package_submission  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prediction", required=True, help="single-band probability raster on the official grid")
    parser.add_argument("--template", required=True, help="official sample-submission/template GeoTIFF")
    parser.add_argument("--evidence", required=True, help="committed passing spatial-holdout evidence JSON")
    parser.add_argument("--candidate-id", required=True, help="pre-registered hypothesis identifier")
    parser.add_argument("--output-dir", default="build", help="output folder (default: build/, gitignored)")
    parser.add_argument("--footprint", help="optional one-band scored-footprint mask on the template grid")
    args = parser.parse_args()

    try:
        result = package_submission(
            args.prediction,
            args.template,
            args.evidence,
            args.candidate_id,
            args.output_dir,
            footprint_path=args.footprint,
        )
    except (SubmissionError, RuntimeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    printable = {key: str(value) if isinstance(value, Path) else value for key, value in result.items()}
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
