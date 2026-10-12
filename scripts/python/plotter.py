import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import os


def _out_name(kind, args):
    if args.o is None or len(args.p) == 1:
        return args.o
    stem, ext = os.path.splitext(args.o)
    return f"{stem}_{kind}{ext}"


def plot_rg_over_time(
    time_data: np.ndarray,
    rg_data: np.ndarray,
    n_bins: int = 50,
    file_name: Path = None,
) -> None:

    time_bins = np.array_split(time_data, n_bins)
    rg_data_bins = np.array_split(rg_data, n_bins)

    bin_centres = np.array([t.mean() for t in time_bins])
    mean = np.array([rg.mean() for rg in rg_data_bins])
    std = np.array([rg.std() for rg in rg_data_bins])

    fig, ax = plt.subplots()

    ax.scatter(time_data, rg_data, s=2, alpha=0.2, color="grey", label="data")
    ax.errorbar(
        bin_centres,
        mean,
        yerr=std,
        fmt="o-",
        markersize=3,
        capsize=2,
        label=r"binned mean $\pm 1 \sigma$",
    )

    ax.set_title(r"Time evolution of radius of gyration, $R_g$")
    ax.set_xlabel("Timestep")
    ax.set_ylabel(r"$R_g$")
    ax.legend()

    mean, std = np.mean(rg_data), np.std(rg_data)
    stats = f"n = {rg_data.size}\nmean = {mean:.2f}\nstd={std:.2f}"
    ax.text(
        0.65,
        0.95,
        stats,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="gray"),
    )

    if file_name is None:
        fig.savefig("figures/rg_over_time.png")
    else:
        fig.savefig(file_name)


def plot_ee_over_time(
    time_data: np.ndarray, ee_data: np.ndarray, n_bins: int = 50, file_name: Path = None
) -> None:

    time_bins = np.array_split(time_data, n_bins)
    ee_data_bins = np.array_split(ee_data, n_bins)

    bin_centres = np.array([t.mean() for t in time_bins])
    mean = np.array([ee.mean() for ee in ee_data_bins])
    std = np.array([ee.std() for ee in ee_data_bins])

    fig, ax = plt.subplots()

    ax.scatter(time_data, ee_data, s=2, alpha=0.2, color="grey", label="data")
    ax.errorbar(
        bin_centres,
        mean,
        yerr=std,
        fmt="o-",
        markersize=3,
        capsize=2,
        label=r"binned mean $\pm 1 \sigma$",
    )

    ax.set_title("Time evolution of end to end distance")
    ax.set_xlabel("Timestep")
    ax.set_ylabel("End to End distance. LJ units")
    ax.legend()

    mean, std = np.mean(ee_data), np.std(ee_data)
    stats = f"n = {ee_data.size}\nmean = {mean:.2f}\nstd={std:.2f}"
    ax.text(
        0.65,
        0.95,
        stats,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="gray"),
    )

    if file_name is None:
        fig.savefig("figures/ee_over_time.png")
    else:
        fig.savefig(file_name)


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
        choices=["rg", "ee"],
        default="rg",
        type=str,
        help="what to plot: rg=Radius of Gyration (default: rg)",
    )
    args = parser.parse_args()

    data = np.loadtxt(args.filepath)

    if "rg" in args.p:
        plot_rg_over_time(data[:, 0], data[:, 1], file_name=_out_name("rg", args))

    if "ee" in args.p:
        plot_ee_over_time(data[:, 0], data[:, 2], file_name=_out_name("ee", args))


if __name__ == "__main__":
    main()
