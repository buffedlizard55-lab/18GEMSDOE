from __future__ import annotations

from copy import deepcopy

import pytest

from gems18.gates import GateError, validate_release_evidence


@pytest.fixture
def evidence():
    return {
        "schema_version": 1,
        "candidate_id": "H18-N1",
        "pre_registered": True,
        "holdout_locked_before_tuning": True,
        "baseline_independently_reproduced": True,
        "negative_controls_pass": True,
        "content_unique": True,
        "holdout_id": "sealed-basin",
        "holdout_manifest_sha256": "a" * 64,
        "input_manifest_sha256": "b" * 64,
        "preregistration_commit": "1234567",
        "gate_status": "PASS",
        "baseline": {"status": "INDEPENDENTLY_REPRODUCED", "dense_fold_dti": [0.20, 0.21, 0.22, 0.23], "sparse_fold_dti": [0.08, 0.09, 0.10, 0.11]},
        "candidate": {"dense_fold_dti": [0.205, 0.215, 0.225, 0.235], "sparse_fold_dti": [0.09, 0.10, 0.105, 0.12]},
        "paired_block_bootstrap_95pct_lower_bound": {"dense": 0.001, "sparse": 0.002},
    }


def test_gate_passes_valid_four_fold_record(evidence):
    result = validate_release_evidence(evidence, "H18-N1")
    assert result["status"] == "PASS"
    assert result["sparse_fold_wins"] == 4


def test_gate_rejects_non_object_evidence():
    with pytest.raises(GateError, match="root must be a JSON object"):
        validate_release_evidence(None, "H18-N1")


def test_gate_requires_baseline_reproduction(evidence):
    record = deepcopy(evidence)
    record["baseline_independently_reproduced"] = False
    with pytest.raises(GateError, match="comparator has not been independently reproduced"):
        validate_release_evidence(record, "H18-N1")


def test_gate_rejects_candidate_that_loses_on_mean(evidence):
    record = deepcopy(evidence)
    record["candidate"]["dense_fold_dti"] = [0.19, 0.20, 0.21, 0.22]
    with pytest.raises(GateError, match="mean dense DTI"):
        validate_release_evidence(record, "H18-N1")


def test_gate_rejects_fold_loss_over_point_zero_one(evidence):
    record = deepcopy(evidence)
    record["candidate"]["sparse_fold_dti"] = [0.06, 0.10, 0.11, 0.13]
    with pytest.raises(GateError, match="lose more than 0.01"):
        validate_release_evidence(record, "H18-N1")
