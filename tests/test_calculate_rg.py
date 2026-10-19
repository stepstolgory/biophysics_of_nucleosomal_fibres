import numpy as np

from calculate_rg import calculate_radius_of_gyration
from calculate_ee import calculate_end_to_end_distance

TITLES = ["id", "x", "y", "z", "ix", "iy", "iz"]
BOX = np.array([10.0, 10.0, 10.0])


def test_rg_of_two_points():
    # two atoms 2 apart: each is 1 from the centre, so Rg = 1
    data = np.array([[1, 0.0, 0, 0, 0, 0, 0], [2, 2.0, 0, 0, 0, 0, 0]])
    assert np.isclose(calculate_radius_of_gyration(2, data, BOX, TITLES), 1.0)


def test_rg_uses_image_flags():
    # atom 2 sits at x = 9 with image flag -1, so it is really at x = -1
    data = np.array([[1, 0.0, 0, 0, 0, 0, 0], [2, 9.0, 0, 0, -1, 0, 0]])
    assert np.isclose(calculate_radius_of_gyration(2, data, BOX, TITLES), 0.5)


def test_end_to_end_is_first_to_last_atom():
    data = np.array(
        [[1, 0.0, 0, 0, 0, 0, 0], [2, 50.0, 50, 50, 0, 0, 0], [3, 3.0, 4, 0, 0, 0, 0]]
    )
    assert np.isclose(calculate_end_to_end_distance(3, data, BOX, TITLES), 5.0)


def test_end_to_end_uses_image_flags():
    data = np.array([[1, 0.0, 0, 0, 0, 0, 0], [2, 9.0, 0, 0, -1, 0, 0]])
    assert np.isclose(calculate_end_to_end_distance(2, data, BOX, TITLES), 1.0)
