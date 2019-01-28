import pytest
from flask import url_for

from app import create_app, db
from app.auth_models import User, Company


@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    create_company()

    yield app

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope='function')
def clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    create_company()
    yield app


@pytest.fixture(scope='session')
def session_clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app


def create_company():
    user1 = User(username='User1', email='user1@example.com', password='cat', confirmed=True)
    user2 = User(username='User2', email='user2@example.com', password='cat', confirmed=True)
    user3 = User(username='User3', email='user3@example.com', password='cat', confirmed=True)
    user4 = User(username='User4', email='user4@example.com', password='cat', confirmed=True)

    company1 = Company(name='ExampleCompanyOne.com')
    company2 = Company(name='ExampleCompanyTwo.com')

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)

    company1.add_user(user1)
    company1.add_user(user2)
    company1.set_company_owner(user1)
    db.session.add(company1)

    company2.add_user(user3)
    company2.add_user(user4)
    company2.set_company_owner(user3)
    db.session.add(company2)

    db.session.commit()


def login_standard_user(client):
    data = {'email': 'user1@example.com',
            'password': 'cat'}
    response = client.post(url_for('auth.login'),
                           data=data, follow_redirects=True)

    return response
