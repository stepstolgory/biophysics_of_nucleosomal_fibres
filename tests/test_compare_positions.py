import pytest

from compare_positions import compare_dumps

HEADER = [
    "ITEM: TIMESTEP",
    "{t}",
    "ITEM: NUMBER OF ATOMS",
    "2",
    "ITEM: BOX BOUNDS pp pp pp",
    "0 10",
    "0 10",
    "0 10",
    "ITEM: ATOMS id type x y z ix iy iz",
]


def write_dump(path, frames):
    """frames: a list of frames, each a list of atom rows 'id type x y z ix iy iz'."""
    lines = []
    for n, atoms in enumerate(frames):
        lines += [h.format(t=n * 1000) for h in HEADER] + atoms
    path.write_text("\n".join(lines) + "\n")


def test_same_positions_pass(tmp_path):
    a, b = tmp_path / "a.dump", tmp_path / "b.dump"
    frame = ["1 1 1.0 2.0 3.0 0 0 0", "2 1 4.0 5.0 6.0 0 0 0"]
    write_dump(a, [frame, frame])
    write_dump(b, [frame, frame])
    compare_dumps(a, b)


def test_same_unwrapped_position_in_different_box_images_pass(tmp_path):
    # x = 9 with ix = -1 and x = -1 with ix = 0 are the same place
    a, b = tmp_path / "a.dump", tmp_path / "b.dump"
    write_dump(a, [["1 1 9.0 0 0 -1 0 0", "2 1 0 0 0 0 0 0"]])
    write_dump(b, [["1 1 -1.0 0 0 0 0 0", "2 1 0 0 0 0 0 0"]])
    compare_dumps(a, b)


def test_different_positions_fail(tmp_path):

    a, b = tmp_path / "a.dump", tmp_path / "b.dump"
    write_dump(a, [["1 1 1.0 0 0 0 0 0", "2 1 2.0 0 0 0 0 0"]])
    write_dump(b, [["1 1 1.5 0 0 0 0 0", "2 1 2.0 0 0 0 0 0"]])
    with pytest.raises(AssertionError, match="Frame 0 differs"):
        compare_dumps(a, b)


def test_different_frame_counts_fail(tmp_path):
    a, b = tmp_path / "a.dump", tmp_path / "b.dump"
    frame = ["1 1 1.0 0 0 0 0 0", "2 1 2.0 0 0 0 0 0"]
    write_dump(a, [frame, frame])
    write_dump(b, [frame])
    with pytest.raises(AssertionError, match="different numbers of frames"):

        compare_dumps(a, b)
