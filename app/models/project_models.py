from app import db
from app.models import uuid_key


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    client = db.Column(db.String(100))
    job_number = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime)
    last_active = db.Column(db.DateTime)
    company = db.Column(db.Integer)
    asset = db.Column(db.String(64), index=True, default=uuid_key)
    is_active = db.Column(db.BOOLEAN, default=True)
    bom = db.relationship(
        "BomResult", cascade="all, delete-orphan", backref="project", lazy=True
    )

    @property
    def bom_count(self):
        return len(self.bom)
