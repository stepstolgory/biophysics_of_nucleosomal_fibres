import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import os
from matplotlib import font_manager

STYLE_DIR = Path(__file__).parent / "style"
for f in (STYLE_DIR / "fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(f))
plt.style.use(STYLE_DIR / "atlas.mplstyle")


def _out_name(kind, args):
    if args.o is None or len(args.p) == 1:
        return args.o

    stem, ext = os.path.splitext(args.o)
    return f"{stem}_{kind}{ext}"


def _stats_text(symbol: str, data: np.ndarray) -> str:
    return (
        rf"$\langle {symbol} \rangle = {data.mean():.2f} \pm {data.std() / np.sqrt(data.size):.1g}$"
        "\n"
        rf"$\sigma = {data.std():.2f}$"
    )


def _finish(fig, file_name, default_name: str, show: bool) -> None:
    if show:
        return

    if file_name is None:
        file_name = Path("figures") / default_name
    Path(file_name).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(file_name)
    plt.close(fig)


def _plot_over_time(
    time_data: np.ndarray,
    values: np.ndarray,
    symbol: str,
    n_bins: int,
    file_name,
    default_name: str,
    show: bool,
) -> None:
    """Shared code for the 'quantity over time' plots."""
    time = time_data / 1e6  # in millions of steps

    time_bins = np.array_split(time, n_bins)

    value_bins = np.array_split(values, n_bins)

    bin_centres = np.array([t.mean() for t in time_bins])
    bin_mean = np.array([v.mean() for v in value_bins])
    bin_std = np.array([v.std() for v in value_bins])

    fig, ax = plt.subplots()

    ax.scatter(time, values, s=2, alpha=0.4, color="grey", label="data")
    ax.errorbar(
        bin_centres,
        bin_mean,
        yerr=bin_std,
        fmt="o-",
        markersize=3,
        capsize=2,
        label=r"binned mean $\pm 1\sigma$",
    )

    ax.set_xlabel(r"Timestep ($10^6$)")
    ax.set_ylabel(rf"${symbol}$")
    ax.legend(
        title=_stats_text(symbol, values), alignment="left", title_fontsize="medium"
    )

    _finish(fig, file_name, default_name, show)


def _plot_histogram(
    values: np.ndarray,
    symbol: str,
    n_bins: int,
    file_name,
    default_name: str,
    show: bool,
) -> None:
    """Shared code for the histogram plots."""
    count, bins = np.histogram(values, n_bins, density=True)

    fig, ax = plt.subplots()

    ax.stairs(count, bins)

    ax.set_xlabel(rf"${symbol}$")
    ax.set_ylabel("Probability density")

    ax.legend(
        handles=[],
        title=_stats_text(symbol, values),
        alignment="left",
        title_fontsize="medium",
        loc="best",
    )

    _finish(fig, file_name, default_name, show)


def plot_rg_over_time(
    time_data: np.ndarray,
    rg_data: np.ndarray,
    n_bins: int = 50,
    file_name: Path = None,
    show: bool = False,
) -> None:
    _plot_over_time(
        time_data, rg_data, "R_g", n_bins, file_name, "rg_over_time.png", show
    )


def plot_ee_over_time(
    time_data: np.ndarray,
    ee_data: np.ndarray,
    n_bins: int = 50,
    file_name: Path = None,
    show: bool = False,
) -> None:
    _plot_over_time(
        time_data, ee_data, "R_{ee}", n_bins, file_name, "ee_over_time.png", show
    )


def plot_rg_histogram(
    rg_data: np.ndarray,
    n_bins: int = 50,
    file_name: Path = None,
    show: bool = False,
) -> None:
    _plot_histogram(rg_data, "R_g", n_bins, file_name, "rg_histogram.png", show)


def plot_ee_histogram(
    ee_data: np.ndarray,
    n_bins: int = 50,
    file_name: Path = None,
    show: bool = False,
) -> None:
    _plot_histogram(ee_data, "R_{ee}", n_bins, file_name, "ee_histogram.png", show)


def main():
    parser = argparse.ArgumentParser(
        description="Various plotting functions for nucleosome quantities."
    )

    parser.add_argument("filepath", help="Path to data file to be plotted")

    parser.add_argument(
        "-o",
        type=str,
        help="output file. (Separate defaults for each plotting functions.",
        default=None,
    )

    parser.add_argument(
        "-p",
        nargs="+",
        choices=["rg", "rgh", "ee", "eeh"],
        default=["rg"],
        type=str,
        help="what to plot: rg=Radius of Gyration over time\nrgh=Radius of gyration histogram\nee=End-to-end distance over time\neeh=End-to-end distance histogram\ndefault=rg",
    )

    parser.add_argument(
        "--show",
        default=False,
        action="store_true",
        help="Display plots at runtime instead of saving.",
    )

    args = parser.parse_args()

    data = np.loadtxt(args.filepath)

    if "rg" in args.p:
        plot_rg_over_time(
            data[:, 0], data[:, 1], file_name=_out_name("rg", args), show=args.show
        )

    if "ee" in args.p:
        plot_ee_over_time(
            data[:, 0], data[:, 2], file_name=_out_name("ee", args), show=args.show
        )

    if "rgh" in args.p:
        plot_rg_histogram(data[:, 1], file_name=_out_name("rgh", args), show=args.show)

    if "eeh" in args.p:
        plot_ee_histogram(data[:, 2], file_name=_out_name("eeh", args), show=args.show)

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
