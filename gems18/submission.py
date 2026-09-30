"""GeoTIFF validation and gated packaging for the GEMS Prize."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gates import validate_release_evidence


class SubmissionError(ValueError):
    """Raised when a GeoTIFF is invalid or cannot be safely packaged."""


def _geo_imports():
    try:
        import numpy as np
        import rasterio
    except ImportError as exc:  # pragma: no cover - environment-specific message
        raise RuntimeError("Install requirements.txt to use GeoTIFF tools: python -m pip install -r requirements.txt") from exc
    return np, rasterio


def _same_grid(reference: Any, candidate: Any, label: str, errors: list[str]) -> None:
    if candidate.width != reference.width or candidate.height != reference.height:
        errors.append(f"{label}: width/height do not match the template")
    if candidate.crs != reference.crs:
        errors.append(f"{label}: CRS does not match the template")
    if candidate.transform != reference.transform:
        errors.append(f"{label}: affine transform does not match the template")


def _validate_reference(reference: Any, errors: list[str]) -> None:
    if reference.count < 1:
        errors.append("template has no raster band")
    if reference.crs is None or reference.crs.to_epsg() != 32611:
        errors.append("template CRS must be EPSG:32611")
    transform = reference.transform
    if transform.b != 0 or transform.d != 0 or abs(transform.a) != 100 or abs(transform.e) != 100:
        errors.append("template must be an unrotated 100 m grid")


def validate_geotiff(
    submission_path: str | Path,
    template_path: str | Path,
    footprint_path: str | Path | None = None,
) -> dict[str, Any]:
    """Check a submission against the official template and footprint mask.

    Outside-footprint values are accepted only when NaN/non-finite or explicitly
    masked by the GeoTIFF mask/nodata metadata. No clipping, scaling, warping, or
    dtype conversion occurs in this validator.
    """
    np, rasterio = _geo_imports()
    errors: list[str] = []
    warnings: list[str] = []
    submission_path = Path(submission_path)
    template_path = Path(template_path)
    footprint_path = Path(footprint_path) if footprint_path is not None else None

    for path, label in ((submission_path, "submission"), (template_path, "template")):
        if not path.is_file():
            return {"valid": False, "errors": [f"{label} file does not exist: {path}"], "warnings": []}
    if footprint_path is not None and not footprint_path.is_file():
        return {"valid": False, "errors": [f"footprint file does not exist: {footprint_path}"], "warnings": []}

    try:
        with rasterio.open(template_path) as reference, rasterio.open(submission_path) as candidate:
            _validate_reference(reference, errors)
            if candidate.count != 1:
                errors.append("submission must contain exactly one band")
            if candidate.dtypes != ("float32",):
                errors.append(f"submission dtype must be float32; got {candidate.dtypes}")
            _same_grid(reference, candidate, "submission", errors)

            if footprint_path is None:
                footprint = reference.read_masks(1) > 0
                if reference.nodata is None and footprint.all():
                    warnings.append("template has no nodata/mask pixels; treating its full extent as the valid footprint")
            else:
                with rasterio.open(footprint_path) as mask_ds:
                    _same_grid(reference, mask_ds, "footprint mask", errors)
                    if mask_ds.count != 1:
                        errors.append("footprint mask must contain one band")
                    mask_values = mask_ds.read(1, masked=False)
                    mask_valid = mask_ds.read_masks(1) > 0
                    footprint = mask_valid & np.isfinite(mask_values) & (mask_values != 0)

            if not footprint.any():
                errors.append("valid footprint is empty")

            values = candidate.read(1, masked=False)
            candidate_mask = candidate.read_masks(1) > 0
            if values.shape != footprint.shape:
                errors.append("submission array shape does not match the footprint")
            else:
                in_values = values[footprint]
                in_mask = candidate_mask[footprint]
                if in_mask.size and not in_mask.all():
                    errors.append("submission masks/nodata some pixels inside the valid footprint")
                finite = np.isfinite(in_values)
                if finite.size and not finite.all():
                    errors.append(f"submission has {int((~finite).sum())} non-finite pixel(s) inside the valid footprint")
                if finite.any():
                    finite_values = in_values[finite]
                    minimum = float(finite_values.min())
                    maximum = float(finite_values.max())
                    if minimum < 0 or maximum > 1:
                        errors.append(f"valid-footprint values must be in [0,1]; observed min={minimum}, max={maximum}")
                else:
                    minimum = None
                    maximum = None

                outside = ~footprint
                if outside.any():
                    visible_finite_outside = outside & candidate_mask & np.isfinite(values)
                    if visible_finite_outside.any():
                        errors.append(f"submission has {int(visible_finite_outside.sum())} finite, unmasked pixel(s) outside the valid footprint")
                    masked_or_nan_outside = (~candidate_mask | ~np.isfinite(values))[outside]
                    if not masked_or_nan_outside.all():
                        errors.append("outside-footprint cells must be null/NaN or explicitly masked")
                else:
                    visible_finite_outside = np.zeros(0, dtype=bool)

            if values.shape == footprint.shape:
                in_count = int(footprint.sum())
                outside_count = int((~footprint).sum())
            else:
                in_count = 0
                outside_count = 0
            report = {
                "valid": not errors,
                "errors": errors,
                "warnings": warnings,
                "submission": str(submission_path),
                "template": str(template_path),
                "grid": {
                    "width": int(reference.width),
                    "height": int(reference.height),
                    "crs": reference.crs.to_string() if reference.crs else None,
                    "transform": list(reference.transform)[:6],
                    "resolution_m": [abs(float(reference.transform.a)), abs(float(reference.transform.e))],
                    "bands": int(candidate.count),
                    "dtype": list(candidate.dtypes),
                    "nodata": candidate.nodata,
                },
                "footprint_pixels": in_count,
                "outside_pixels": outside_count,
                "valid_min": minimum if values.shape == footprint.shape else None,
                "valid_max": maximum if values.shape == footprint.shape else None,
            }
            return report
    except Exception as exc:
        return {"valid": False, "errors": [f"could not open/validate GeoTIFF: {exc}"], "warnings": warnings}


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", value.strip()).strip("-").lower()
    if not slug:
        raise SubmissionError("candidate id must contain letters or digits")
    return slug[:48]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_submission(
    prediction_path: str | Path,
    template_path: str | Path,
    evidence_path: str | Path,
    candidate_id: str,
    output_dir: str | Path = "build",
    footprint_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a unique official-grid TIFF only after release evidence passes."""
    np, rasterio = _geo_imports()
    evidence_path = Path(evidence_path)
    if not evidence_path.is_file():
        raise SubmissionError(f"holdout evidence file does not exist: {evidence_path}")
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SubmissionError(f"could not read holdout evidence: {exc}") from exc
    try:
        gate_report = validate_release_evidence(evidence, candidate_id)
    except ValueError as exc:
        raise SubmissionError(str(exc)) from exc

    prediction_path = Path(prediction_path)
    template_path = Path(template_path)
    output_dir = Path(output_dir)
    footprint_path = Path(footprint_path) if footprint_path is not None else None
    if not prediction_path.is_file() or not template_path.is_file():
        raise SubmissionError("prediction and template files must both exist")
    if footprint_path is not None and not footprint_path.is_file():
        raise SubmissionError(f"footprint mask does not exist: {footprint_path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(template_path) as reference, rasterio.open(prediction_path) as prediction:
        reference_errors: list[str] = []
        _validate_reference(reference, reference_errors)
        if reference_errors:
            raise SubmissionError("invalid template: " + "; ".join(reference_errors))
        if prediction.count != 1:
            raise SubmissionError("prediction raster must contain exactly one band")
        grid_errors: list[str] = []
        _same_grid(reference, prediction, "prediction", grid_errors)
        if grid_errors:
            raise SubmissionError("prediction grid mismatch: " + "; ".join(grid_errors))

        if footprint_path is None:
            footprint = reference.read_masks(1) > 0
        else:
            with rasterio.open(footprint_path) as mask_ds:
                mask_errors: list[str] = []
                _same_grid(reference, mask_ds, "footprint mask", mask_errors)
                if mask_ds.count != 1:
                    mask_errors.append("footprint mask must contain exactly one band")
                if mask_errors:
                    raise SubmissionError("invalid footprint mask: " + "; ".join(mask_errors))
                mask_values = mask_ds.read(1, masked=False)
                mask_valid = mask_ds.read_masks(1) > 0
                footprint = mask_valid & np.isfinite(mask_values) & (mask_values != 0)
        if not footprint.any():
            raise SubmissionError("valid footprint is empty")
        source = prediction.read(1, masked=False)
        prediction_mask = prediction.read_masks(1) > 0
        if not prediction_mask[footprint].all():
            raise SubmissionError("prediction contains masked/nodata pixels inside the template footprint")
        inside = source[footprint]
        if not np.isfinite(inside).all():
            raise SubmissionError("prediction contains NaN/Inf inside the template footprint")
        if float(inside.min()) < 0 or float(inside.max()) > 1:
            raise SubmissionError(f"prediction values outside [0,1]: min={float(inside.min())}, max={float(inside.max())}")

        values = source.astype(np.float32, copy=True)
        values[~footprint] = np.nan
        pixel_hash = hashlib.sha256(values.tobytes(order="C")).hexdigest()
        now = datetime.now(timezone.utc)
        timestamp = now.strftime("%Y%m%dT%H%M%SZ")
        slug = _safe_slug(candidate_id)
        nonce = secrets.token_hex(4)
        stem = f"gems18-{slug}-{timestamp}-{pixel_hash[:8]}-{nonce}"
        output_path = output_dir / f"{stem}.tif"
        suffix = 2
        while output_path.exists():
            output_path = output_dir / f"{stem}-{suffix:02d}.tif"
            suffix += 1

        profile = reference.profile.copy()
        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=float("nan"),
            compress="deflate",
            predictor=3,
        )
        temporary_path: Path | None = None
        try:
            fd, temp_name = tempfile.mkstemp(prefix=".gems18-", suffix=".tif", dir=output_dir)
            os.close(fd)
            temporary_path = Path(temp_name)
            with rasterio.open(temporary_path, "w", **profile) as dst:
                dst.write(values, 1)
            report = validate_geotiff(temporary_path, template_path, footprint_path)
            if not report["valid"]:
                raise SubmissionError("generated TIFF failed revalidation: " + "; ".join(report["errors"]))
            os.replace(temporary_path, output_path)
            temporary_path = None
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    final_report = validate_geotiff(output_path, template_path, footprint_path)
    if not final_report["valid"]:
        output_path.unlink(missing_ok=True)
        raise SubmissionError("packaged TIFF failed final revalidation: " + "; ".join(final_report["errors"]))

    full_sha = _sha256_file(output_path)
    note = f"18GEMSDOE {candidate_id} | holdout evidence {evidence['holdout_id']} | release gate PASS | SHA-256 {full_sha[:12]}"
    note_path = output_path.with_suffix(".note.txt")
    note_path.write_text(note + "\n", encoding="utf-8")
    manifest = {
        "candidate_id": candidate_id,
        "file": output_path.name,
        "sha256": full_sha,
        "pixel_sha256": pixel_hash,
        "note": note,
        "holdout_id": evidence["holdout_id"],
        "footprint_source": footprint_path.name if footprint_path is not None else "template-mask",
        "release_gate": gate_report,
        "format_validation": final_report,
        "created_utc": now.isoformat(),
    }
    manifest_path = output_path.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"file": output_path, "note_file": note_path, "manifest_file": manifest_path, "manifest": manifest}
