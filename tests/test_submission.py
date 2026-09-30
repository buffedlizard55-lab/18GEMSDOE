from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine

from gems18.gates import GateError, validate_release_evidence
from gems18.submission import SubmissionError, package_submission, validate_geotiff


TRANSFORM = Affine(100, 0, 500000, 0, -100, 4400000)


def write_raster(path: Path, values: np.ndarray, *, dtype="float32", nodata=np.nan, transform=TRANSFORM, crs="EPSG:32611"):
    profile = {
        "driver": "GTiff",
        "width": values.shape[1],
        "height": values.shape[0],
        "count": 1,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(values.astype(dtype), 1)


def good_evidence(candidate_id="H18-N1"):
    return {
        "schema_version": 1,
        "candidate_id": candidate_id,
        "pre_registered": True,
        "holdout_locked_before_tuning": True,
        "baseline_independently_reproduced": True,
        "negative_controls_pass": True,
        "content_unique": True,
        "holdout_id": "sealed-basin-test",
        "holdout_manifest_sha256": "a" * 64,
        "input_manifest_sha256": "b" * 64,
        "preregistration_commit": "abc1234",
        "gate_status": "PASS",
        "baseline": {
            "status": "INDEPENDENTLY_REPRODUCED",
            "dense_fold_dti": [0.20, 0.21, 0.22, 0.23],
            "sparse_fold_dti": [0.08, 0.09, 0.10, 0.11],
        },
        "candidate": {
            "dense_fold_dti": [0.205, 0.215, 0.225, 0.235],
            "sparse_fold_dti": [0.09, 0.10, 0.105, 0.12],
        },
        "paired_block_bootstrap_95pct_lower_bound": {"dense": 0.001, "sparse": 0.002},
    }


def test_valid_geotiff_passes_and_checks_range(tmp_path):
    template = tmp_path / "template.tif"
    candidate = tmp_path / "candidate.tif"
    ref = np.zeros((4, 5), dtype=np.float32)
    ref[0, 0] = np.nan
    pred = np.full((4, 5), 0.25, dtype=np.float32)
    pred[0, 0] = np.nan
    write_raster(template, ref)
    write_raster(candidate, pred)

    report = validate_geotiff(candidate, template)

    assert report["valid"] is True
    assert report["footprint_pixels"] == 19
    assert report["valid_min"] == 0.25
    assert report["valid_max"] == 0.25


def test_out_of_range_inside_footprint_fails(tmp_path):
    template = tmp_path / "template.tif"
    candidate = tmp_path / "candidate.tif"
    write_raster(template, np.zeros((4, 5), dtype=np.float32))
    values = np.zeros((4, 5), dtype=np.float32)
    values[2, 3] = 1.0001
    write_raster(candidate, values)

    report = validate_geotiff(candidate, template)

    assert report["valid"] is False
    assert any("[0,1]" in error for error in report["errors"])


def test_nan_inside_footprint_fails(tmp_path):
    template = tmp_path / "template.tif"
    candidate = tmp_path / "candidate.tif"
    write_raster(template, np.zeros((4, 5), dtype=np.float32))
    values = np.zeros((4, 5), dtype=np.float32)
    values[1, 1] = np.nan
    write_raster(candidate, values)

    report = validate_geotiff(candidate, template)

    assert report["valid"] is False
    assert any("non-finite" in error for error in report["errors"])


def test_finite_unmasked_outside_footprint_fails(tmp_path):
    template = tmp_path / "template.tif"
    candidate = tmp_path / "candidate.tif"
    ref = np.zeros((4, 5), dtype=np.float32)
    ref[-1, -1] = np.nan
    pred = np.zeros((4, 5), dtype=np.float32)
    pred[-1, -1] = 0.5
    write_raster(template, ref)
    write_raster(candidate, pred)

    report = validate_geotiff(candidate, template)

    assert report["valid"] is False
    assert any("outside the valid footprint" in error for error in report["errors"])


def test_wrong_crs_or_transform_fails(tmp_path):
    template = tmp_path / "template.tif"
    candidate = tmp_path / "candidate.tif"
    write_raster(template, np.zeros((4, 5), dtype=np.float32))
    write_raster(candidate, np.zeros((4, 5), dtype=np.float32), transform=Affine(100, 0, 500010, 0, -100, 4400000))

    report = validate_geotiff(candidate, template)

    assert report["valid"] is False
    assert any("transform" in error for error in report["errors"])


def test_release_gate_recomputes_fold_metrics():
    evidence = good_evidence()
    report = validate_release_evidence(evidence, "H18-N1")
    assert report["status"] == "PASS"
    assert report["sparse_fold_wins"] == 4
    assert report["mean_dense_delta"] > 0
    assert report["mean_sparse_delta"] > 0


def test_release_gate_rejects_unlocked_or_nonpassing_evidence():
    evidence = good_evidence()
    evidence["holdout_locked_before_tuning"] = False
    evidence["gate_status"] = "BLOCKED"
    try:
        validate_release_evidence(evidence, "H18-N1")
    except GateError as exc:
        assert "holdout was not locked" in str(exc)
        assert "gate_status must be PASS" in str(exc)
    else:
        raise AssertionError("invalid release evidence was accepted")


def test_packager_uses_explicit_footprint_mask_when_template_has_no_nodata(tmp_path):
    template = tmp_path / "template.tif"
    prediction = tmp_path / "prediction.tif"
    footprint = tmp_path / "footprint.tif"
    evidence = tmp_path / "evidence.json"
    write_raster(template, np.zeros((4, 5), dtype=np.float32), nodata=None)
    write_raster(prediction, np.full((4, 5), 0.4, dtype=np.float32))
    mask = np.zeros((4, 5), dtype=np.uint8)
    mask[1, 1:3] = 1
    write_raster(footprint, mask, dtype="uint8", nodata=0)
    evidence.write_text(json.dumps(good_evidence()))

    result = package_submission(prediction, template, evidence, "H18-N1", tmp_path / "out", footprint_path=footprint)

    assert result["manifest"]["footprint_source"] == "footprint.tif"
    assert result["manifest"]["format_validation"]["footprint_pixels"] == 2
    checked = validate_geotiff(result["file"], template, footprint)
    assert checked["valid"] is True
    with rasterio.open(result["file"]) as ds:
        values = ds.read(1)
        assert np.isfinite(values[1, 1:3]).all()
        assert np.isnan(values[0, 0])


def test_packager_refuses_missing_or_failed_evidence(tmp_path):
    template = tmp_path / "template.tif"
    prediction = tmp_path / "prediction.tif"
    failed = tmp_path / "failed.json"
    write_raster(template, np.zeros((4, 5), dtype=np.float32))
    write_raster(prediction, np.full((4, 5), 0.1, dtype=np.float32))
    bad = good_evidence()
    bad["gate_status"] = "BLOCKED"
    failed.write_text(json.dumps(bad))

    try:
        package_submission(prediction, template, failed, "H18-N1", tmp_path / "out")
    except SubmissionError as exc:
        assert "gate_status must be PASS" in str(exc)
    else:
        raise AssertionError("packager accepted failed evidence")


def test_packager_writes_unique_tif_note_and_manifest_after_gate(tmp_path):
    template = tmp_path / "template.tif"
    prediction = tmp_path / "prediction.tif"
    evidence = tmp_path / "evidence.json"
    ref = np.zeros((4, 5), dtype=np.float32)
    ref[-1, -1] = np.nan
    pred = np.full((4, 5), 0.4, dtype=np.float32)
    pred[-1, -1] = np.nan
    write_raster(template, ref)
    write_raster(prediction, pred)
    evidence.write_text(json.dumps(good_evidence()))

    result = package_submission(prediction, template, evidence, "H18-N1", tmp_path / "out")

    assert result["file"].exists()
    assert result["note_file"].exists()
    assert result["manifest_file"].exists()
    assert result["file"].suffix == ".tif"
    assert "h18-n1" in result["file"].name
    checked = validate_geotiff(result["file"], template)
    assert checked["valid"] is True
    with rasterio.open(result["file"]) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert np.isnan(ds.read(1)[-1, -1])

    duplicate_name_guard = package_submission(prediction, template, evidence, "H18-N1", tmp_path / "out")
    assert duplicate_name_guard["file"].exists()
    assert duplicate_name_guard["file"] != result["file"]
    assert duplicate_name_guard["file"].name.startswith("gems18-h18-n1-")
