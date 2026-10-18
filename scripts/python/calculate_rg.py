#!/usr/bin/env python3
# Loads each data chunk one at a time, unwraps coordinates, calculates radius of gyration for each chunk, plots time evolution of it


import csv
from itertools import islice
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import argparse

from data_loader import load_dump_timestep


def _unwrap_coords(data: np.ndarray, dims: np.ndarray, titles: list) -> np.ndarray:

    pos_ids = [titles.index(c) for c in ("x", "y", "z")]
    img_ids = [titles.index(c) for c in ("ix", "iy", "iz")]
    real_pos = data[:, pos_ids] + data[:, img_ids] * dims
    return real_pos


def calculate_radius_of_gyration(
    n_atoms: int, data: np.ndarray, box_size: np.ndarray, titles: list
) -> float:

    unwrapped_positions = _unwrap_coords(data, box_size, titles)
    mean_r = np.mean(
        unwrapped_positions, axis=0
    )  # This should be mean x, y, z positions in an array of shape (3,)
    rg_sq = (
        np.sum(np.square(unwrapped_positions - mean_r)) / n_atoms
    )  # This should be the square of the radius of gyration for the given data chunk
    return np.sqrt(rg_sq)


def calculate_end_to_end_distance(
    n_atoms: int, data: np.ndarray, box_size: np.ndarray, titles: list
) -> float:
    """Calculate the end to end distance by calculating the cartesian distance between atom with id 0 and id n_atom"""

    # Since the list comes out as sorted by atom ID, I can just take the first and last atom
    # NOTE:: Could be beneficial to add an "offset" parameter for longer tails. Then would find distance between data[offset] and data[-offset]

    first_atom, last_atom = data[0], data[-1]
    first_atom, last_atom = _unwrap_coords(
        np.array([first_atom, last_atom]), box_size, titles
    )
    e_e_distance = np.linalg.norm(last_atom - first_atom)
    return e_e_distance


def store_data_to_csv(
    data: np.ndarray | list, save_path: Path | str, header: np.ndarray | list
) -> None:
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerow(header)
        writer.writerows(data)


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
    e_e_distance_all = []
    timesteps = []

    # test_chunk_params, test_chunk_data = next(load_dump_timestep(filepath, needed_cols))
    # print(
    #     calculate_radius_of_gyration(
    #         test_chunk_params["n_atoms"], test_chunk_data, test_chunk_params["box_size"]
    #     )
    # )

    for chunk_params, chunk_data in load_dump_timestep(args.filepath, needed_cols):
        rg_sq_all.append(
            calculate_radius_of_gyration(
                chunk_params["n_atoms"],
                chunk_data,
                chunk_params["box_size"],
                chunk_params["used_titles"],
            )
        )

        e_e_distance_all.append(
            calculate_end_to_end_distance(
                chunk_params["n_atoms"],
                chunk_data,
                chunk_params["box_size"],
                chunk_params["used_titles"],
            )
        )

        timesteps.append(chunk_params["timestep"])
    save_path_rg = "data_files/rg.dat" if args.out is None else args.out
    save_path_ee = "data_files/ee.dat" if args.out is None else args.out
    store_data_to_csv(
        np.vstack((timesteps, rg_sq_all)).T,
        save_path_rg,
        ["#", "timestep", "R_g"],
    )
    store_data_to_csv(
        np.vstack((timesteps, e_e_distance_all)).T,
        save_path_ee,
        ["#", "timestep", "e_e_distance"],
    )
