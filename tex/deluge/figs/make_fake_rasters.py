"""Generate fake 16x16 hydromet rasters across 7 timesteps per variable.

Style: noisy weather-field look — smoothed Gaussian random fields with
variable-specific transforms (heavy tails for precip, slow drift for
soil moisture, snow mask for SWE, etc.). Each timestep is saved as a
standalone PNG, plus a per-variable contact sheet.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

OUT_DIR = "fake_rasters"
N = 16
T = 7
SEED = 11

os.makedirs(OUT_DIR, exist_ok=True)


def grf(n, sigma, rng):
    """Gaussian random field: white noise smoothed to a length scale."""
    z = rng.standard_normal((n, n))
    z = gaussian_filter(z, sigma=sigma)
    return (z - z.mean()) / (z.std() + 1e-9)


def temporal_grf(n, t, sigma_s, sigma_t, rng):
    """Spatio-temporal GRF — smooth in space AND time so timesteps
    look related but not identical (like real daily weather)."""
    z = rng.standard_normal((t, n, n))
    z = gaussian_filter(z, sigma=(sigma_t, sigma_s, sigma_s))
    z = (z - z.mean()) / (z.std() + 1e-9)
    return z


def multiscale(n, t, scales, weights, sigma_t, rng):
    """Sum of GRFs at several spatial scales — gives both broad
    structure and fine-grained texture (looks like real weather)."""
    out = np.zeros((t, n, n))
    for s, w in zip(scales, weights):
        out += w * temporal_grf(n, t, sigma_s=s, sigma_t=sigma_t, rng=rng)
    out = (out - out.mean()) / (out.std() + 1e-9)
    return out


# Shared "soil-moisture-style" base: smooth multi-scale field + fine texture.
# `sigma_t` controls how fast the pattern evolves day-to-day.
def smooth_field(rng, sigma_t, contrast=1.0):
    base = multiscale(N, T, scales=[2.5, 1.0, 0.4],
                      weights=[1.0, 0.95, 0.55], sigma_t=sigma_t, rng=rng)
    fine = temporal_grf(N, T, sigma_s=0.35, sigma_t=max(0.4, sigma_t * 0.3),
                        rng=np.random.default_rng(rng.integers(1e9)))
    return contrast * base + 0.25 * fine


def to_range(z, lo, hi):
    # rescale a zero-mean field to [lo, hi] using its 2/98 percentiles
    p2, p98 = np.quantile(z, 0.02), np.quantile(z, 0.98)
    z = np.clip((z - p2) / (p98 - p2 + 1e-9), 0, 1)
    return lo + (hi - lo) * z


def make_precip(rng):
    z = smooth_field(rng, sigma_t=0.9, contrast=1.15)
    return to_range(z, 0.0, 28.0)        # mm/day


def make_antecedent(precip):
    # running 3-day sum — smoother and larger
    out = np.zeros_like(precip)
    for t in range(T):
        lo = max(0, t - 2)
        out[t] = precip[lo:t + 1].sum(axis=0)
    return out


def make_soil_moisture(rng, precip):
    base = smooth_field(rng, sigma_t=2.5, contrast=1.0)
    cum = np.cumsum(precip, axis=0)
    cum = (cum - cum.min()) / (cum.max() - cum.min() + 1e-9)
    f = to_range(base, 0.10, 0.45) + 0.08 * cum
    return np.clip(f, 0.05, 0.55)


def make_runoff(rng, precip):
    # correlated with precip but with its own multi-scale structure on top
    z = smooth_field(rng, sigma_t=1.0, contrast=1.1)
    pnorm = precip / (precip.max() + 1e-9)
    f = to_range(z, 0.0, 8.0) + 6.0 * pnorm
    return np.clip(f, 0, None)


def make_swe(rng):
    # gentle elevation bias built into the field itself, no hard masking
    y, x = np.mgrid[0:N, 0:N]
    elev = (np.exp(-(((x - 4) ** 2 + (y - 3) ** 2) / (2 * 7.0 ** 2)))
            + 0.7 * np.exp(-(((x - 11) ** 2 + (y - 6) ** 2) / (2 * 5.0 ** 2))))
    elev = elev / elev.max()
    z = smooth_field(rng, sigma_t=3.0, contrast=1.1)
    f = to_range(z, 0.0, 1.0) * (0.35 + 0.65 * elev[None])
    return to_range(f, 0.0, 140.0)


# build everything from one seed chain so it's reproducible
rng = np.random.default_rng(SEED)
precip = make_precip(rng)
antec  = make_antecedent(precip)
sm     = make_soil_moisture(rng, precip)
runoff = make_runoff(rng, precip)
swe    = make_swe(rng)

VARS = [
    ("precipitation",        precip, "Blues"),
    ("antecedent_precip_3d", antec,  "PuBu"),
    ("soil_moisture",        sm,     "YlGnBu"),
    ("runoff",               runoff, "GnBu"),
    ("swe",                  swe,    "BuPu"),
]


def save_raster(arr2d, path, cmap, vmin, vmax):
    fig, ax = plt.subplots(figsize=(1.6, 1.6), dpi=220)
    ax.imshow(arr2d, cmap=cmap, interpolation="nearest", vmin=vmin, vmax=vmax)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    fig.savefig(path, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close(fig)


for name, stack, cmap in VARS:
    sub = os.path.join(OUT_DIR, name)
    os.makedirs(sub, exist_ok=True)
    np.save(os.path.join(sub, f"{name}.npy"), stack)

    # per-timestep percentile stretch so each frame fills its colormap —
    # makes the structure visible even on days with weaker signal
    for t in range(T):
        frame = stack[t]
        vmin = float(np.quantile(frame, 0.02))
        vmax = float(np.quantile(frame, 0.98))
        if vmax <= vmin:
            vmax = vmin + 1.0
        save_raster(frame, os.path.join(sub, f"{name}_t{t:02d}.png"),
                    cmap, vmin, vmax)

    # shared scale for the contact-sheet so cross-day comparison still works
    vmin_s = float(np.quantile(stack, 0.02))
    vmax_s = float(np.quantile(stack, 0.98))

    # contact sheet (1 x T strip)
    fig, axes = plt.subplots(1, T, figsize=(T * 1.4, 1.4), dpi=180)
    for t, ax in enumerate(axes):
        ax.imshow(stack[t], cmap=cmap, interpolation="nearest",
                  vmin=vmin_s, vmax=vmax_s)
        ax.set_axis_off()
        ax.set_title(f"t{t}", fontsize=8)
    fig.suptitle(name, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, f"{name}_strip.png"),
                bbox_inches="tight", dpi=180, transparent=True)
    plt.close(fig)

    print(f"{name:24s}  shape={stack.shape}  "
          f"min={stack.min():7.3f}  p99={np.quantile(stack,0.99):7.3f}")

print(f"\nPNGs + .npy in ./{OUT_DIR}/  (per-variable subdirs + strip overviews)")
