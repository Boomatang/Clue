# Test that the models can be created
from app import db
from app.mocks import set_up_sample_bom_files, set_up_sample_bom_file_data
from app.models import BomFile, BomFileContents


def test_add_bom_file_class(client):
    # Checking if a bom file could have been uploaded

    name = "test file"
    comment = "File was uploaded"

    bom_file = BomFile(name=name, comment=comment)

    db.session.add(bom_file)
    db.session.commit()

    result = BomFile.query.filter_by(name=name).first()

    assert result.comment == comment


def test_add_bom_file_contents(client):
    item_no = "1.1"
    part_number = "1.1"
    description = "Item description"
    BB_length = 600
    BB_width = 500
    BB_thickness = 10
    length = 1000
    qty = 10
    file_id = 1

    bom_file_contents = BomFileContents(item_no=item_no,
                                        part_number=part_number,
                                        description=description,
                                        BB_length=BB_length,
                                        BB_width=BB_width,
                                        BB_thickness=BB_thickness,
                                        length=length,
                                        qty=qty,
                                        file_id=file_id)

    db.session.add(bom_file_contents)
    db.session.commit()

    result = BomFileContents.query.filter_by(part_number=part_number).first()

    assert result.length == length


def test_add_four_mock_files_to_db(client, clean_db):
    set_up_sample_bom_files(4)
    bom_files = BomFile.query.all()
    assert 4 == len(bom_files)


def test_add_four_items_to_mock_files(client, clean_db):
    set_up_sample_bom_files(1)
    set_up_sample_bom_file_data(id=1, qty=4)
    bom_file: BomFile = BomFile.query.filter_by(id=1).first()
    assert 4 == len(bom_file.items)
