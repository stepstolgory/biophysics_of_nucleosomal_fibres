import argparse
import os
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

from mphys.constants import QUANTITIES
from mphys.paths import FIGURES, FONTS, STYLE

QUANTITIES = {
    "rg": dict(symbol=r"R_g", unit=r"\sigma_{LJ}"),
    "ee": dict(symbol=r"R_{ee}", unit=r"\sigma_{LJ}"),
    "fraction": dict(symbol=r"f_{\mathrm{stack}}", unit=None, ylim=(0, 1)),
    "E": dict(symbol=r"$E_{ff}$", unit=r"k_BT"),
    "I": dict(symbol="I", unit=None, ylim=(0, 1)),
    "W": dict(symbol="W", unit=r"k_BT"),
}
TIMESCALE = 1e6
TIME_LABEL = rf"Time steps ($10^{np.log10(1e6)}$)"


def _use_style():
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))


def _stats_text(symbol: str, data: np.ndarray) -> str:
    return (
        rf"$\langle {symbol} \rangle = {data.mean():.2f} \pm {data.std() / np.sqrt(data.size):.1g}$"
        "\n"
        rf"$\sigma = {data.std():.2f}$"
    )


def _label(name: str) -> str:
    q = QUANTITIES.get(name, None)
    if q is not None:
        label = f"{q['symbol']} ({q['unit']})"
        return label
    else:
        warnings.warn(f"{name} doesn't have a QUANTITIES entry. Using default label.")
        return name


def timeseries(
    ax: plt.Axes,
    t: np.ndarray,
    y: np.ndarray,
    q: str,
    t_scale: int = 1e6,
    n_bins: int = 50,
):
    """Plot a variable over time
    ax (plt.Axes) : axes to plot on
    t (np.ndarray) : numpy array of times
    y (np.ndarray) : numpy array of data points
    q (str) : name of quantity to plot
    t_scale (int) : what to scale the time array by. Default 1e6
    n_bins (int) : number of bins for the mean line. Default 50
    """
    _use_style()

    t = t / t_scale  # Scale the timesteps

    t_bins = np.array_split(t, n_bins)

    y_bins = np.array_split(y, n_bins)

    bin_centres = np.array([time.mean() for time in t_bins])
    bin_mean = np.array([v.mean() for v in y_bins])
    bin_std = np.array([v.std() for v in y_bins])

    ax.scatter(t, y, s=2, alpha=0.4, color="grey", label="data")
    ax.error_bar(
        bin_centres,
        bin_mean,
        yerr=bin_std,
        fmt="o-",
        markersize=3,
        capsize=2,
        label=r"binned mean $\pm 1\sigma$",
    )
