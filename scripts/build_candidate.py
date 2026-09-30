#!/usr/bin/env python3
"""Build the shipped H19-C submission field and the evidence that goes with it.

The field is composed of three components, in the order of how much is *claimed*
for each (``docs/research/hypotheses.md`` gives the mechanism for each):

``catalogue``
    the provided training labels.  The platform masks exactly these pixels out of
    scoring (DrivenData staff, forum 11516 post 4), so including them is neutral in
    both prize rounds and makes the file a complete fault map rather than a
    partial one.
``state-map``
    the USGS State Geologic Map Compilation structure lines that fall inside the
    footprint (H19-B).  These are mapped faults; 61,664 of their pixels have no
    training label within 300 m, so they are pixels the scoring mask does not
    cover.  This is the component whose value depends on an unverifiable claim --
    that the experts' new faults are, at least partly, structures that state maps
    carry and the Quaternary catalogue does not -- and it is labelled as such.
``physics``
    pixels where **at least two physically independent families** (magnetics,
    gravity, topography) have a lineament ridge at the same place (H19-A),
    capped to a support chosen on the tuning folds.

Everything is emitted at value 1: the metric's denominator carries a fixed
``0.8 * |G|`` term, so raising a field's values can only help (``docs/validation.md``
derives this), and the algebra is otherwise scale free.

Usage::

    python scripts/build_candidate.py                 # sweep + sealed read + write field
    python scripts/build_candidate.py --no-write      # evidence only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import gems18.fields as F  # noqa: E402
from gems18.holdout import build_partition, split_digest  # noqa: E402
from gems18.metric import ALPHA, BETA, BlockResolvedScorer, score  # noqa: E402

DEFAULT_SUPPORT_SWEEP = (25000, 50000, 100000, 200000, 400000)


def log(msg: str) -> None:
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


class Raster:
    """Small reader that exposes bands by their tag name."""

    def __init__(self, path: Path):
        self.path = Path(path)
        with rasterio.open(self.path) as ds:
            self.shape = (ds.height, ds.width)
            self.transform = ds.transform
            self.crs = ds.crs
            self.names = {}
            for i in range(1, ds.count + 1):
                tag = ds.tags(i).get("band_name") or ds.descriptions[i - 1] or f"band{i}"
                self.names[tag.split(" - ")[0]] = i
            self._count = ds.count

    def named(self, *tags: str) -> np.ndarray:
        with rasterio.open(self.path) as ds:
            for t in tags:
                idx = self.names.get(t)
                if idx is None:
                    raise KeyError(f"{t!r} not in {sorted(self.names)}")
                arr = ds.read(idx).astype(np.float32)
                if ds.nodata is not None:
                    arr[arr == np.float32(ds.nodata)] = np.nan
                yield arr


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_png(path: Path, rgb: np.ndarray) -> None:
    """Minimal RGB PNG writer (no image library in this environment)."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            len(data).to_bytes(4, "big")
            + tag
            + data
            + zlib.crc32(tag + data).to_bytes(4, "big")
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", w.to_bytes(4, "big") + h.to_bytes(4, "big") + bytes([8, 2, 0, 0, 0]))
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def build_physics_components(r: Raster, valid: np.ndarray, log) -> dict:
    """The three independent evidence families and their conjunction (H19-A)."""
    out = {}
    (rtp, tmi, tmi_hg) = r.named("rtp", "tmi", "tmi_hg")
    mag = np.maximum(
        F.robust_normalise(np.abs(F.fill_nan(rtp))),
        F.robust_normalise(F.fill_nan(tmi)),
    )
    mag = np.maximum(mag, F.robust_normalise(np.abs(F.fill_nan(tmi_hg))))
    mag = np.maximum(mag, F.multiscale_max(lambda a, s: np.abs(F.tilt_derivative(a, s)), rtp))
    gy, gx = F.gradient(mag, 2.0)
    out["mag_ridge"] = F.ridge_map(mag, gy, gx, valid=valid)
    del mag, rtp, tmi, tmi_hg, gy, gx
    log(f"  magnetics ridge px {int((out['mag_ridge'] > 0).sum()):,}")

    (grav, grav_hg) = r.named("iso_grav_anom", "iso_grav_anom_hg")
    grav_f = F.multiscale_max(F.hgm, grav, scales=(4.0, 8.0, 15.0))
    grav_f = np.maximum(grav_f, F.robust_normalise(np.abs(F.fill_nan(grav_hg))))
    gy, gx = F.gradient(grav_f, 2.0)
    out["grav_ridge"] = F.ridge_map(grav_f, gy, gx, valid=valid)
    del grav, grav_hg, grav_f, gy, gx
    log(f"  gravity ridge px {int((out['grav_ridge'] > 0).sum()):,}")

    (elev, slope) = r.named("det_elev", "det_elev_slope")
    elev_f = F.fill_nan(elev)
    curv = F.multiscale_max(lambda a, s: np.abs(F.curvature(a, s)), elev_f)
    topo = np.maximum(curv, F.robust_normalise(np.abs(F.fill_nan(slope))))
    gy, gx = F.gradient(topo, 2.0)
    out["topo_ridge"] = F.ridge_map(topo, gy, gx, valid=valid)
    del elev, slope, elev_f, curv, topo, gy, gx
    log(f"  topography ridge px {int((out['topo_ridge'] > 0).sum()):,}")

    agree = F.agreement_2plus(
        [out["mag_ridge"] > 0, out["grav_ridge"] > 0, out["topo_ridge"] > 0], radius=1
    )
    base = (
        0.45 * out["mag_ridge"] + 0.30 * out["topo_ridge"] + 0.15 * out["grav_ridge"]
    )
    out["conjunction"] = (base * agree).astype(np.float32)
    del base, agree
    log(f"  conjunction px {int((out['conjunction'] > 0).sum()):,}")
    return out


def top_support(field: np.ndarray, n: int, valid: np.ndarray) -> np.ndarray:
    """Keep the ``n`` strongest positive pixels of ``field`` (ties by index)."""
    flat = np.where(valid & (field > 0), field, 0.0).ravel()
    nz = int(np.count_nonzero(flat))
    if nz == 0:
        return np.zeros_like(field)
    k = min(n, nz)
    idx = np.argpartition(flat, -k)[-k:]
    out = np.zeros(flat.size, dtype=bool)
    out[idx] = True
    return out.reshape(field.shape)


def sensitivity_table(emission_px: int, g_values=(30000, 60000, 120000, 240000)) -> list[dict]:
    """Score as a function of assumed truth size and coverage -- stated, not claimed.

    ``DTI = T / (0.2 * M + 0.8 * |G|)`` with ``T = rho * |G|``.  ``M`` is the emitted
    mass outside the pixel-exact known-fault mask, so it is the *paid* mass.
    """
    rows = []
    for g in g_values:
        for rho in (0.1, 0.2, 0.3, 0.5, 0.7):
            t = rho * g
            d = ALPHA * emission_px + BETA * g
            rows.append({"truth_px": g, "coverage_rho": rho, "dti": t / d})
    return rows


def main() -> int:
    global T0
    T0 = time.time()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", type=Path, default=ROOT / "data")
    ap.add_argument("--support-sweep", default=",".join(str(x) for x in DEFAULT_SUPPORT_SWEEP))
    ap.add_argument("--physics-support", type=int, default=None)
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "submission_h19.tif")
    ap.add_argument("--evidence", type=Path, default=ROOT / "data" / "evidence" / "candidate_h19.json")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    feat = args.data / "training_features.tif"
    labels_p = args.data / "labels.tif"
    template_p = args.data / "sample_submission.tif"
    proxy_p = args.data / "proxy_catalogue.tif"

    with rasterio.open(labels_p) as ds:
        labels = ds.read(1)
    valid = labels != -1
    known = labels == 1
    with rasterio.open(template_p) as ds:
        tmpl = ds.read(1, masked=True)
        transform, crs = ds.transform, ds.crs
        footprint = ~tmpl.mask
    with rasterio.open(proxy_p) as ds:
        proxy = ds.read(1)
    log(f"labels: {int(known.sum()):,} px | footprint {int(valid.sum()):,} px | "
        f"SGMC proxy {int((proxy > 0).sum()):,} px (gap {(proxy == 2).sum():,})")

    # held-out blocks for the *catalogue* test: can the physics arm find faults it
    # was not shown?  (Tuning folds choose the support; the sealed blocks are read once.)
    # The holdout split is fixed by the split manifest, not by this script: build it
    # from the same proxy mass the manifest was cut with and refuse to continue if the
    # digest drifts (that is the whole point of committing the digest).
    partition = build_partition(labels.shape, (proxy == 2).astype(np.float32))
    digest = split_digest(partition)
    _manifest_p = ROOT / "data" / "evidence" / "holdout_manifest.json"
    if _manifest_p.exists():
        _recorded = json.loads(_manifest_p.read_text()).get("split_sha256")
        if _recorded and _recorded != digest:
            raise SystemExit(f"holdout split drifted: computed {digest} != recorded {_recorded}")
    tuning = ~np.isin(partition.block_id, np.asarray(partition.sealed_blocks))
    log(f"partition: {len(partition.blocks)} blocks, sealed {len(partition.sealed_blocks)}, split {digest[:16]}…")

    r = Raster(feat)
    arms = build_physics_components(r, valid, log)
    conjunction = arms.pop("conjunction")

    sweep = [int(x) for x in args.support_sweep.split(",") if x]
    results = []
    for n in sweep:
        mask = top_support(conjunction, n, valid)
        emit = mask & ~known  # paid emission: exactly what the platform will see
        truth_cat = known & tuning  # catalogue pixels in tuning blocks
        sc = BlockResolvedScorer(emit.astype(np.float32), valid=valid, known_mask=None,
                                 block_id=partition.block_id)
        res = sc.evaluate(truth_cat.astype(np.float32))
        gap_truth = (proxy == 2)
        sc2 = BlockResolvedScorer(emit.astype(np.float32), valid=valid, known_mask=known,
                                  block_id=partition.block_id)
        res_gap = sc2.evaluate(gap_truth.astype(np.float32))
        results.append(
            {
                "support_px": n,
                "emitted_px": int(emit.sum()),
                "catalogue_tuning_dti": res.dti,
                "catalogue_tuning_tp_w": res.tp_w,
                "catalogue_tuning_truth_px": res.truth_px,
                "sgmc_gap_dti": res_gap.dti,
                "sgmc_gap_tp_w": res_gap.tp_w,
            }
        )
        del sc, sc2
        log(f"  support {n:>7,} -> catalogue-tuning DTI {res.dti:.4f} | SGMC-gap DTI {res_gap.dti:.4f}")

    best = max(results, key=lambda d: d["catalogue_tuning_dti"])
    support = args.physics_support or best["support_px"]
    log(f"support chosen on tuning folds: {support:,} px")

    physics = top_support(conjunction, support, valid)
    del conjunction, arms

    # ---- sealed read (once, after the support is fixed)
    sealed = np.isin(partition.block_id, np.asarray(partition.sealed_blocks))
    sc = BlockResolvedScorer(physics.astype(np.float32), valid=valid, known_mask=None,
                             block_id=partition.block_id)
    res_sealed = sc.evaluate((known & sealed).astype(np.float32))
    del sc
    log(f"SEALED catalogue read: DTI {res_sealed.dti:.4f} on {res_sealed.truth_px:,} px "
        f"(emitted {res_sealed.emission_px:,})")

    # ---- composition
    catalogue = known.copy()
    sgmc = proxy > 0
    field = (catalogue | sgmc | physics).astype(np.float32)
    emitted_paid = int((field > 0).sum()) - int((catalogue & (field > 0)).sum())
    components = {
        "catalogue_px": int(catalogue.sum()),
        "state_map_px": int(sgmc.sum()),
        "state_map_gap_px": int((proxy == 2).sum()),
        "physics_px": int(physics.sum()),
        "physics_on_state_map_frac": float((physics & sgmc).sum() / max(1, physics.sum())),
        "physics_on_catalogue_frac": float((physics & catalogue).sum() / max(1, physics.sum())),
        "total_px": int((field > 0).sum()),
        "paid_emission_px": emitted_paid,
        "coverage_of_footprint": float((field > 0).sum() / valid.sum()),
    }
    log(f"composition: {components}")

    sensitivity = sensitivity_table(emitted_paid)

    evidence = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "candidate_id": "H19-C",
        "field": "catalogue ∪ state-map structures ∪ >=2-family physics conjunction",
        "inputs": {
            "labels_sha256": sha256_file(labels_p),
            "features_sha256": sha256_file(feat),
            "template_sha256": sha256_file(template_p),
            "proxy_catalogue_sha256": sha256_file(proxy_p),
        },
        "holdout": {"split_sha256": digest, "blocks": len(partition.blocks),
                    "sealed_blocks": len(partition.sealed_blocks)},
        "support_sweep": results,
        "support_chosen": support,
        "sealed_catalogue_read": {
            "dti": res_sealed.dti, "truth_px": res_sealed.truth_px,
            "emission_px": res_sealed.emission_px, "tp_w": res_sealed.tp_w,
        },
        "components": components,
        "sensitivity": sensitivity,
        "notes": [
            "The state-map component cannot be validated against the hidden truth here; "
            "it is included because its pixels are outside the pixel-exact scoring mask and "
            "because state maps carry structures the Quaternary catalogue does not.  If that "
            "claim is false the component is pure false-positive mass, which is why its exact "
            "size is published next to it.",
            "The physics component is validated on the catalogue holdout (tuning folds choose "
            "the support, the sealed blocks are read once) and on the SGMC-gap proxy.",
            "No leaderboard score is claimed anywhere.",
        ],
    }

    if not args.no_write:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=1, default=str))
        out = np.where(valid, field, np.nan).astype(np.float32)
        profile = {
            "driver": "GTiff", "height": out.shape[0], "width": out.shape[1], "count": 1,
            "dtype": "float32", "crs": crs, "transform": transform,
            "nodata": float("nan"), "compress": "deflate", "tiled": True,
        }
        with rasterio.open(args.out, "w", **profile) as dst:
            dst.write(out, 1)
        evidence["submission"] = {
            "path": str(args.out), "bytes": args.out.stat().st_size,
            "sha256": sha256_file(args.out),
        }
        args.evidence.write_text(json.dumps(evidence, indent=1, default=str))
        log(f"wrote {args.out} ({args.out.stat().st_size:,} bytes) sha256 {evidence['submission']['sha256'][:16]}…")

        # small preview for the site
        step = 4
        small = field[::step, ::step]
        rgb = np.zeros(small.shape + (3,), dtype=np.uint8)
        v = valid[::step, ::step]
        rgb[..., 0] = np.where(v, 24, 255).astype(np.uint8)
        rgb[..., 1] = np.where(v, 26, 255).astype(np.uint8)
        rgb[..., 2] = np.where(v, 32, 255).astype(np.uint8)
        cat = catalogue[::step, ::step]
        sm = sgmc[::step, ::step]
        ph = physics[::step, ::step]
        rgb[cat] = (120, 160, 255)
        rgb[sm] = (255, 176, 64)
        rgb[ph] = (255, 72, 72)
        rgb[ph & (cat | sm)] = (255, 255, 0)
        write_png(ROOT / "docs" / "downloads" / "candidate_preview.png", rgb)
        log("wrote docs/downloads/candidate_preview.png")

    print(json.dumps({k: v for k, v in evidence.items() if k not in ("sensitivity", "support_sweep")},
                     indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
