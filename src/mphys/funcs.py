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


def read_table(path: Path | str) -> tuple[list[str], np.ndarray]:
    """
    Reads a space separated data file with a commented header.
        path : Path | str - Path to data file

    Returns: Column names as a list, and the data as a 2D numpy.ndarray

        Note: Lines starting with '#' are header lines. The last one holds the column names.
    """
    header_lines = []
    with open(path, "r") as f:
        for line in f:
            if not line.startswith("#"):
                break
            header_lines.append(line)

    if not header_lines:
        raise ValueError(f"{path} has no header line starting with '#'")

    names = header_lines[-1][1:].split()
    data = np.loadtxt(path, ndmin=2)

    if data.size == 0:
        raise ValueError(f"{path} has a header but no data")
    if data.shape[1] != len(names):
        raise ValueError(
            f"{path}: header has {len(names)} column names but the data has {data.shape[1]} columns"
        )
    return names, data


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


def partner_gaps(partners: np.ndarray) -> np.ndarray:
    """
    Gap along the chain between the nucleosome owning each face and the nucleosome stacked on it.
        partners (np.ndarray) : Partner index for every face, shape (F, 2N) or (2N,).
                   Column 2i is nucleosome i's plus face, column 2i + 1 its minus face.
                   A free face is -1.

    Returns: Gaps as a numpy.ndarray of the same shape as partners. 0 for a free face.

        Note: The sign is dropped, so stacking with i + 2 and i - 2 both give 2.
    """
    partners = np.asarray(partners, dtype=int)
    if partners.shape[-1] % 2 != 0:
        raise ValueError(
            f"Expected 2 faces per nucleosome, got {partners.shape[-1]} columns"
        )

    # Nucleosome that owns each face: columns 0, 1 -> 0, columns 2, 3 -> 1, ...
    owner = np.arange(partners.shape[-1]) // 2  # Shape (2N,)

    # Free faces are -1, so test for that rather than for 0 (0 is a real nucleosome)
    return np.where(partners >= 0, np.abs(partners - owner), 0)


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


def main():
    path = "data_files/sweep02/E8.0_I0.2_W10.0_r1_rg.dat"
    path2 = "final_rg_W10.dat"
    partners = np.array(
        [
            [2, -1, 3, -1, 4, 0, 5, 1, -1, 2, -1, 3],  # ladder: 0-2-4 and 1-3-5
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # nothing stacked
            [
                1,
                -1,
                2,
                0,
                3,
                1,
                4,
                2,
                5,
                3,
                -1,
                4,
            ],  # one stack in chain order: 0-1-2-3-4-5
            [5, -1, 4, -1, 3, -1, -1, 2, -1, 1, -1, 0],  # pairs 0-5, 1-4, 2-3
        ]
    )
    print(read_table(path)[:5])
    print(parse_run_name(path))
    print(parse_run_name(path2))
    print(partner_gaps(partners))


if __name__ == "__main__":
    main()
