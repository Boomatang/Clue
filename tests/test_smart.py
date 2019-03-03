import pytest

from csv import reader
from pathlib import Path as P

from app.smart import BarSpacingCalculator, RawBomFile, fix_csv_file

sizes = [
    (100, 1500, 12),
    (100, 1000, 10),
    (100, 100, 10),
    (0, 1500, 10),
    (100, 0, 10),
    (100, 1500, 0),
    (1600, 1500, 10),
    (0, 0, 0),
    (10, 10, 10),
    (0, 100, 0),
    (0, 0, 10),
    (10, 0, 0),
]


@pytest.mark.parametrize("size", sizes)
def test_bar_spacing_less_than(size):
    unit = BarSpacingCalculator(size[0], size[1], size[2])

    assert unit.real_gap_size <= size[0]


def test_function_check_is_int():
    assert RawBomFile._check_is_int(True) is None


def test_csv_fixing(tmpdir):
    # setup
    # TODO refactor this to run multiply checks
    a_file = tmpdir.join("test.csv")
    plain_text = (
        "ITEM NO.,PART NUMBER,Mark,DESCRIPTION,3D-Bounding Box Length,"
        "3D-Bounding Box Width,3D-Bounding Box Thickness,LENGTH,QTY.\n"
        "1,,,PLATE, 100x100x10,100,100,10,,12"
    )

    a_file.write(plain_text)

    expected = [
        [
            "ITEM NO.",
            "PART NUMBER",
            "Mark",
            "DESCRIPTION",
            "3D-Bounding Box Length",
            "3D-Bounding Box Width",
            "3D-Bounding Box Thickness",
            "LENGTH",
            "QTY.",
        ],
        ["1", "", "", "PLATE 100x100x10", "100", "100", "10", "", "12"],
    ]

    f = P(a_file)

    # fixing file
    fix_csv_file(f)

    # Checking result
    a = reader(open(a_file), delimiter=",", quotechar="|")
    for row, other_row in zip(a, expected):
        assert row == other_row


def test_csv_fixing_with_symbols(tmpdir):
    # setup
    # TODO refactor this to run multiply checks
    a_file = tmpdir.join("test.csv")
    plain_text = (
        "ITEM NO.,PART NUMBER,Mark,DESCRIPTION,3D-Bounding Box Length,"
        "3D-Bounding Box Width,3D-Bounding Box Thickness,LENGTH,QTY.\n"
        "1,,,Ø48 90° Key Clamp Elbow,100,100,10,150,12"
    )

    a_file.write(plain_text)

    expected = [
        [
            "ITEM NO.",
            "PART NUMBER",
            "Mark",
            "DESCRIPTION",
            "3D-Bounding Box Length",
            "3D-Bounding Box Width",
            "3D-Bounding Box Thickness",
            "LENGTH",
            "QTY.",
        ],
        ["1", "", "", "Ø48 90° Key Clamp Elbow", "100", "100", "10", "150", "12"],
    ]

    f = P(a_file)

    # fixing file
    fix_csv_file(f)

    # Checking result
    a = reader(open(a_file), delimiter=",", quotechar="|")
    for row, other_row in zip(a, expected):
        assert row == other_row
