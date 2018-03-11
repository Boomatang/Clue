from datetime import datetime

from . import db

material_size_lengths = db.Table('material_size_lengths',
                                 db.Column('size_id', db.Integer, db.ForeignKey('material.id'), primary_key=True),
                                 db.Column('length_id', db.Integer, db.ForeignKey('material_length.id'),
                                           primary_key=True)
                                 )


class MaterialSize(db.Model):
    __tablename__ = 'material'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64), unique=True)
    lengths = db.relationship('MaterialLength', secondary=material_size_lengths, lazy='subquery',
                              backref=db.backref('sizes', lazy=True))

    @staticmethod
    def add_new_material(size, lengths):
        print('hello world')

        entry = MaterialSize.query.filter_by(size=size).first()

        if entry is None:
            entry = MaterialSize(size=size)

            for length in lengths:
                entry_length = MaterialLength.query.filter_by(length=int(length)).first()
                if entry_length is None:
                    entry_length = MaterialLength(length=int(length))
                entry.lengths.append(entry_length)
        db.session.add(entry)
        db.session.commit()

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
    items = db.relationship('BomFileContents', backref='file', lazy=True)

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
            return '.'.join(parent[:1])

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
    sizes = db.relationship('BomSessionSize', backref='session', lazy=True)

    def __repr__(self):
        return f'<BomSession : {self.id} Timestamp : {self.timestamp}>'


class BomSessionSize(db.Model):
    __tablename__ = 'bom_session_size'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    default = db.Column(db.Integer)
    lengths = db.relationship('BomSessionLength', backref='size', lazy=True)
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
