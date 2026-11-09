import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import BoundaryNorm, ListedColormap

from mphys.paths import DATA, FIGURES, FONTS, STYLE

QUANTITIES = {
    "rg": dict(symbol=r"$R_g$", unit=r"$\sigma_{LJ}$"),
    "ee": dict(symbol=r"$R_{ee}$", unit=r"$\sigma_{LJ}$"),
    "fraction": dict(symbol=r"$f_{\mathrm{stack}}$", unit=None, ylim=(0, 1)),
    "E": dict(symbol=r"$E_{ff}$", unit=r"$k_BT$"),
    "I": dict(symbol="I", unit=None),
}
TIME_SCALE = 1e6
TIME_LABEL = rf"Time steps ($10^{int(np.log10(TIME_SCALE))}$)"


def _entry(name: str) -> dict:
    """
    Returns the QUANTITIES entry for a column name.
        name : str - Column name from a data file

    Returns: dict of the quantity's settings, or an empty dict if it has no entry
    """
    return QUANTITIES.get(name, {})


def stats_text(y: np.ndarray, name: str) -> str:
    """
    Mean and SD of one run, for a legend title.
        y : np.ndarray - Values of the quantity
        name : str - Column name, used to look up its symbol

    Returns: two lines of text, <symbol> = mean and sigma = SD
    """
    symbol = _entry(name).get("symbol", rf"\mathrm{{{name}}}").strip("$")
    return (
        rf"$\langle {symbol} \rangle = {y.mean():.2f}$"
        "\n"
        rf"$\sigma = {y.std():.2f}$"
    )


def use_style():
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))


def label(name: str) -> str:
    q = QUANTITIES.get(name, None)
    if q is not None:
        if q["unit"] is not None:
            label = f"{q['symbol']} ({q['unit']})"
        else:
            label = f"{q['symbol']}"
        return label
    else:
        warnings.warn(f"{name} doesn't have a QUANTITIES entry. Using default label.")
        return name


def timeseries(
    ax: plt.Axes,
    t: np.ndarray,
    y: np.ndarray,
    name: str,
    n_bins: int = 50,
    raw: bool = True,
    **kw,
) -> plt.Axes:
    """Plot a variable over time
    ax (plt.Axes) : axes to plot on
    t (np.ndarray) : numpy array of times
    y (np.ndarray) : numpy array of data points
    name (str) : name of quantity to plot
    n_bins (int) : number of bins for the mean line. Default 50
    raw (bool) : plot gray points of raw data if True. Default True
    **kw : passed on to ax.errorbar (e.g. color, alpha, label)

    Returns: the axes plotted on
    """
    n_bins = min(n_bins, len(t))  # No empty bins for short runs

    t = t / TIME_SCALE  # Scale the timesteps

    t_bins = np.array_split(t, n_bins)

    y_bins = np.array_split(y, n_bins)

    bin_centres = np.array([time.mean() for time in t_bins])
    bin_mean = np.array([v.mean() for v in y_bins])
    bin_std = np.array([v.std() for v in y_bins])

    if raw:
        ax.scatter(t, y, s=2, alpha=0.4, color="grey", label="data")

    # Defaults for the mean line, anything in kw replaces them
    kw.setdefault("fmt", "o-")
    kw.setdefault("markersize", 3)
    kw.setdefault("capsize", 2)
    kw.setdefault("label", r"binned mean $\pm 1\sigma$")

    ax.errorbar(bin_centres, bin_mean, yerr=bin_std, **kw)

    ax.set_xlabel(TIME_LABEL)
    ax.set_ylabel(label(name))

    ylim = _entry(name).get("ylim")
    if ylim is not None:
        ax.set_ylim(ylim)

    return ax


def histogram(
    ax: plt.Axes, y: np.ndarray, name: str, n_bins: int = 50, **kw
) -> plt.Axes:
    """Plot a histogram of a variable
    ax (plt.Axes) : axes to plot on
    y (np.ndarray) : numpy array of data points
    name (str) : name of quantity to plot
    n_bins (int) : number of bins for the histogram
    **kw : passed on to ax.stairs

    Returns: the axes plotted on
    """
    count, bins = np.histogram(y, n_bins, density=True)

    ax.stairs(count, bins, **kw)

    ax.set_xlabel(label(name))
    ax.set_ylabel("Probability density")

    xlim = _entry(name).get("ylim")
    if xlim is not None:
        ax.set_xlim(xlim)
    return ax


def savefig(fig: plt.Figure, path: Path | str) -> None:
    """
    Saves a figure, making its folder first if needed, then closes it.
        fig : plt.Figure - Figure to save
        path : Path | str - Where to save it. The extension sets the format (.png, .pdf, ...)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def default_out(input_path: Path | str, plot_kind: str) -> Path:
    """
    Default output path for a plot made from a data file.
        input_path : Path | str - Data file the plot is made from
        plot_kind : str - Kind of plot, added to the name (e.g. "ts", "hist", "kymo")

    Returns: figures/<same sub-folder>/<input stem>_<plot_kind>.png if the input is inside
             data_files/, otherwise the same name next to the input
    """
    input_path = Path(input_path).resolve()
    name = f"{input_path.stem}_{plot_kind}.png"
    if input_path.is_relative_to(DATA):
        return FIGURES / input_path.parent.relative_to(DATA) / name
    return input_path.parent / name


# Kymograph colours: free, gap 1, gap 2 (the ladder), gap 3, gap 4 or more.
# Shared with the which-neighbour bars, so a gap always has the same colour.
GAP_COLOURS = ["#f2f2f2", "#e00000", "#0066cc", "#ff7f0e", "#808080"]
GAP_LABELS = ["free", "1", "2", "3", "4+"]


def kymograph(ax: plt.Axes, t: np.ndarray, gaps: np.ndarray):
    """
    Plot which neighbour each face is stacked with, over time.
        ax : plt.Axes - Axes to plot on
        t : np.ndarray - Timesteps, shape (F,)
        gaps : np.ndarray - Gap along the chain for every face (from partner_gaps), shape (F, 2N).
               0 is a free face. Gaps of 4 or more get the same colour.

    Returns: the QuadMesh from pcolormesh, for fig.colorbar
    """
    gaps = np.clip(gaps, 0, len(GAP_COLOURS) - 1)
    rows = np.arange(gaps.shape[1])  # One row per face: n0+, n0-, n1+, n1-, ...

    # One colour per whole number: edges at -0.5, 0.5, ..., 4.5
    cmap = ListedColormap(GAP_COLOURS)
    norm = BoundaryNorm(np.arange(len(GAP_COLOURS) + 1) - 0.5, cmap.N)
    mesh = ax.pcolormesh(
        t / TIME_SCALE, rows, gaps.T, cmap=cmap, norm=norm, shading="nearest"
    )

    # Plus face on row 2i, minus face on row 2i + 1
    N = gaps.shape[1] // 2
    face_labels = [f"{i}{side}" for i in range(N) for side in ("+", "-")]
    ax.set_yticks(rows, face_labels, fontsize=6)
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_ylabel("Nucleosome")
    ax.set_xlabel(TIME_LABEL)
    return mesh
