"""
degrade_modalities.py  (v2)

Sensor degradation and depth-cleanup toolkit for the synthetic indoor fire
victim detection dataset.

Design rationale (v2):
  The raw Z-pass depth is rendered within the full volumetric scene, so
  smoke-affected pixels may record the depth of a scattering event rather
  than the underlying surface -- the same physical mechanism by which
  active range sensors (ToF / structured light) fail in scattering media.
  The raw depth therefore already carries a physically motivated,
  visibility-dependent ranging disturbance. Two consequences:

    1. `depth_clean` mode marks scatter-induced erroneous values as
       INVALID (0), aligning the data with real sensor behavior (sensors
       flag corrupted measurements; they do not silently report wrong
       distances). Run this on raw depth BEFORE release/training.
    2. The depth degradation pipeline models SENSOR-SIDE effects only
       (axial noise, flying pixels, uniform dropout, quantization).
       Smoke-driven dropout has been removed to avoid double-counting
       the disturbance already present in the rendered data.

Modes:
  python degrade_modalities.py --modality depth_clean --input depth_raw/test --output depth/test
  python degrade_modalities.py --modality depth --input depth/test --output depth_degraded/test --preset moderate
  python degrade_modalities.py --modality ir --input images_ir/test --output images_ir_degraded/test --preset moderate

`depth_clean` also writes <output>/../invalid_fraction_<split>.csv (per-frame
fraction of pixels marked invalid), which supports the smoke/disturbance
co-location statistic reported in Technical Validation.

All randomness is seeded per-file from the filename hash: results are exactly
reproducible. The resolved parameter set is written as JSON next to the
output directory.

Dependencies: numpy, opencv-python
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

PRESETS = {
    "mild": {
        "ir": {
            "optical_blur_sigma": 0.8,      # px, at native render resolution
            "sensor_size": [320, 240],      # (w, h) of simulated thermal core
            "fpn_column_sigma": 0.004,      # column offset, fraction of dynamic range
            "fpn_gain_sigma": 0.01,         # per-pixel multiplicative gain std
            "temporal_noise_sigma": 0.006,  # additive, fraction of dynamic range
            "agc_percentiles": [1.0, 99.0],
            "upsample_back": True,
        },
        "depth": {                          # SENSOR-SIDE effects only
            "axial_a": 0.004,               # m, constant axial noise term
            "axial_b": 0.0015,              # m^-1: sigma = a + b*z^2 (ToF-like)
            "edge_grad_thresh": 0.15,       # m, gradient defining a discontinuity
            "flying_pixel_prob": 0.15,      # per edge pixel
            "uniform_dropout_prob": 0.01,   # random sensor dropout
            "z_min": 0.3,                   # m
            "z_max": 10.0,                  # m
        },
    },
    "moderate": {
        "ir": {
            "optical_blur_sigma": 1.4,
            "sensor_size": [320, 240],
            "fpn_column_sigma": 0.010,
            "fpn_gain_sigma": 0.02,
            "temporal_noise_sigma": 0.015,
            "agc_percentiles": [1.0, 99.0],
            "upsample_back": True,
        },
        "depth": {
            "axial_a": 0.008,
            "axial_b": 0.003,
            "edge_grad_thresh": 0.12,
            "flying_pixel_prob": 0.35,
            "uniform_dropout_prob": 0.04,
            "z_min": 0.3,
            "z_max": 8.0,
        },
    },
    "severe": {
        "ir": {
            "optical_blur_sigma": 2.2,
            "sensor_size": [160, 120],
            "fpn_column_sigma": 0.020,
            "fpn_gain_sigma": 0.04,
            "temporal_noise_sigma": 0.030,
            "agc_percentiles": [2.0, 98.0],
            "upsample_back": True,
        },
        "depth": {
            "axial_a": 0.015,
            "axial_b": 0.006,
            "edge_grad_thresh": 0.10,
            "flying_pixel_prob": 0.6,
            "uniform_dropout_prob": 0.10,
            "z_min": 0.3,
            "z_max": 6.0,
        },
    },
}

# Scatter-outlier marking (depth_clean mode). Not severity-dependent:
# it is a data-preparation step, applied once, with fixed documented values.
OUTLIER_CFG = {
    "median_ksize": 5,     # window for local median (cv2 float32: 3 or 5)
    "abs_thresh": 0.05,    # m, absolute deviation floor
    "rel_thresh": 0.02,    # fraction of local median depth
    "iterations": 2,       # repeated passes catch clustered scatter pixels
}

DEPTH_MM_SCALE = 1000.0    # stored uint16 depth is in millimeters, 0 = invalid


def _rng_for(path: Path, global_seed: int) -> np.random.Generator:
    """Deterministic per-file RNG: seed = global_seed XOR filename hash."""
    h = int(hashlib.md5(path.name.encode()).hexdigest()[:8], 16)
    return np.random.default_rng(global_seed ^ h)


# ---------------------------------------------------------------------------
# Depth: scatter-outlier marking (run once on raw Z-pass depth)
# ---------------------------------------------------------------------------

def mark_depth_outliers(depth_m: np.ndarray, cfg: dict = OUTLIER_CFG):
    """Mark volumetric-scatter depth outliers as invalid (0).

    depth_m: float32 metric depth in meters (0 = already invalid).
    Returns (cleaned_depth, invalid_fraction). Pixels whose depth deviates
    from the local median beyond abs_thresh + rel_thresh * median are set
    to 0. Iterating the pass lets the median re-form over cleaned
    neighborhoods, catching clustered scatter pixels that a single pass
    would miss.
    """
    z = depth_m.astype(np.float32).copy()
    initially_valid = z > 0
    for _ in range(cfg["iterations"]):
        valid = z > 0
        if not valid.any():
            break
        # Median over the window; invalid pixels excluded by substituting
        # a large sentinel so they never become the local reference.
        z_for_median = np.where(valid, z, np.float32(1e6))
        med = cv2.medianBlur(z_for_median, cfg["median_ksize"])
        reliable_med = med < 1e5
        dev = np.abs(z - med)
        thresh = cfg["abs_thresh"] + cfg["rel_thresh"] * med
        outlier = valid & reliable_med & (dev > thresh)
        z[outlier] = 0.0
    n_ref = int(initially_valid.sum())
    invalid_fraction = float((initially_valid & (z == 0)).sum()) / max(n_ref, 1)
    return z, invalid_fraction


# ---------------------------------------------------------------------------
# Depth: sensor-side degradation (assumes outlier-marked input)
# ---------------------------------------------------------------------------

def degrade_depth(depth_m: np.ndarray, cfg: dict, rng: np.random.Generator) -> np.ndarray:
    """Apply sensor-side effects only. Smoke-induced disturbance is already
    present in the rendered data (volumetric scattering) and marked invalid
    by depth_clean; it is deliberately NOT re-applied here.

    depth_m: float32 meters, 0 = invalid. Returns uint16 mm, 0 = invalid."""
    h, w = depth_m.shape[:2]
    z = depth_m.astype(np.float32).copy()
    valid = z > 0

    # 1. Distance-dependent axial noise: sigma(z) = a + b * z^2 (ToF-like)
    sigma = cfg["axial_a"] + cfg["axial_b"] * z * z
    z = z + rng.normal(0.0, 1.0, size=(h, w)).astype(np.float32) * sigma

    # 2. Flying pixels along depth discontinuities (mixed-pixel effect)
    gx = cv2.Sobel(depth_m, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(depth_m, cv2.CV_32F, 0, 1, ksize=3)
    edges = np.hypot(gx, gy) > cfg["edge_grad_thresh"]
    fly = edges & valid & (rng.random((h, w)) < cfg["flying_pixel_prob"])
    if fly.any():
        bg = cv2.dilate(depth_m, np.ones((5, 5), np.uint8))
        alpha = rng.random((h, w)).astype(np.float32)
        z[fly] = alpha[fly] * depth_m[fly] + (1.0 - alpha[fly]) * bg[fly]

    # 3. Uniform sensor dropout (e.g. low-reflectivity failures)
    dropped = rng.random((h, w)) < cfg["uniform_dropout_prob"]
    valid &= ~dropped

    # 4. Range clipping
    valid &= (z >= cfg["z_min"]) & (z <= cfg["z_max"])

    # 5. Quantize to uint16 millimeters, 0 = invalid
    out = np.zeros((h, w), dtype=np.uint16)
    zq = np.clip(z * DEPTH_MM_SCALE, 0, 65535).astype(np.uint16)
    out[valid] = zq[valid]
    return out


# ---------------------------------------------------------------------------
# IR degradation (unchanged from v1)
# ---------------------------------------------------------------------------

def degrade_ir(ir: np.ndarray, cfg: dict, rng: np.random.Generator) -> np.ndarray:
    """ir: single-channel float32 in [0,1] (linear radiance ordering).
    Returns uint8 (native render size if upsample_back, else sensor size)."""
    h0, w0 = ir.shape[:2]
    sw, sh = cfg["sensor_size"]

    if cfg["optical_blur_sigma"] > 0:                       # 1. optics MTF
        ir = cv2.GaussianBlur(ir, (0, 0), cfg["optical_blur_sigma"])
    ir = cv2.resize(ir, (sw, sh), interpolation=cv2.INTER_AREA)  # 2. sensor res

    col_offsets = rng.normal(0.0, cfg["fpn_column_sigma"], size=(1, sw)).astype(np.float32)
    pix_gain = rng.normal(1.0, cfg["fpn_gain_sigma"], size=(sh, sw)).astype(np.float32)
    ir = ir * pix_gain + col_offsets                        # 3. fixed-pattern noise

    ir = ir + rng.normal(0.0, cfg["temporal_noise_sigma"],  # 4. read noise
                         size=(sh, sw)).astype(np.float32)

    lo, hi = np.percentile(ir, cfg["agc_percentiles"])      # 5. AGC
    if hi - lo < 1e-6:
        hi = lo + 1e-6
    ir = np.clip((ir - lo) / (hi - lo), 0.0, 1.0)

    ir8 = (ir * 255.0 + 0.5).astype(np.uint8)               # 6. 8-bit quantization
    if cfg.get("upsample_back", True):                      # 7. optional upsample
        ir8 = cv2.resize(ir8, (w0, h0), interpolation=cv2.INTER_NEAREST)
    return ir8


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_ir(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"Cannot read {path}")
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    maxv = 65535.0 if img.dtype == np.uint16 else 255.0
    return img.astype(np.float32) / maxv


def load_depth(path: Path) -> np.ndarray:
    img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"Cannot read {path}")
    if img.dtype == np.uint16:      # assume millimeters
        return img.astype(np.float32) / DEPTH_MM_SCALE
    return img.astype(np.float32)   # assume meters (e.g. converted EXR)


def save_depth_mm(path: Path, depth_m: np.ndarray) -> None:
    out = np.clip(depth_m * DEPTH_MM_SCALE, 0, 65535).astype(np.uint16)
    cv2.imwrite(str(path), out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="IR/depth sensor degradation and depth-cleanup toolkit")
    ap.add_argument("--modality", choices=["ir", "depth", "depth_clean"], required=True)
    ap.add_argument("--input", required=True, help="Input directory of PNG files")
    ap.add_argument("--output", required=True, help="Output directory")
    ap.add_argument("--preset", choices=list(PRESETS), default="moderate",
                    help="Severity preset (ignored by depth_clean)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    in_dir, out_dir = Path(args.input), Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.modality == "depth_clean":
        cfg, meta_name = OUTLIER_CFG, "depth_outlier_marking.json"
    else:
        cfg = PRESETS[args.preset][args.modality]
        meta_name = f"degradation_{args.modality}_{args.preset}.json"

    meta = {"modality": args.modality, "seed": args.seed, "parameters": cfg}
    if args.modality != "depth_clean":
        meta["preset"] = args.preset
    (out_dir.parent / meta_name).write_text(json.dumps(meta, indent=2))

    files = sorted(in_dir.glob("*.png"))
    print(f"{len(files)} files | modality={args.modality}")

    stats_rows = []
    for i, f in enumerate(files):
        if args.modality == "depth_clean":
            cleaned, inv_frac = mark_depth_outliers(load_depth(f), cfg)
            save_depth_mm(out_dir / f.name, cleaned)
            stats_rows.append((f.name, f"{inv_frac:.6f}"))
        elif args.modality == "depth":
            out = degrade_depth(load_depth(f), cfg, _rng_for(f, args.seed))
            cv2.imwrite(str(out_dir / f.name), out)
        else:  # ir
            out = degrade_ir(load_ir(f), cfg, _rng_for(f, args.seed))
            cv2.imwrite(str(out_dir / f.name), out)
        if (i + 1) % 500 == 0:
            print(f"  {i + 1}/{len(files)}")

    if stats_rows:
        csv_path = out_dir.parent / f"invalid_fraction_{out_dir.name}.csv"
        with open(csv_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["filename", "invalid_fraction"])
            w.writerows(stats_rows)
        fracs = np.array([float(r[1]) for r in stats_rows])
        print(f"invalid fraction: mean={fracs.mean():.4f} "
              f"median={np.median(fracs):.4f} max={fracs.max():.4f}")
        print(f"per-frame stats -> {csv_path}")

    print(f"Done -> {out_dir}")


if __name__ == "__main__":
    main()