import pytest
from flask import current_app, url_for

from app import db
from app.auth_models import User, Company

paths = ['main.index', 'auth.login', 'auth.register']


def test_app_exists(client):
    assert client is not None


def test_app_is_testing(client):
    assert current_app.config['TESTING']


@pytest.mark.single_thread
@pytest.mark.parametrize('path', paths)
def test_main_nav_paths(client, path):

    assert client.get(url_for(path)).status_code == 200


users = [{'email': 'pass1@example.com', 'password': 'cat'},
         {'email': 'pass2@example.com', 'password': 'cat'}]


@pytest.mark.parametrize('user', users)
def test_user_login_redirects_to_index(client, user):
    u = User()
    u.email = user['email']
    u.password = user['password']
    u.confirmed = True
    db.session.add(u)
    db.session.commit()
    data = {'email': user['email'],
            'password': user['password']}
    response = client.post(url_for('auth.login'),
                           data=data, follow_redirects=True)

    assert b'Version 3.1' in response.data


users = [{'email': 'fail1@example.com', 'password': 'fake'}]


@pytest.mark.parametrize('user', users)
def test_user_login_fails(client, user):
    data = {'email': user['email'],
            'password': user['password']}
    response = client.post(url_for('auth.login'),
                           data=data, follow_redirects=True)

    assert b'Invalid E-mail or Password' in response.data


users = [{'company': 'Boring Company', 'username': 'jim', 'email': 'jim@test.com',
          'password': 'cats1234', 'password2': 'cats1234'}]


@pytest.mark.parametrize('user', users)
def test_user_register_complete(clean_db, client, user):
    data = {'company': user['company'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],
            'password2': user['password2']}

    response = client.post(url_for('auth.register'),
                           data=data)
    db_user = User.query.filter_by(email=user['email']).first()

    assert response.status_code == 302
    assert db_user.username == user['username']
    assert db_user.company.owner.email == user['email']


users = [{'company': 'Boring Company', 'username': 'jim fitz', 'email': 'test@test.com', 'password': 'cats1234',
          'password2': 'cats1234', 'massage': b'must have only letters'},
         {'company': 'The Fast Company', 'username': 'jim', 'email': 'jim@test', 'password': 'cats1234', 'password2': 'cats1234',
          'massage': b'Invalid email address'},
         {'company': 'Bad Company', 'username': 'jim', 'email': 'jim@test.com', 'password': 'cats1234', 'password2': 'dog',
          'massage': b'Passwords must match'},
         {'company': 'Bad Company', 'username': 'jim', 'email': 'jim@test.com', 'password': 'cats',
          'password2': 'cats',
          'massage': b'8 characters long'}
         ]


@pytest.mark.parametrize('user', users)
def test_user_register_fails(clean_db, client, user):
    data = {'company': user['company'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],
            'password2': user['password2']}

    response = client.post(url_for('auth.register'),
                           data=data)

    assert user['massage'] in response.data


paths = ['main.test', 'auth.change_password', 'auth.password_reset_request',
         'auth.change_email_request']


@pytest.mark.single_thread
@pytest.mark.parametrize('path', paths)
def test_login_required(clean_db, client, path):
    u = User()
    u.password = 'cat'
    u.email = 'test@test.test'
    u.confirmed = True

    client.post(url_for('auth.login'),
                data={'email': 'test@test.com', 'password': 'cat'},
                follow_redirects=True)

    assert client.get(url_for(path), follow_redirects=True).status_code == 200


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


def login_user(user, client):
    data = {'email': user['email'],
            'password': user['password']}
    response = client.post(url_for('auth.login'),
                           data=data, follow_redirects=True)

    return response


users = [{'email': 'user1@example.com', 'password': 'cat', 'response': True},
         {'email': 'user2@example.com', 'password': 'cat', 'response': False}]


@pytest.mark.parametrize('user', users)
def test_menu_for_company_settings_link(client, clean_db, user):
    """Test if the user can see the company settings"""

    check_string = b'Company Settings'

    create_company()
    response = login_user(user, client)

    answer = check_string in response.data

    assert answer == user['response']


users = [{'email': 'user1@example.com', 'password': 'cat', 'response': True, 'company': 'ExampleCompanyOne.com',
          'asset': 'company1_asset', 'check': b'company1_asset'},
         {'email': 'user3@example.com', 'password': 'cat', 'response': True, 'company': 'ExampleCompanyOne.com',
          'asset': 'company1_asset', 'check': b'The requested URL was not found on the server'}]


@pytest.mark.parametrize('user', users)
def test_user_access_to_assets(client, clean_db, user):
    """Test if the user can see the company settings"""
    create_company()

    company = Company.load_company_by_name(user['company'])
    company.add_asset(user['asset'])

    check_string = user['check']

    login_user(user, client)

    response = client.get(url_for('main.test_asset', asset=user['asset']), follow_redirects=True)

    answer = check_string in response.data

    assert answer == user['response']
