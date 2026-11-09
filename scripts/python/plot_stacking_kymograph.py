"""
Kymograph of which neighbour each face is stacked with, over time.

Usage:
    python plot_stacking_kymograph.py FILE [FILE ...] [--outdir DIR] [--show]
    python plot_stacking_kymograph.py data_files/sweep04/*_faces.dat

Output (unless --outdir is given): figures/<same sub-folder>/<file stem>_kymo.png
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from mphys.funcs import partner_gaps, read_table
from mphys.plotting import (
    GAP_COLOURS,
    GAP_LABELS,
    default_out,
    kymograph,
    savefig,
    use_style,
)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("files", nargs="+", type=Path, help="_faces.dat files")
    parser.add_argument(
        "--outdir", type=Path, default=None,
        help="Folder for the plots, keeping their default names",
    )
    parser.add_argument(
        "--show", action="store_true", help="Display the plots instead of saving them"
    )
    args = parser.parse_args()

    use_style()

    for path in args.files:
        names, data = read_table(path)
        t = data[:, names.index("timestep")]
        partners = np.delete(data, names.index("timestep"), axis=1).astype(int)

        fig, ax = plt.subplots(figsize=(10, 4.2))
        mesh = kymograph(ax, t, partner_gaps(partners))
        ax.set_title(path.stem, fontsize="small")

        cbar = fig.colorbar(mesh, ax=ax, ticks=np.arange(len(GAP_COLOURS)), pad=0.02)
        cbar.ax.set_yticklabels(GAP_LABELS)
        cbar.ax.minorticks_off()
        cbar.set_label("Stacked with neighbour")

        if args.show:
            continue
        out = default_out(path, "kymo")
        if args.outdir is not None:
            out = args.outdir / out.name
        savefig(fig, out)
        print(f"Saved {out}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
