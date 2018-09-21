import pytest

from app.smart import BarSpacingCalculator, RawBomFile

sizes = [(100, 1500, 12),
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
         (10, 0, 0)
         ]


@pytest.mark.parametrize('size', sizes)
def test_bar_spacing_less_than(size):
    unit = BarSpacingCalculator(size[0], size[1], size[2])

    assert unit.real_gap_size <= size[0]


def test_function_check_is_int():
    assert RawBomFile._check_is_int(True) is None
