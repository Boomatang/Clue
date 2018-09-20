import pytest
from datetime import datetime

from app.models import Certs
from app import db


def test_adding_cert_data(client, clean_db):
    a = Certs()
    db.session.add(a)
    db.session.commit()

    result = Certs.query.all()
    expected = 1
    assert len(result) == expected


@pytest.fixture(scope="session")
def simple_model(session_clean_db):
    a = Certs()
    a.run_time = 55.5
    a.file_count = 45
    a.upload_file = "/upload/file"
    a.download_file = "/download/file"

    db.session.add(a)
    db.session.commit()

    yield a


def test_field_type_date(client, simple_model):
    result: Certs = Certs.query.first()
    assert type(result.date) == datetime


def test_field_type_run_time(client, simple_model):
    result: Certs = Certs.query.first()
    assert type(result.run_time) == float


def test_field_type_file_count(client, simple_model):
    result: Certs = Certs.query.first()
    assert type(result.file_count) == int


def test_field_type_upload_file(client, simple_model):

    result: Certs = Certs.query.first()
    assert type(result.upload_file) == str


def test_field_type_download_file(client, simple_model):

    result: Certs = Certs.query.first()
    assert type(result.download_file) == str
