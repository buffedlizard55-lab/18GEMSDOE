"""Release gate for a pre-registered, spatially blocked candidate."""

from __future__ import annotations

import math
import re
from typing import Any


class GateError(ValueError):
    """Raised when evidence is insufficient for a release package."""


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_release_evidence(evidence: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    """Validate holdout evidence and recompute the project promotion gate.

    Required evidence format is documented in docs/research/preregistration.md.
    This is a process gate, not a cryptographic attestation: the evidence file
    must still be reviewed and committed with its source data/split hashes.
    """
    if not isinstance(evidence, dict):
        raise GateError("holdout evidence root must be a JSON object")
    errors: list[str] = []
    if evidence.get("schema_version") != 1:
        errors.append("holdout evidence schema_version must be 1")
    if evidence.get("candidate_id") != candidate_id:
        errors.append("candidate_id does not match the requested package")
    if evidence.get("pre_registered") is not True:
        errors.append("candidate was not marked preregistered")
    if evidence.get("holdout_locked_before_tuning") is not True:
        errors.append("the spatial holdout was not locked before tuning")
    if evidence.get("baseline_independently_reproduced") is not True:
        errors.append("the comparator has not been independently reproduced")
    if evidence.get("negative_controls_pass") is not True:
        errors.append("mechanistic negative controls did not pass")
    if evidence.get("content_unique") is not True:
        errors.append("the prediction has not passed the uniqueness check")
    if not isinstance(evidence.get("holdout_id"), str) or not evidence["holdout_id"].strip():
        errors.append("holdout_id is required")

    for key in ("holdout_manifest_sha256", "input_manifest_sha256", "preregistration_commit"):
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{key} is required")
    for key in ("holdout_manifest_sha256", "input_manifest_sha256"):
        value = evidence.get(key)
        if isinstance(value, str) and not re.fullmatch(r"[0-9a-fA-F]{64}", value):
            errors.append(f"{key} must be a 64-character SHA-256")

    baseline = evidence.get("baseline")
    candidate = evidence.get("candidate")
    if not isinstance(baseline, dict) or baseline.get("status") != "INDEPENDENTLY_REPRODUCED":
        errors.append("baseline.status must be INDEPENDENTLY_REPRODUCED")
        baseline = {}
    if not isinstance(candidate, dict):
        errors.append("candidate fold metrics are required")
        candidate = {}

    metric_arrays: dict[str, tuple[list[float], list[float]]] = {}
    for metric in ("dense", "sparse"):
        base_values = baseline.get(f"{metric}_fold_dti")
        candidate_values = candidate.get(f"{metric}_fold_dti")
        if not isinstance(base_values, list) or not isinstance(candidate_values, list):
            errors.append(f"baseline and candidate {metric}_fold_dti arrays are required")
            continue
        if len(base_values) != 4 or len(candidate_values) != 4:
            errors.append(f"{metric} metrics must contain exactly four spatial folds")
            continue
        if not all(_finite_number(v) for v in base_values + candidate_values):
            errors.append(f"{metric} fold metrics must all be finite numbers")
            continue
        metric_arrays[metric] = ([float(v) for v in base_values], [float(v) for v in candidate_values])

    ci = evidence.get("paired_block_bootstrap_95pct_lower_bound")
    if not isinstance(ci, dict):
        errors.append("paired block-bootstrap lower bounds are required")
    else:
        for metric in ("dense", "sparse"):
            value = ci.get(metric)
            if not _finite_number(value) or float(value) <= 0:
                errors.append(f"95% paired block-bootstrap lower bound for {metric} must be positive")

    metrics: dict[str, Any] = {}
    if len(metric_arrays) == 2:
        dense_base, dense_candidate = metric_arrays["dense"]
        sparse_base, sparse_candidate = metric_arrays["sparse"]
        dense_delta = [c - b for b, c in zip(dense_base, dense_candidate)]
        sparse_delta = [c - b for b, c in zip(sparse_base, sparse_candidate)]
        sparse_fold_wins = sum(delta > 0 for delta in sparse_delta)
        mean_dense_delta = sum(dense_delta) / 4
        mean_sparse_delta = sum(sparse_delta) / 4
        metrics = {
            "mean_dense_delta": mean_dense_delta,
            "mean_sparse_delta": mean_sparse_delta,
            "sparse_fold_wins": sparse_fold_wins,
            "dense_fold_delta": dense_delta,
            "sparse_fold_delta": sparse_delta,
        }
        if mean_dense_delta <= 0:
            errors.append("candidate mean dense DTI must exceed the reproduced comparator")
        if mean_sparse_delta <= 0:
            errors.append("candidate mean sparse DTI must exceed the reproduced comparator")
        if sparse_fold_wins < 3:
            errors.append("candidate must win sparse DTI in at least three of four folds")
        if min(dense_delta + sparse_delta) < -0.01:
            errors.append("candidate may not lose more than 0.01 DTI in any fold")

    if evidence.get("gate_status") != "PASS":
        errors.append("gate_status must be PASS")
    if errors:
        raise GateError("Release gate blocked:\n- " + "\n- ".join(errors))
    return {"status": "PASS", "candidate_id": candidate_id, **metrics}
