#!/usr/bin/env python3
# Loads each data chunk one at a time, unwraps coordinates, calculates radius of gyration for each chunk, plots time evolution of it

import numpy as np
import argparse

from mphys.data_loader import load_dump_timestep
from mphys.funcs import unwrap_coords, store_data_to_csv
from mphys.paths import DATA


def calculate_radius_of_gyration(
    n_atoms: int, data: np.ndarray, box_size: np.ndarray, titles: list
) -> float:

    unwrapped_positions = unwrap_coords(data, box_size, titles)
    mean_r = np.mean(
        unwrapped_positions, axis=0
    )  # This should be mean x, y, z positions in an array of shape (3,)
    rg_sq = (
        np.sum(np.square(unwrapped_positions - mean_r)) / n_atoms
    )  # This should be the square of the radius of gyration for the given data chunk
    return np.sqrt(rg_sq)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "calculate_rg", usage="python calculate_rg.py filepath [-o savepath]"
    )
    parser.add_argument("filepath", type=str, help="Path to dump file")
    parser.add_argument(
        "-o", "--out", type=str, default=None, help="Save output file here"
    )
    args = parser.parse_args()
    needed_cols = ["x", "y", "z", "ix", "iy", "iz"]
    # Iterate over chunks
    rg_sq_all = []
    timesteps = []

    for chunk_params, chunk_data in load_dump_timestep(args.filepath, needed_cols):
        rg_sq_all.append(
            calculate_radius_of_gyration(
                chunk_params["n_atoms"],
                chunk_data,
                chunk_params["box_size"],
                chunk_params["used_titles"],
            )
        )

        timesteps.append(chunk_params["timestep"])
    save_path_rg = DATA / "rg.dat" if args.out is None else args.out

    store_data_to_csv(
        np.vstack((timesteps, rg_sq_all)).T,
        save_path_rg,
        ["#", "timestep", "R_g"],
    )
