"""
Plot mean stacking fraction per energy

Usage:
    python plot_stacking_fraction_per_energy.py filepath [--show] [-o]
"""

import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
from matplotlib import font_manager

from mphys.funcs import read_table, parse_run_name
from mphys.paths import FONTS, STYLE, FIGURES
from mphys.plotting import timeseries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "datadir",
        type=Path,
        help="Path to a directory containing a sweeps _stackings files",
    )
    parser.add_argument(
        "--show", action="store_true", help="Display the plot instead of saving it"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=f"{FIGURES}/kymograph.png",
        help=f"Filepath to save plot to. Default: {FIGURES}/kymograph.png",
    )

    args = parser.parse_args()

    files = sorted(args.datadir.glob("*_stacking.dat"))
    if not files:
        parser.error(f"no *_stacking.dat files in {args.datadir}")

    groups = defaultdict(list)
    for path in files:
        params = parse_run_name(path)
        if params is None:
            print(f"Skipping {path.name}: name doesn't match the pattern")
            continue
        groups[(params["E"], params["I"])].append(path)

    rows = []
    for (E, I), paths in sorted(groups.items()):
        run_means = []
        for path in paths:
            names, data = read_table(path)
            run_means.append(data[:, 1].mean(axis=0))

        run_means = np.array(run_means)

        n = len(run_means)
        mean = run_means.mean(axis=0)
        if n > 1:
            sd = run_means.std(axis=0, ddof=1)
            se = sd / np.sqrt(n)
        else:
            sd = se = np.full_like(mean, np.nan)

        rows.append([E, I, n, mean, sd, se])

    # Now I need to pick out the data properly. For each row I need to get:
    # an x-label: (E, I)
    # the mean fraction to plot: mean
    # the standard error on the mean: se
    ticks = []
    means = []
    errors = []
    for E, I, n, mean, sd, se in rows:
        ticks.append(f"({E},{I})")
        means.append(mean)
        errors.append(se)
    print(ticks)
    print(means)
    print(errors)


if __name__ == "__main__":
    main()
