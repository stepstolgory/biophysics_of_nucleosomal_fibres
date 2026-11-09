import matplotlib

matplotlib.use("Agg")  # No screen needed

import matplotlib.pyplot as plt
import numpy as np
import pytest

from mphys.plotting import (
    GAP_COLOURS,
    histogram,
    kymograph,
    label,
    stats_text,
    timeseries,
)


@pytest.fixture
def ax():
    fig, ax = plt.subplots()
    yield ax
    plt.close(fig)


def test_label_with_and_without_unit():
    assert label("rg") == r"$R_g$ ($\sigma_{LJ}$)"
    assert label("fraction") == r"$f_{\mathrm{stack}}$"  # unit is None


def test_label_unknown_name_falls_back_to_name():
    with pytest.warns(UserWarning):
        assert label("gap2") == "gap2"


def test_stats_text_takes_values_then_name():
    text = stats_text(np.array([0.2, 0.4]), "fraction")
    assert r"\langle f_{\mathrm{stack}} \rangle = 0.30" in text
    assert r"\sigma = 0.10" in text


def test_stats_text_unknown_name():
    assert r"\mathrm{gap2}" in stats_text(np.array([1.0, 1.0]), "gap2")


def test_timeseries_and_histogram_run(ax):
    t = np.arange(100) * 10000
    y = np.linspace(0, 1, 100)
    assert timeseries(ax, t, y, "fraction") is ax
    assert ax.get_ylim() == (0, 1)  # From QUANTITIES
    assert histogram(ax, y, "fraction") is ax


def test_kymograph_clips_gaps(ax):
    t = np.arange(3) * 10000
    gaps = np.array([[0, 2, 2, 7], [1, 0, 3, 4], [0, 0, 0, 0]])  # 3 frames, 2 nucleosomes
    mesh = kymograph(ax, t, gaps)
    values = np.asarray(mesh.get_array()).reshape(4, 3)  # One row per face
    assert values.max() == len(GAP_COLOURS) - 1  # 7 is drawn as 4+
    assert [tick.get_text() for tick in ax.get_yticklabels()] == ["0+", "0-", "1+", "1-"]
