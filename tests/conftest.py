import pytest

from app import create_app, db


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app


@pytest.fixture(scope='session')
def session_clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app
