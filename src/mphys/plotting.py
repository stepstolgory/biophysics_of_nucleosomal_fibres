import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import os
from matplotlib import font_manager
from mphys.paths import STYLE, FONTS, FIGURES
from mphys.constants import QUANTITIES


def use_style():
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))


def _stats_text(symbol: str, data: np.ndarray) -> str:
    return (
        rf"$\langle {symbol} \rangle = {data.mean():.2f} \pm {data.std() / np.sqrt(data.size):.1g}$"
        "\n"
        rf"$\sigma = {data.std():.2f}$"
    )


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
    use_style()

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
