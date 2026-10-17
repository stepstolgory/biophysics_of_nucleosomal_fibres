import data_loader
import argparse
import numpy as np
from calculate_rg import _unwrap_coords
from itertools import zip_longest

COLUMNS = ["x", "y", "z", "ix", "iy", "iz"]


def main():
    parser = argparse.ArgumentParser(
        "Compare positions", "./compare_positions.py file1 file2"
    )
    parser.add_argument("file1", type=str, help="File to compare against")
    parser.add_argument("file2", type=str, help="File begin compared")

    args = parser.parse_args()

    # Load data files

    frames1 = data_loader.load_dump_timestep(args.file1, COLUMNS)
    frames2 = data_loader.load_dump_timestep(args.file2, COLUMNS)

    for n, (f1, f2) in enumerate(zip_longest(frames1, frames2)):
        print(n)
        assert (
            f1 is not None and f2 is not None
        ), "The files have different numbers of frames."
        params1, data1 = f1

        params2, data2 = f2

        data1 = _unwrap_coords(data1, params1["box_size"], params1["used_titles"])
        data2 = _unwrap_coords(data2, params2["box_size"], params2["used_titles"])

        assert np.allclose(data1, data2), f"Frame {n} differs."


if __name__ == "__main__":
    main()
