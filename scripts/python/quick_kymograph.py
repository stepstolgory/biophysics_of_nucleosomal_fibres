#!/usr/bin/env python3
"""
Quick kymograph of which neighbour each face is stacked with, over time.

Usage:
    python quick_kymograph.py data_files/sweep04/E8.0_I0.2_W10.0_r1_faces.dat [--show]
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import BoundaryNorm, ListedColormap

from mphys.funcs import partner_gaps, read_table
from mphys.paths import FONTS, STYLE

# free, gap 1, gap 2 (the ladder), gap 3, gap 4 or more
GAP_COLOURS = ["#f2f2f2", "#e00000", "#0066cc", "#ff7f0e", "#808080"]
GAP_LABELS = ["free", "1", "2", "3", "4+"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=Path, help="Path to a _faces.dat file")
    parser.add_argument(
        "--show", action="store_true", help="Display the plot instead of saving it"
    )
    args = parser.parse_args()

    for f in FONTS.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.style.use(str(STYLE / "atlas.mplstyle"))

    names, data = read_table(args.filepath)
    t = data[:, names.index("timestep")] / 1e6
    partners = np.delete(data, names.index("timestep"), axis=1).astype(int)

    # Gap along the chain for every face, with 4 and above lumped together
    gaps = np.clip(partner_gaps(partners), 0, len(GAP_COLOURS) - 1)
    rows = np.arange(gaps.shape[1])  # One row per face: n0+, n0-, n1+, n1-, ...

    cmap = ListedColormap(GAP_COLOURS)
    norm = BoundaryNorm(np.arange(len(GAP_COLOURS) + 1) - 0.5, cmap.N)

    fig, ax = plt.subplots(figsize=(10, 4.2))
    mesh = ax.pcolormesh(t, rows, gaps.T, cmap=cmap, norm=norm, shading="nearest")

    # One tick per face: 0+, 0-, 1+, 1-, ... (plus face on row 2i, minus face on row 2i + 1)
    N = gaps.shape[1] // 2
    face_labels = [f"{i}{side}" for i in range(N) for side in ("+", "-")]
    ax.set_yticks(rows, face_labels, fontsize=8)
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_ylabel("Nucleosome")
    ax.set_xlabel(r"Time steps ($10^6$)")

    cbar = fig.colorbar(mesh, ax=ax, ticks=np.arange(len(GAP_COLOURS)), pad=0.02)
    cbar.ax.set_yticklabels(GAP_LABELS)
    cbar.ax.minorticks_off()
    cbar.set_label("Stacked with neighbour")

    if args.show:
        plt.show()
    else:
        out = args.filepath.with_name(f"{args.filepath.stem}_kymo.png")
        fig.savefig(out)
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
