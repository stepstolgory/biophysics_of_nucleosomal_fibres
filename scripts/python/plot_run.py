"""
Plot a quantity from per-run data files against time, and as a histogram.

Reads files written by the analysis scripts, for example
    data_files/sweep02/E8.0_I0.2_W10.0_r1_rg.dat
with a timestep column and one or more quantity columns. The column names come from
the file's header (the last line starting with '#'), so the labels always match the data.

Usage:
    python plot_run.py FILE [FILE ...]                    # one time series per file
    python plot_run.py FILE -p ts hist                    # time series and histogram
    python plot_run.py FILE -c gap2                       # a column other than the first
    python plot_run.py data_files/sweep02/E8.0_I0.2_W10.0_r*_rg.dat --overlay -o figures/sweep02/rg_E8.0_I0.2.png

Output (unless -o or --outdir is given): figures/<same sub-folder>/<file stem>_<ts|hist>.png
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mphys.funcs import read_table
from mphys.plotting import (
    default_out,
    histogram,
    savefig,
    stats_text,
    timeseries,
    use_style,
)

PLOT_KINDS = ["ts", "hist"]


def load_column(path: Path, column: str | None) -> tuple[np.ndarray, np.ndarray, str]:
    """
    Load the time and one quantity column from a data file.
        path : Path - Data file
        column : str | None - Column to load. None means the first column after timestep

    Returns: times, values and the column name
    """
    names, data = read_table(path)
    if "timestep" not in names:
        raise ValueError(
            f"{path} has no 'timestep' column (columns: {' '.join(names)})"
        )
    if column is None:
        column = next(name for name in names if name != "timestep")
    if column not in names:
        raise ValueError(
            f"{path} has no column '{column}' (columns: {' '.join(names)})"
        )
    return data[:, names.index("timestep")], data[:, names.index(column)], column


def draw(
    ax: plt.Axes, kind: str, t: np.ndarray, y: np.ndarray, name: str, n_bins: int, **kw
) -> plt.Axes:
    """Draw one kind of plot ("ts" or "hist") on the axes"""
    if kind == "ts":
        return timeseries(ax, t, y, name, n_bins=n_bins, **kw)
    return histogram(ax, y, name, n_bins=n_bins, **kw)


def out_path(input_path: Path, kind: str, args) -> Path:
    """Where to save a plot: -o if given, otherwise the default name (in --outdir if given)"""
    if args.o is not None:
        out = Path(args.o)
        # With more than one kind of plot, tell them apart: rg.png -> rg_ts.png, rg_hist.png
        if len(args.p) > 1:
            out = out.with_name(f"{out.stem}_{kind}{out.suffix}")
        return out

    # A column chosen with -c goes in the name too, so it can't overwrite the default
    # column's plot: ..._stacking_ts.png and ..._stacking_gap2_ts.png
    if args.c is not None and not input_path.stem.endswith(f"_{args.c}"):
        kind = f"{args.c}_{kind}"

    out = default_out(input_path, kind)
    if args.outdir is not None:
        out = Path(args.outdir) / out.name
    return out


def finish(fig: plt.Figure, out: Path, show: bool) -> None:
    """Save the figure, or keep it open for plt.show()"""
    if show:
        return
    savefig(fig, out)
    print(f"Saved {out}")


def plot_each(args) -> None:
    """One figure per file and kind of plot"""
    for path in args.files:
        t, y, name = load_column(path, args.c)
        for kind in args.p:
            fig, ax = plt.subplots()
            draw(ax, kind, t, y, name, args.bins)
            if kind == "ts":
                # "best" moves the legend off the data, the style's default is upper right
                ax.legend(
                    title=stats_text(y, name),
                    alignment="left",
                    title_fontsize="medium",
                    loc="best",
                )
            else:
                ax.legend(
                    handles=[],
                    title=stats_text(y, name),
                    alignment="left",
                    title_fontsize="medium",
                )
            ax.set_title(path.stem, fontsize="small")
            finish(fig, out_path(path, kind, args), args.show)


def plot_overlay(args) -> None:
    """One figure per kind of plot, with every file on it"""
    runs = [load_column(path, args.c) for path in args.files]

    names = {name for _, _, name in runs}
    if len(names) > 1:
        raise ValueError(f"Files have different columns: {' '.join(sorted(names))}")

    for kind in args.p:
        fig, ax = plt.subplots()
        for i, (t, y, name) in enumerate(runs):
            # The repeats are interchangeable, so one colour and one legend entry for all
            run_label = f"{len(runs)} runs" if i == 0 else "_nolegend_"
            if kind == "ts":
                draw(
                    ax,
                    kind,
                    t,
                    y,
                    name,
                    args.bins,
                    raw=False,
                    color="C0",
                    alpha=0.4,
                    label=run_label,
                )
            else:
                draw(
                    ax,
                    kind,
                    t,
                    y,
                    name,
                    args.bins,
                    color="C0",
                    alpha=0.5,
                    label=run_label,
                )
        ax.legend()
        finish(fig, out_path(args.files[0], kind, args), args.show)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("files", nargs="+", type=Path, help="Data files to plot")
    parser.add_argument(
        "-p",
        nargs="+",
        choices=PLOT_KINDS,
        default=["ts"],
        help="What to plot: ts = against time, hist = histogram. Default ts",
    )
    parser.add_argument(
        "-c",
        type=str,
        default=None,
        help="Column to plot. Default: the first column after timestep",
    )
    parser.add_argument(
        "--overlay",
        action="store_true",
        help="Put all the files on one plot instead of one plot each. Needs -o",
    )
    parser.add_argument(
        "-o",
        type=str,
        default=None,
        help="Output file. Needs --overlay if more than one file is given",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=None,
        help="Folder for the output files, keeping their default names",
    )
    parser.add_argument(
        "--bins", type=int, default=50, help="Number of bins. Default 50"
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the plots instead of saving them",
    )
    args = parser.parse_args()

    if args.overlay and args.o is None and not args.show:
        parser.error(
            "--overlay needs -o, as there is no single input file to name the plot after"
        )
    if not args.overlay and args.o is not None and len(args.files) > 1:
        parser.error("-o with more than one file needs --overlay (or use --outdir)")

    use_style()

    try:
        if args.overlay:
            plot_overlay(args)
        else:
            plot_each(args)
    except ValueError as e:
        parser.error(str(e))

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
