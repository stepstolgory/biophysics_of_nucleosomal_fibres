#!/usr/bin/env python3
# Loads each data chunk one at a time, unwraps coordinates, calculates radius of gyration for each chunk, plots time evolution of it


import csv
from itertools import islice
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

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


def plot_rg_over_time(
    time_data: np.ndarray, rg_data: np.ndarray, n_bins: int = 50
) -> None:

    time_bins = np.array_split(time_data, n_bins)
    rg_data_bins = np.array_split(rg_data, n_bins)

    bin_centres = np.array([t.mean() for t in time_bins])
    mean = np.array([rg.mean() for rg in rg_data_bins])
    std = np.array([rg.std() for rg in rg_data_bins])

    fig, ax = plt.subplots()

    ax.scatter(time_data, rg_data, s=2, alpha=0.2, color="grey", label="data")
    ax.errorbar(
        bin_centres,
        mean,
        yerr=std,
        fmt="o-",
        markersize=3,
        capsize=2,
        label=r"binned mean $\pm 1 \sigma$",
    )

    ax.set_title(r"Time evolution of radius of gyration, $R_g$")
    ax.set_xlabel("Timestep")
    ax.set_ylabel(r"$R_g$")
    ax.legend()

    fig.savefig("figures/rg_over_time.png")
    # plt.show()


def store_data_to_csv(
    data: np.ndarray | list, save_path: Path | str, header: np.ndarray | list
) -> None:
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


if __name__ == "__main__":
    filepath = "/home/smikoyan/projects/mphys/initial_tests/dump_main.nucleosomes"
    needed_cols = ["x", "y", "z", "ix", "iy", "iz"]
    # Iterate over chunks
    rg_sq_all = []
    timesteps = []
    # test_chunk_params, test_chunk_data = next(load_dump_timestep(filepath, needed_cols))
    # print(
    #     calculate_radius_of_gyration(
    #         test_chunk_params["n_atoms"], test_chunk_data, test_chunk_params["box_size"]
    #     )
    # )
    for chunk_params, chunk_data in load_dump_timestep(filepath, needed_cols):
        rg_sq_all.append(
            calculate_radius_of_gyration(
                chunk_params["n_atoms"],
                chunk_data,
                chunk_params["box_size"],
                chunk_params["used_titles"],
            )
        )
        timesteps.append(chunk_params["timestep"])
    plot_rg_over_time(np.asarray(timesteps), np.asarray(rg_sq_all))
    store_data_to_csv(
        np.vstack((timesteps, rg_sq_all)).T,
        "data_files/rg_sq_data.dat",
        ["timestep", r"$R_g$"],
    )
