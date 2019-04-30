from datetime import datetime

from app import db


class BomSession(db.Model):
    __tablename__ = "bom_session"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sizes = db.relationship(
        "BomSessionSize", cascade="all, delete-orphan", backref="session", lazy=True
    )

    def __repr__(self):
        return f"<BomSession : {self.id} Timestamp : {self.timestamp}>"


class BomSessionSize(db.Model):
    __tablename__ = "bom_session_size"
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(64))
    default = db.Column(db.Integer)
    lengths = db.relationship(
        "BomSessionLength", cascade="all, delete-orphan", backref="size", lazy=True
    )
    session_id = db.Column(db.Integer, db.ForeignKey("bom_session.id"), nullable=False)

    def __repr__(self):
        return f"<BomSessionSize : {self.size}>"


class BomSessionLength(db.Model):
    __tablename__ = "bom_session_length"
    id = db.Column(db.Integer, primary_key=True)
    length = db.Column(db.Integer)
    size_id = db.Column(
        db.Integer, db.ForeignKey("bom_session_size.id"), nullable=False
    )

    def __repr__(self):
        return f"<BomSessionLength : {self.length}>"
