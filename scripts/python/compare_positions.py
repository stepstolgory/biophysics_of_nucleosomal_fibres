import argparse
from itertools import zip_longest

import numpy as np


from mphys.data_loader import load_dump_timestep
from mphys.funcs import unwrap_coords

COLUMNS = ["x", "y", "z", "ix", "iy", "iz"]


def compare_dumps(file1, file2) -> None:
    """Raise AssertionError if the unwrapped positions differ in any frame."""
    frames1 = load_dump_timestep(file1, COLUMNS)
    frames2 = load_dump_timestep(file2, COLUMNS)

    for n, (f1, f2) in enumerate(zip_longest(frames1, frames2)):
        assert (
            f1 is not None and f2 is not None
        ), "The files have different numbers of frames."
        params1, data1 = f1
        params2, data2 = f2

        data1 = unwrap_coords(data1, params1["box_size"], params1["used_titles"])
        data2 = unwrap_coords(data2, params2["box_size"], params2["used_titles"])

        assert np.allclose(data1, data2), f"Frame {n} differs."


def main():
    parser = argparse.ArgumentParser(
        "Compare positions", "./compare_positions.py file1 file2"
    )
    parser.add_argument("file1", type=str, help="File to compare against")
    parser.add_argument("file2", type=str, help="File begin compared")
    args = parser.parse_args()

    compare_dumps(args.file1, args.file2)
    print("[PASSED] All atom positions match in all frames.")


if __name__ == "__main__":
    main()
