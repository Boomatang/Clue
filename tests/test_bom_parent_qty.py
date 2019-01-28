import pytest

from app import db
from app.BOM.views import create_result
from app.models import BomResult, BomSession, BomSessionSize, \
    BomSessionLength, BomFileContents


from app.smart import CreateBom, RawBomFile
from tests.conftest import login_standard_user


@pytest.fixture()
def csv_file(tmpdir):
    p = tmpdir.mkdir("sub").join("sample.csv")
    p.write("ITEM NO.,PART NUMBER,DESCRIPTION,3D-Bounding Box Length,3D-Bounding Box Width,3D-Bounding Box Thickness,"
            "LENGTH,QTY.\n "
            "1,18-06-148-J01-A01,,,,,,3\n"
            "1.1,  18-06-148-J01-P01,,,,,,3\n"
            "1.1.1,    ,large,,,,6000,3")

    return p


@pytest.fixture()
def setup_for_creating_bom(clean_db, csv_file):

    raw: RawBomFile = RawBomFile(csv_file)
    entry = raw.return_entry()
    db.session.add(entry)

    bom_session: BomSession = BomSession(id=1)
    db.session.add(bom_session)

    length = BomSessionLength(length=6500, size_id=1)

    db.session.add(length)

    size = BomSessionSize(id=1, size='large', session_id=1, lengths=[length], default=6500)
    db.session.add(size)

    db.session.commit()
    entry.configure_file()


def test_creating_bom(client, setup_for_creating_bom):
    expected = 27
    bom = CreateBom(setup=1, data=1)
    bom.run()

    login_standard_user(client)
    result: BomResult = create_result(bom, 1)
    result = result.required_length_qty('large', 6500)
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
