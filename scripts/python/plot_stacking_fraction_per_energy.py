"""
Plot the mean of one column of a summary file against (E, I).

Reads a summary_<kind>.dat file made by combine_runs.py.

Usage:
    python plot_stacking_fraction_per_energy.py SUMMARY [-c COLUMN] [--show] [-o OUT]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mphys.funcs import read_table
from mphys.plotting import default_out, label, savefig, use_style


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "summary", type=Path, help="summary_<kind>.dat from combine_runs.py"
    )
    parser.add_argument(
        "-c",
        "--column",
        default="fraction",
        help="Column to plot (without _mean). Default fraction",
    )
    parser.add_argument(
        "--show", action="store_true", help="Display the plot instead of saving it"
    )
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=None,
        help="Where to save. Default: figures/<sweep>/summary_<kind>_<column>_perE.png",
    )
    args = parser.parse_args()

    names, data = read_table(args.summary)
    if f"{args.column}_mean" not in names:
        parser.error(f"{args.summary.name} has no column {args.column}_mean")

    E = data[:, names.index("E")]
    I = data[:, names.index("I")]
    n = data[:, names.index("n")]
    mean = data[:, names.index(f"{args.column}_mean")]
    se = data[:, names.index(f"{args.column}_se")]

    order = np.lexsort((E, I))  # sort by I, then by E within each I
    E, I, n, mean, se = E[order], I[order], n[order], mean[order], se[order]
    ticks = [f"({e:g}, {i:g})" for e, i in zip(E, I)]

    use_style()
    x = np.arange(len(ticks))  # evenly spaced positions 0, 1, 2, ...
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.errorbar(x, mean, yerr=se, fmt="o", capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels(ticks, rotation=45, ha="right")
    ax.tick_params(axis="x", which="minor", bottom=False, top=False)
    ax.set_xlabel(r"$(E_{ff}, I)$")
    ax.set_ylabel(r"$\langle$" + label(args.column) + r"$\rangle$")
    if args.column == "fraction":
        ax.set_ylim(0, 1)
    n_text = f"{n.min():g}" if n.min() == n.max() else f"{n.min():g} to {n.max():g}"
    ax.set_title(f"Error bars: SE over n = {n_text} runs", fontsize="small")
    fig.tight_layout()

    if args.show:
        plt.show()
    else:
        out = args.out or default_out(args.summary, f"{args.column}_perE")
        savefig(fig, out)
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
