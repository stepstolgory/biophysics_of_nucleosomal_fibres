#!/usr/bin/env python3
# Loads each data chunk one at a time, unwraps coordinates, calculates radius of gyration for each chunk, plots time evolution of it

import numpy as np
import argparse

from mphys.data_loader import load_dump_timestep
from mphys.funcs import unwrap_coords, store_data_to_csv
from mphys.paths import DATA


def calculate_end_to_end_distance(
    n_atoms: int, data: np.ndarray, box_size: np.ndarray, titles: list
) -> float:
    """Calculate the end to end distance by calculating the cartesian distance between atom with id 0 and id n_atom"""

    # Since the list comes out as sorted by atom ID, I can just take the first and last atom
    # NOTE:: Could be beneficial to add an "offset" parameter for longer tails. Then would find distance between data[offset] and data[-offset]

    first_atom, last_atom = data[0], data[-1]
    first_atom, last_atom = unwrap_coords(
        np.array([first_atom, last_atom]), box_size, titles
    )
    e_e_distance = np.linalg.norm(last_atom - first_atom)
    return e_e_distance


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
    e_e_distance_all = []
    timesteps = []

    for chunk_params, chunk_data in load_dump_timestep(args.filepath, needed_cols):

        e_e_distance_all.append(
            calculate_end_to_end_distance(
                chunk_params["n_atoms"],
                chunk_data,
                chunk_params["box_size"],
                chunk_params["used_titles"],
            )
        )

        timesteps.append(chunk_params["timestep"])

    save_path_ee = DATA / "ee.dat" if args.out is None else args.out

    store_data_to_csv(
        np.vstack((timesteps, e_e_distance_all)).T,
        save_path_ee,
        ["#", "timestep", "e_e_distance"],
    )
