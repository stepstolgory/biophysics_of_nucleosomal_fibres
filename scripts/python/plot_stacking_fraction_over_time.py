"""
Stacking fraction over time.

Usage:
    python plot_stacking_fraction_over_time.py filename [--show] [-o output_path]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

from mphys.funcs import read_table
from mphys.paths import FONTS, STYLE, FIGURES
from mphys.plotting import timeseries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=Path, help="Path to a _stackings.dat file")
    parser.add_argument(
        "--show", action="store_true", help="Display the plot instead of saving it"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=f"{FIGURES}/stackings_over_time.png",
        help=f"Filepath to save plot to. Default: {FIGURES}/stackings_over_time.png",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        default=False,
        help="Plot raw data points on graph",
    )
    args = parser.parse_args()

    # Make sure the styles all match
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))

    names, data = read_table(args.filepath)
    t = data[:, names.index("timestep")]
    fractions = data[:, names.index("fraction")]

    fig, ax = plt.subplots()
    ax = timeseries(ax, t, fractions, "fraction", raw=args.raw)

    if args.show:
        plt.show()
    else:
        out = args.out
        fig.savefig(out)
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
