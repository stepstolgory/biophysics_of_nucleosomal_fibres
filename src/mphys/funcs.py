import numpy as np
import csv
from pathlib import Path


def unwrap_coords(data: np.ndarray, dims: np.ndarray, titles: list) -> np.ndarray:

    pos_ids = [titles.index(c) for c in ("x", "y", "z")]
    img_ids = [titles.index(c) for c in ("ix", "iy", "iz")]
    real_pos = data[:, pos_ids] + data[:, img_ids] * dims
    return real_pos


def store_data_to_csv(
    data: np.ndarray | list, save_path: Path | str, header: np.ndarray | list
) -> None:
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=" ", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(data)
