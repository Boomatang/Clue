from datetime import datetime

from app import db


class Certs(db.Model):
    __tablename__ = "certs"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    file_count = db.Column(db.Integer)
    run_time = db.Column(db.Integer)
    upload_file = db.Column(db.String(250))
    download_file = db.Column(db.String(250))

    def timestamp_format(self):
        return f"{self.date:%d/%m/%Y}"
