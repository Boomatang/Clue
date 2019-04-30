from datetime import datetime

from app import db


class BomFile(db.Model):
    __tablename__ = "bom_files"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    comment = db.Column(db.String(250))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship(
        "BomFileContents", cascade="all, delete-orphan", backref="file", lazy=True
    )
    results = db.relationship(
        "BomResult", cascade="all, delete-orphan", backref="file", lazy=True
    )
    project_id = db.Column(db.String(64))

    def configure_file(self):
        for item in self.items:
            item.set_parent()

    def materials_required(self):
        material = []
        for item in self.items:
            if item.description is not None:
                if item.description not in material and item.is_material():
                    material.append(item.description)
        if len(material) == 0:
            material.append("No materials Found")

        return material

    def __repr__(self):
        return f"<File Name : {self.name}"


class BomFileContents(db.Model):
    __tablename__ = "bom_file_contents"
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(64))
    part_number = db.Column(db.String(64))
    description = db.Column(db.String(64))
    BB_length = db.Column(db.Float)
    BB_width = db.Column(db.Float)
    BB_thickness = db.Column(db.Float)
    length = db.Column(db.Float)
    qty = db.Column(db.Integer)
    parent = db.Column(db.Integer)
    file_id = db.Column(db.Integer, db.ForeignKey("bom_files.id"), nullable=False)

    def set_parent(self):
        parent_item_no = self._get_parent_item_no()
        self.parent = self._get_parent_id(parent_item_no, self.file_id)

    def total_required(self):
        total = self.qty
        if self.parent:
            parent = BomFileContents.query.filter_by(id=self.parent).first()
            total = total * parent.total_required()

        return total

    @staticmethod
    def _get_parent_id(item_no, file_id):

        p = BomFileContents.query.filter_by(item_no=item_no, file_id=file_id).first()
        if p is not None:
            return p.id
        else:
            return None

    def _get_parent_item_no(self):
        parent = self.item_no.split(".")

        if len(parent) == 1:
            return None
        else:
            return ".".join(parent[:-1])

    def is_plate(self):
        contains = ["pl", "plate"]

        string = self.description.split("-")
        test = string[-1].lower()
        if string is not None:
            for item in contains:
                if test.startswith(item):
                    return True
        else:
            return False

    def has_length(self):
        if self.length is None:
            return False
        else:
            return True

    def is_material(self):
        out = self.has_length()
        if self.is_plate():
            out = False
        return out

    def __repr__(self):
        return f"<Item : {self.item_no} - {self.part_number} - {self.description}"
