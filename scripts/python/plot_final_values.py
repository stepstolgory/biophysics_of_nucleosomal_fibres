#!/usr/bin/env python3
"""
Plot the final value of Rg and R_ee on an E-I grid, averaged over repeats.

Reads every file in DIR named
    E<float>_I<float>_W<float>_r<int>_<rg|ee>.dat
Each file has two space-separated columns: timestep and value. Any line that
isn't two numbers (for example the "timestep value" header, or lines starting
with '#') is skipped.

For each file it takes the final value (or, with --last N, the mean of the last
N values). Files with the same E, I and W but a different r are repeats, so
these are averaged.

Outputs, for each quantity (rg, ee) and each W value found:
    final_<q>_W<W>.dat   one row per (E, I):  E I mean SD SE n
    final_<q>_W<W>.png   colour map: I on x, E on y, colour = mean over repeats

Usage:
    python plot_final_values.py DIR
    python plot_final_values.py DIR --last 100     # mean of the last 100 rows of each file
    python plot_final_values.py DIR --outdir plots --show

"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

FLOAT = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
NAME_RE = re.compile(
    rf"^E(?P<E>{FLOAT})_I(?P<I>{FLOAT})_W(?P<W>{FLOAT})_r(?P<rep>\d+)_(?P<q>rg|ee)\.dat$"
)

NAMES = {"rg": "Rg", "ee": "end-to-end distance"}
LABELS = {"rg": r"$R_g$ ($\sigma_{LJ}$)", "ee": r"$R_{ee}$ ($\sigma_{LJ}$)"}


def read_tail(path, last):
    """Return (final timestep, mean of the last `last` values, rows used), or None if no data."""
    rows = []
    with open(path) as f:
        for line in f:
            parts = line.replace(",", " ").split()
            if len(parts) < 2:
                continue
            try:
                rows.append((float(parts[0]), float(parts[1])))

            except ValueError:
                continue  # header or comment line
    if not rows:
        return None
    tail = rows[-last:]
    return rows[-1][0], float(np.mean([v for _, v in tail])), len(tail)


def collect(directory, last):
    """Group the final values by (quantity, W, E, I). Each group is a list of (rep, final_step, value)."""
    groups = defaultdict(list)
    skipped = []
    for path in sorted(directory.glob("*.dat")):
        m = NAME_RE.match(path.name)
        if not m:
            skipped.append(path.name)
            continue
        res = read_tail(path, last)
        if res is None:
            print(f"warning: no data in {path.name}, skipped", file=sys.stderr)
            continue
        step, value, n_used = res
        if n_used < last:
            print(
                f"warning: {path.name} has only {n_used} rows (asked for --last {last})",
                file=sys.stderr,
            )
        key = (m["q"], float(m["W"]), float(m["E"]), float(m["I"]))

        groups[key].append((int(m["rep"]), step, value))
    if skipped:
        print(
            f"note: {len(skipped)} .dat file(s) don't match the name pattern and were ignored, "
            f"e.g. {skipped[0]}",
            file=sys.stderr,
        )
    return groups


def summarise(runs):
    """Mean, SD, SE and n over repeats. SD and SE are NaN if there is only one repeat."""
    vals = np.array([v for _, _, v in runs])
    n = len(vals)
    mean = vals.mean()
    sd = vals.std(ddof=1) if n > 1 else np.nan
    se = sd / np.sqrt(n) if n > 1 else np.nan
    return mean, sd, se, n


def plot_grid(Es, Is, mean, se, n, q, W, last, outfile, show):

    fig, ax = plt.subplots(figsize=(1.6 * len(Is) + 3.0, 0.6 * len(Es) + 2.5))
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("lightgrey")  # (E, I) points with no runs
    im = ax.imshow(np.ma.masked_invalid(mean), origin="lower", aspect="auto", cmap=cmap)

    # One cell per parameter value, labelled with the value (spacing is not to scale)
    ax.set_xticks(range(len(Is)))
    ax.set_xticklabels([f"{v:g}" for v in Is])
    ax.set_yticks(range(len(Es)))
    ax.set_yticklabels([f"{v:g}" for v in Es])
    ax.set_xlabel(r"$I$")
    ax.set_ylabel(r"$E_{ff}$")

    # Write mean, SE and number of repeats in each cell
    for i in range(len(Es)):
        for j in range(len(Is)):
            if np.isnan(mean[i, j]):
                continue
            text = f"{mean[i, j]:.2f}"

            if not np.isnan(se[i, j]):
                text += f"\n± {se[i, j]:.2f}"
            text += f"\nn = {n[i, j]}"

            colour = "black" if im.norm(mean[i, j]) > 0.5 else "white"

            ax.text(j, i, text, ha="center", va="center", fontsize=8, color=colour)

    what = "final value" if last == 1 else f"mean of last {last} values"

    ax.set_title(f"{NAMES[q]}: {what}, averaged over repeats (W = {W:g})", fontsize=10)

    fig.colorbar(im, ax=ax, label=LABELS[q])
    fig.tight_layout()
    fig.savefig(outfile, dpi=200)
    if not show:
        plt.close(fig)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "directory", type=Path, help="folder holding the *_rg.dat and *_ee.dat files"
    )
    p.add_argument(
        "--last",
        type=int,
        default=1,
        help="average the last N values of each file instead of taking only the final one "
        "(default 1)",
    )
    p.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="where to write the .dat and .png files (default: the input folder)",
    )
    p.add_argument(
        "--show", action="store_true", help="also open the plots in a window"
    )
    args = p.parse_args()

    if not args.directory.is_dir():
        sys.exit(f"error: {args.directory} is not a folder")
    if args.last < 1:
        sys.exit("error: --last must be at least 1")
    outdir = args.outdir or args.directory
    outdir.mkdir(parents=True, exist_ok=True)

    groups = collect(args.directory, args.last)

    if not groups:
        sys.exit(
            f"error: no files matching E<E>_I<I>_W<W>_r<rep>_<rg|ee>.dat in {args.directory}"
        )

    for q in ("rg", "ee"):
        for W in sorted({k[1] for k in groups if k[0] == q}):
            keys = sorted(k for k in groups if k[0] == q and k[1] == W)
            Es = sorted({k[2] for k in keys})
            Is = sorted({k[3] for k in keys})
            mean = np.full((len(Es), len(Is)), np.nan)
            se = np.full_like(mean, np.nan)

            n = np.zeros(mean.shape, dtype=int)

            stem = f"final_{q}_W{W:g}"
            rows = []
            for key in keys:
                _, _, E, I = key
                runs = groups[key]
                steps = {s for _, s, _ in runs}
                if len(steps) > 1:
                    detail = ", ".join(f"r{r}: {s:g}" for r, s, _ in sorted(runs))
                    print(
                        f"warning: {q} at E={E:g} I={I:g} W={W:g}: repeats end at different "
                        f"timesteps (crashed run?) {detail}",
                        file=sys.stderr,
                    )
                m_, sd_, se_, n_ = summarise(runs)

                i, j = Es.index(E), Is.index(I)
                mean[i, j], se[i, j], n[i, j] = m_, se_, n_
                rows.append(f"{E:g} {I:g} {m_:.6g} {sd_:.6g} {se_:.6g} {n_}")

            what = (
                "final value" if args.last == 1 else f"mean of last {args.last} values"
            )
            with open(outdir / f"{stem}.dat", "w") as f:

                f.write(f"# {NAMES[q]} ({what} of each run), averaged over repeats\n")

                f.write(f"# source: {args.directory.resolve()}\n")
                f.write(f"# W = {W:g}\n")
                f.write("# E I mean SD SE n\n")
                f.write("\n".join(rows) + "\n")

            plot_grid(
                Es, Is, mean, se, n, q, W, args.last, outdir / f"{stem}.png", args.show
            )

            print(
                f"{stem}: {len(keys)} (E, I) points, {n.sum()} runs -> "
                f"{outdir / (stem + '.dat')}, {outdir / (stem + '.png')}"
            )

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
