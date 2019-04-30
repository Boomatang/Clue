from flask_login import current_user

from app import db
from app.models import uuid_key, Company

material_size_lengths = db.Table(
    "material_size_lengths",
    db.Column("size_id", db.Integer, db.ForeignKey("material.id"), primary_key=True),
    db.Column(
        "length_id", db.Integer, db.ForeignKey("material_length.id"), primary_key=True
    ),
)


class MaterialClass(db.Model):
    __tablename__ = "material_class"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(150))
    materials = db.relationship("MaterialSize", backref="type", lazy=True)
    company = db.Column(db.Integer)
    asset = db.Column(db.String(64), index=True, default=uuid_key)

    def has_materials(self):
        if len(self.materials) > 0:
            return True
        else:
            return False

    @staticmethod
    def setup(company):
        MaterialClass._add_basic_classes(company)
        MaterialClass._set_default_classes_on_materials(company)

    @staticmethod
    def _add_basic_classes(company):
        db_company = Company.query.filter_by(id=company).first_or_404()

        items = [
            ("Undefined", "This is the default when no class is add to the materials"),
            ("Miscellaneous", "A list of various materials from different sources"),
        ]
        temp = []

        for item in items:
            entry = MaterialClass(name=item[0], description=item[1], company=company)
            db.session.add(entry)
            temp.append(entry)
        db.session.commit()

        for i in temp:
            db_company.add_asset(i.asset)

        db.session.commit()

    @staticmethod
    def _set_default_classes_on_materials(company):
        default = MaterialClass.query.filter_by(
            name="Undefined", company=company
        ).first()

        for entry in MaterialSize.query.all():
            entry.type = default

        db.session.commit()

    def __repr__(self):
        return f"<Material Class : {self.name}>"


class MaterialSize(db.Model):
    __tablename__ = "material"
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    lengths = db.relationship(
        "MaterialLength",
        secondary=material_size_lengths,
        lazy="subquery",
        backref=db.backref("sizes", lazy=False),
    )
    default = "Not Working"
    class_id = db.Column(db.Integer, db.ForeignKey("material_class.id"))
    company = db.Column(db.Integer)
    asset = db.Column(db.String(64), index=True, default=uuid_key)

    @staticmethod
    def add_new_material(size, lengths, group=None, company=None):
        entry = MaterialSize.query.filter_by(size=size, company=company).first()

        if entry is None:
            entry = MaterialSize(size=size, company=company)

            if group:
                entry.class_id = group

            for length in lengths:
                entry_length = MaterialLength.query.filter_by(
                    length=int(length)
                ).first()
                if entry_length is None:
                    entry_length = MaterialLength(length=int(length))
                entry.lengths.append(entry_length)
        db.session.add(entry)
        db.session.commit()
        current_user.company.add_asset(entry.asset)
        db.session.commit()

    @property
    def all_lengths(self):
        return (i.length for i in self.lengths)

    def add_length(self, new_length):
        existing = MaterialLength.query.filter_by(length=new_length).first()
        if existing is None:
            self.lengths.append(MaterialLength(length=new_length))
        else:
            self.lengths.append(existing)

    def remove_lengths(self, lengths):
        for length in self.lengths:
            if length.id in lengths:
                self.lengths.remove(length)

    def __repr__(self):
        return f"<Size : {self.size}>"


class MaterialLength(db.Model):
    __tablename__ = "material_length"
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return f"<Length : {self.length}>"
