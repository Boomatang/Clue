from . import db


class Sample(db.Model):
    __tablename__ = 'sample'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

