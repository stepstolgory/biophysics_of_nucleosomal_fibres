import numpy as np
import csv
from pathlib import Path
import re

FLOAT = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"

# E8.0_I0.2_W10.0_r1_rg.dat -> E, I, W, rep, kind
RUN_NAME_RE = re.compile(
    rf"E(?P<E>{FLOAT})_I(?P<I>{FLOAT})_W(?P<W>{FLOAT})_r(?P<rep>\d+)_(?P<kind>[a-z]+)\.dat"
)


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


def read_table(path: Path | str) -> np.ndarray:
    """
    Returns columns names and data from a space separated file as a 2D array.

    path (Path | str) : Path to data file
    """
    data = np.loadtxt(path, ndmin=2)
    return data


def parse_run_name(path: Path | str) -> dict | None:
    """
    Read the parameters from a data file name like E8.0_I0.2_W10.0_r1_rg.dat
        path (Path | str) : Path to the file. Only the file name is used.

    Returns: dict with E, I, W (float), rep (int) and kind (str),
             or None if the name doesn't match
    """
    m = RUN_NAME_RE.fullmatch(Path(path).name)
    if m is None:
        return None
    return {
        "E": float(m["E"]),
        "I": float(m["I"]),
        "W": float(m["W"]),
        "rep": int(m["rep"]),
        "kind": m["kind"],
    }


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
