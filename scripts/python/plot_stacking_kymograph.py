"""
Kymograph of which neighbour each face is stacked with, over time.

Usage:
    python plot_stacking_kymograph.py filename [--show] [-o output path]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import BoundaryNorm, ListedColormap

from mphys.funcs import partner_gaps, read_table
from mphys.paths import FONTS, STYLE, FIGURES
from mphys.plotting import TIME_SCALE, TIME_LABEL

# free, gap 1, gap 2 (the ladder), gap 3, gap 4 or more
GAP_COLOURS = ["#f2f2f2", "#e00000", "#0066cc", "#ff7f0e", "#808080"]
GAP_LABELS = ["free", "1", "2", "3", "4+"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=Path, help="Path to a _faces.dat file")
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

    # Make sure the styles all match
    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))

    names, data = read_table(args.filepath)
    t = data[:, names.index("timestep")] / TIME_SCALE
    partners = np.delete(data, names.index("timestep"), axis=1).astype(int)

    # Gap along the chain for every face, with 4 and above lumped together
    gaps = np.clip(
        partner_gaps(partners), 0, len(GAP_COLOURS) - 1
    )  # Values below 0 are set to 0 (0 neighbours) values above 4 are set to 4 (4+ is the same colour)
    rows = np.arange(gaps.shape[1])  # One row per face: n0+, n0-, n1+, n1-, ...

    # Setting the colour map for the kymograph
    cmap = ListedColormap(GAP_COLOURS)
    norm = BoundaryNorm(np.arange(len(GAP_COLOURS) + 1) - 0.5, cmap.N)

    fig, ax = plt.subplots(figsize=(10, 4.2))
    mesh = ax.pcolormesh(
        t, rows, gaps.T, cmap=cmap, norm=norm, shading="nearest"
    )  # pseudo colour plot with a non-regular rectangular grid

    # One tick per face: 0+, 0-, 1+, 1-, ... (plus face on row 2i, minus face on row 2i + 1)
    N = gaps.shape[1] // 2  # number of nucleosomes (2 faces per)
    face_labels = [f"{i}{side}" for i in range(N) for side in ("+", "-")]
    ax.set_yticks(rows, face_labels, fontsize=6)
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_ylabel("Nucleosome")
    ax.set_xlabel(TIME_LABEL)

    cbar = fig.colorbar(mesh, ax=ax, ticks=np.arange(len(GAP_COLOURS)), pad=0.02)
    cbar.ax.set_yticklabels(GAP_LABELS)
    cbar.ax.minorticks_off()
    cbar.set_label("Stacked with neighbour")

    if args.show:
        plt.show()
    else:
        out = args.out
        fig.savefig(out)
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
