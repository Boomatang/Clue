import pytest

from app import db
from app.models import (
    BomResult,
    BomSession,
    BomSessionSize,
    BomSessionLength,
    BomFileContents,
)


from app.smart import CreateBom, RawBomFile
from tests.conftest import login_standard_user


def test_creating_bom(client, setup_for_creating_bom):
    expected = 27
    bom = CreateBom(setup=1, data=1)
    bom.run()

    login_standard_user(client)
    result: BomResult = bom.create_result()
    result = result.required_length_qty("large", 6500)
    assert expected == result


def test_creating_bom_with_no_plate(client, setup_for_creating_bom_with_no_plate):
    expected = 27
    bom = CreateBom(setup=1, data=1)
    bom.run()

    login_standard_user(client)
    result: BomResult = bom.create_result()
    result = result.required_length_qty("large", 6500)
    assert expected == result


def test_raw_bom_file(csv_file):
    expected = RawBomFile
    result: RawBomFile = RawBomFile(csv_file)

    assert type(result) == expected


def test_total_required(setup_for_creating_bom):
    expected = 39
    result = 0
    entries = BomFileContents.query.all()[:]
    for item in entries:
        result += item.total_required()

    assert result == expected
