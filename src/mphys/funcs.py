import numpy as np
import csv
from pathlib import Path


def unwrap_coords(data: np.ndarray, dims: np.ndarray, titles: list) -> np.ndarray:
    """
    Unwrapps the periodic box coordinates
        data : numpy.ndarray - Position data to unwrap
        dims : numpy.ndarray - Dimensions of the box
        titles : list - Column titles read from file

    Returns: Unwrapped positions as a numpy.ndarray
    """
    pos_ids = [titles.index(c) for c in ("x", "y", "z")]
    img_ids = [titles.index(c) for c in ("ix", "iy", "iz")]
    real_pos = data[:, pos_ids] + data[:, img_ids] * dims
    return real_pos


def store_data_to_csv(
    data: np.ndarray | list, save_path: Path | str, header: np.ndarray | list
) -> None:
    """
    Saves data to a file separated by a space character with custom header.
        data : numpy.ndarray | list - Data to write
        save_path : Path | str - Path to write to
        header : np.ndarray | list - File header

        Note: Lines starting with '#' are automatically considered comments
    """
    with open(save_path, "w", newline="") as f:
        writer = csv.writer(f, delimiter=" ", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(data)


def quat2uaxis(q: np.ndarray):
    """Return the unit vector corresponding to the z-axis of the bead"""
    p = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    p[0] = 2.0 * q[1] * q[3] + 2.0 * q[0] * q[2]
    p[1] = 2.0 * q[2] * q[3] - 2.0 * q[0] * q[1]
    p[2] = q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]
    return p


def quat2faxis(q: np.ndarray):
    """Return the unit vector corresponding to the x-axis of the bead"""
    p = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    p[0] = q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3]
    p[1] = 2.0 * q[1] * q[2] + 2.0 * q[0] * q[3]
    p[2] = 2.0 * q[1] * q[3] - 2.0 * q[0] * q[2]
    return p


def quat2vaxis(q: np.ndarray):
    """Return the unit vector corresponding to the y-axis of the bead"""
    p = np.array([0.0, 0.0, 0.0], dtype=np.float64)
    p[0] = 2.0 * q[1] * q[2] - 2.0 * q[0] * q[3]
    p[1] = q[0] * q[0] - q[1] * q[1] + q[2] * q[2] - q[3] * q[3]
    p[2] = 2.0 * q[2] * q[3] + 2.0 * q[0] * q[1]
    return p
