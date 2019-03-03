from forgery_py import name, lorem_ipsum, basic

from app import db
from app.models import BomFile, BomFileContents


def set_up_sample_bom_files(number):
    while number:
        number -= 1
        bom = BomFile(
            name=name.first_name(), comment=lorem_ipsum.paragraph(sentences_quantity=3)
        )
        db.session.add(bom)

    db.session.commit()


def set_up_sample_bom_file_data(id=1, qty=4):
    bom_file: BomFile = BomFile.query.filter_by(id=id).first()
    while qty:
        qty -= 1
        contents: BomFileContents = BomFileContents(
            item_no=basic.number(at_least=1, at_most=10),
            part_number=basic.number(at_least=1, at_most=10),
            description=lorem_ipsum.words(4),
            BB_length=basic.number(at_least=150, at_most=1000),
            BB_width=basic.number(at_least=50, at_most=1130),
            BB_thickness=basic.number(at_least=1, at_most=10),
            length=basic.number(at_least=50, at_most=8500),
            qty=basic.number(at_least=1, at_most=40),
            file_id=bom_file.id,
        )

        bom_file.items.append(contents)

    db.session.commit()
