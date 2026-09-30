"""Spatially blocked holdout, paired block bootstrap and a sealed slice.

The unit of independence in a fault map is a *structure*, not a pixel: two
adjacent pixels of the same fault are one observation.  Every split here is
therefore made of whole 512 px (51.2 km) blocks, folds are balanced on proxy
fault mass, and a sealed set of blocks is written to disk with its manifest hash
before any candidate is built so that nothing can be tuned against it.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

BLOCK_PX = 512
N_FOLDS = 4


@dataclass(frozen=True)
class Partition:
    """Block partition of the competition grid."""

    block_id: np.ndarray  # (rows, cols) int32, -1 outside any block row/col
    blocks: list[tuple[int, int]]  # (row0, col0) of each block in label order
    fold_of_block: np.ndarray  # per block label -> fold
    sealed_blocks: list[int]

    def fold_mask(self, fold: int) -> np.ndarray:
        return np.isin(self.block_id, np.flatnonzero(self.fold_of_block == fold))

    def sealed_mask(self) -> np.ndarray:
        return np.isin(self.block_id, np.asarray(self.sealed_blocks, dtype=int))


def build_partition(shape: tuple[int, int], mass: np.ndarray, *, seed: int = 20260930) -> Partition:
    """Partition the grid into 512 px blocks, greedily balanced on ``mass``.

    ``mass`` is the proxy-fault pixel count per cell (or any non-negative weight)
    so that no fold is starved of positives.
    """
    rows, cols = shape
    block_id = np.full(shape, -1, dtype=np.int32)
    blocks: list[tuple[int, int]] = []
    block_mass: list[float] = []
    for r0 in range(0, rows, BLOCK_PX):
        for c0 in range(0, cols, BLOCK_PX):
            lab = len(blocks)
            block_id[r0 : r0 + BLOCK_PX, c0 : c0 + BLOCK_PX] = lab
            blocks.append((r0, c0))
            block_mass.append(float(mass[r0 : r0 + BLOCK_PX, c0 : c0 + BLOCK_PX].sum()))
    order = np.argsort(-np.asarray(block_mass))
    fold_load = np.zeros(N_FOLDS)
    fold_of_block = np.zeros(len(blocks), dtype=np.int32)
    for b in order:
        f = int(np.argmin(fold_load))
        fold_of_block[b] = f
        fold_load[f] += block_mass[b]
    rng = np.random.default_rng(seed)
    sealed = sorted(rng.choice(len(blocks), size=max(1, len(blocks) // 4), replace=False).tolist())
    return Partition(block_id=block_id, blocks=blocks, fold_of_block=fold_of_block, sealed_blocks=sealed)


def split_digest(partition: Partition) -> str:
    """Deterministic hash of the split, recorded so the holdout cannot be quietly re-cut."""
    payload = json.dumps(
        {
            "blocks": [[int(r), int(c)] for r, c in partition.blocks],
            "folds": [int(f) for f in partition.fold_of_block],
            "sealed": [int(b) for b in partition.sealed_blocks],
            "block_px": BLOCK_PX,
        },
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def block_truth(truth: np.ndarray, partition: Partition, blocks: list[int]) -> np.ndarray:
    """Truth restricted to a set of blocks (false positives still count globally)."""
    keep = np.zeros(truth.shape, dtype=bool)
    sel = np.asarray(blocks, dtype=int)
    if sel.size:
        keep = np.isin(partition.block_id, sel)
    return (truth.astype(bool) & keep).astype(np.float32)


def paired_block_bootstrap(
    diff_per_block: np.ndarray, *, n: int = 2000, seed: int = 7
) -> dict:
    """Paired bootstrap over blocks: P(candidate > comparator) and a 95 % CI."""
    d = np.asarray(diff_per_block, dtype=float)
    d = d[np.isfinite(d)]
    if d.size == 0:
        return {"n_blocks": 0, "p_candidate_better": None, "ci95": [None, None], "mean": None}
    rng = np.random.default_rng(seed)
    draws = rng.choice(d, size=(n, d.size), replace=True).mean(axis=1)
    return {
        "n_blocks": int(d.size),
        "mean": float(d.mean()),
        "p_candidate_better": float((draws > 0).mean()),
        "ci95": [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))],
    }


def write_manifest(path: str | Path, partition: Partition, extra: dict) -> str:
    p = Path(path)
    payload = {
        "block_px": BLOCK_PX,
        "n_blocks": len(partition.blocks),
        "fold_of_block": [int(f) for f in partition.fold_of_block],
        "sealed_blocks": [int(b) for b in partition.sealed_blocks],
        "split_sha256": split_digest(partition),
    }
    payload.update(extra)
    p.write_text(json.dumps(payload, indent=1, sort_keys=True))
    return payload["split_sha256"]
