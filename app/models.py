import statistics
from datetime import datetime

from . import db

material_size_lengths = db.Table('material_size_lengths',
                                 db.Column('size_id', db.Integer, db.ForeignKey('material.id'), primary_key=True),
                                 db.Column('length_id', db.Integer, db.ForeignKey('material_length.id'),
                                           primary_key=True)
                                 )


class MaterialClass(db.Model):
    __tablename__ = 'material_class'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    materials = db.relationship('MaterialSize', backref='type', lazy=True)

    def has_materials(self):
        if len(self.materials) > 0:
            return True
        else:
            return False

    @staticmethod
    def setup():
        MaterialClass._add_basic_classes()
        MaterialClass._set_default_classes_on_materials()

    @staticmethod
    def _add_basic_classes():
        items = [("Undefined", "This is the default when no class is add to the materials"),
                 ("Miscellaneous", "A list of various materials from different sources")]

        for item in items:
            entry = MaterialClass(name=item[0], description=item[1])
            db.session.add(entry)
        db.session.commit()

    @staticmethod
    def _set_default_classes_on_materials():
        default = MaterialClass.query.filter_by(name="Undefined").first()

        for entry in MaterialSize.query.all():
            entry.type = default

        db.session.commit()


class MaterialSize(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64), unique=True)
    lengths = db.relationship('MaterialLength', secondary=material_size_lengths, lazy='subquery',
                              backref=db.backref('sizes', lazy=False))
    default = "Not Working"
    class_id = db.Column(db.Integer, db.ForeignKey('material_class.id'))

    @staticmethod
    def add_new_material(size, lengths, group=None):
        entry = MaterialSize.query.filter_by(size=size).first()

        if entry is None:
            entry = MaterialSize(size=size)

            if group:
                entry.class_id = group

            for length in lengths:
                entry_length = MaterialLength.query.filter_by(length=int(length)).first()
                if entry_length is None:
                    entry_length = MaterialLength(length=int(length))
                entry.lengths.append(entry_length)
        db.session.add(entry)
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
        return f'<Size : {self.size}>'


class MaterialLength(db.Model):
    __tablename__ = 'material_length'
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer, unique=True)

    def __repr__(self):
        return f'<Length : {self.length}>'


class BomFile(db.Model):
    __tablename__ = 'bom_files'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    comment = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('BomFileContents', cascade="all, delete-orphan", backref='file', lazy=True)
    results = db.relationship('BomResult', cascade="all, delete-orphan", backref='file', lazy=True)

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
            material.append('No materials Found')

        return material

    def __repr__(self):
        return f'<File Name : {self.name}'


class BomFileContents(db.Model):
    __tablename__ = 'bom_file_contents'
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
    file_id = db.Column(db.Integer, db.ForeignKey('bom_files.id'), nullable=False)

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
        parent = self.item_no.split('.')

        if len(parent) == 1:
            return None
        else:
            return '.'.join(parent[:-1])

    def is_plate(self):
        contains = ['pl', 'plate']

        string = self.description.split('-')
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
        return f'<Item : {self.item_no} - {self.part_number} - {self.description}'


class BomSession(db.Model):
    __tablename__ = 'bom_session'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sizes = db.relationship('BomSessionSize', cascade="all, delete-orphan", backref='session', lazy=True)

    def __repr__(self):
        return f'<BomSession : {self.id} Timestamp : {self.timestamp}>'


class BomSessionSize(db.Model):
    __tablename__ = 'bom_session_size'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    default = db.Column(db.Integer)
    lengths = db.relationship('BomSessionLength', cascade="all, delete-orphan", backref='size', lazy=True)
    session_id = db.Column(db.Integer, db.ForeignKey('bom_session.id'), nullable=False)

    def __repr__(self):
        return f'<BomSessionSize : {self.size}>'


class BomSessionLength(db.Model):
    __tablename__ = 'bom_session_length'
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer)
    size_id = db.Column(db.Integer, db.ForeignKey('bom_session_size.id'), nullable=False)

    def __repr__(self):
        return f'<BomSessionLength : {self.length}>'


class BomResult(db.Model):
    __tablename__ = 'bom_result'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    __job_number = db.Column(db.String)
    comment = db.Column(db.String)
    file_id = db.Column(db.Integer, db.ForeignKey('bom_files.id'), nullable=False)
    material = db.relationship('BomResultMaterial', cascade="all, delete-orphan", backref='result', lazy=True)

    @property
    def job_number(self):
        return self.__job_number

    @job_number.setter
    def job_number(self, number):
        self.__job_number = number

    @job_number.getter
    def job_number(self):
        if self.__job_number is not None:
            return self.__job_number
        else:
            return "Unknown"

    @property
    def lengths(self):
        out = []

        for material in self.material:
            for beam in material.beams:
                if beam.length not in out:
                    out.append(beam.length)
        return out

    def timestamp_format(self):
        return f"{self.timestamp:%d/%m/%Y}"

    def delete(self):
        for material in self.material:
            material.delete()

        db.session.delete(self)
        # db.session.commit()

    def material_review(self):

        return (i.size for i in self.material)

    def required_lengths(self, size):
        lengths = []
        for item in self.material:
            if item.size == size:
                for beam in item.beams:
                    if beam.length not in lengths:
                        lengths.append(beam.length)
        return lengths

    def required_length_qty(self, size, length):
        counter = 0
        for item in self.material:
            if item.size == size:
                for beam in item.beams:
                    if beam.length == length:
                        counter += 1
        return counter

    def material_missing(self, material):
        for item in self.material:
            if material == item.size:
                return len(item.missing)

    def get_beams_for_material(self, material):

        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()

        return size.beams

    def get_missing_parts_for_material(self, material):

        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()

        return size.missing

    def is_missing_parts_for_material(self, material):

        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()
        if len(size.missing):
            return True

        return False

    def has_missing_parts(self):
        for item in self.material:
            if len(item.missing):
                return True

        return False

    def material_average_percentage(self, material):
        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()

        return size.average()

    def material_low_percentage(self, material):
        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()

        return size.low()

    def material_high_percentage(self, material):
        size = BomResultMaterial.query.filter_by(result_id=self.id, size=material).first()

        return size.high()


class BomResultMaterial(db.Model):
    __tablename__ = 'bom_result_material'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    beams = db.relationship('BomResultBeam', backref='material', lazy=True)
    missing = db.relationship('BomResultMissingPart', cascade="all,delete-orphan", backref='material', lazy=True)
    result_id = db.Column(db.Integer, db.ForeignKey('bom_result.id'), nullable=False)

    def delete(self):
        for beam in self.beams:
            beam.delete()

        for part in self.missing:
            part.delete()

        db.session.delete(self)
        # db.session.commit()

    def average(self):
        return round(statistics.mean(self._all_lengths()))

    def low(self):

        return min([x for x in self._all_lengths()])

    def high(self):
        return max([x for x in self._all_lengths()])

    def _all_lengths(self):
        avg = []
        for beam in self.beams:
            avg.append(beam.get_percentage())
        if len(avg) > 0:
            return avg
        else:
            return [0, 0]


class BomResultBeam(db.Model):
    __tablename__ = 'bom_result_beam'
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer)
    waste = db.Column(db.Integer)
    material_id = db.Column(db.Integer, db.ForeignKey('bom_result_material.id'), nullable=False)
    parts = db.relationship('BomResultBeamPart', cascade="all, delete-orphan", backref='beam', lazy=True)

    def delete(self):
        for part in self.parts:
            part.delete()

        db.session.delete(self)
        # db.session.commit()

    def get_percentage(self):
        one = self.length / 100
        total = self.length - self.waste
        try:
            return round(total / one)
        except ZeroDivisionError:
            return 0

    def progress_bar_state(self):
        if self.get_percentage() < 60:
            return "error"
        elif self.get_percentage() < 80:
            return "warning"
        else:
            return "success"


class BomResultBeamPart(db.Model):
    __tablename__ = 'bom_result_beam_part'
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(64))
    length = db.Column(db.Float)
    qty = db.Column(db.Integer)
    beam_id = db.Column(db.Integer, db.ForeignKey('bom_result_beam.id'), nullable=False)

    def delete(self):
        db.session.delete(self)
        # db.session.commit()


class BomResultMissingPart(db.Model):
    __tablename__ = 'bom_result_missing_part'
    id = db.Column(db.Integer, primary_key=True)
    item_no = db.Column(db.String(64))
    length = db.Column(db.Float)
    qty = db.Column(db.Integer)
    material_id = db.Column(db.Integer, db.ForeignKey('bom_result_material.id'), nullable=False)

    def delete(self):
        db.session.delete(self)
        # db.session.commit()
