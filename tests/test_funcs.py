import numpy as np

from mphys.funcs import store_data_to_csv, unwrap_coords

TITLES = ["id", "x", "y", "z", "ix", "iy", "iz"]


def test_unwrap_adds_box_images():
    data = np.array([[1, 1.0, 2.0, 3.0, 1, 0, -1]])
    box = np.array([10.0, 10.0, 10.0])
    assert np.allclose(unwrap_coords(data, box, TITLES), [[11.0, 2.0, -7.0]])


def test_store_data_writes_header_and_rows(tmp_path):
    out = tmp_path / "table.dat"

    store_data_to_csv([[0, 1.5], [1000, 2.5]], out, ["#", "timestep", "R_g"])
    text = out.read_bytes().decode()
    assert "\r" not in text
    assert text.splitlines() == ["# timestep R_g", "0 1.5", "1000 2.5"]
