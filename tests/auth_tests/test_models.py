import pytest

from app import db
from app.auth_models import User, Company


def test_user_password_setter():
    u = User()
    u.password = "cat"
    assert u.password_hash is not None


def test_user_no_password_getter():
    u = User()
    u.password = "cat"
    with pytest.raises(AttributeError):
        u.password


def test_user_password_verification():
    u = User()
    u.password = "cat"
    assert u.verify_password("cat")
    assert not u.verify_password("dog")


def test_user_salts_are_random():
    u = User()
    u.password = "cat"
    u2 = User()
    u2.password = "cat"

    assert u.password_hash != u2.password_hash


def test_valid_confirmation_token(clean_db):
    u = User()
    u.password = "cat"
    db.session.add(u)
    db.session.commit()

    token = u.generate_confirmation_token()

    assert u.confirm(token)


def test_create_company():
    c = Company()
    c.name = "test name"

    db.session.add(c)

    db.session.commit()

    db_c = Company.query.filter_by(name="test name").first()

    assert db_c == c


def test_company_add_users(clean_db):
    company = Company()
    company.name = "test name"

    user1 = User()
    user1.username = "Frank"
    user2 = User()
    user2.username = "John"

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(company)

    company.add_user(user1)
    company.add_user(user2)

    users = company.users

    assert user1 in users
    assert user2 in users


def test_company_owner(clean_db):
    name = "Test Company"
    company = Company()
    company.name = name

    user1 = User()
    user1.username = "Frank"

    db.session.add(user1)
    db.session.add(company)

    company.set_company_owner(user1)
    db.session.commit()

    db_company = Company.query.filter_by(name=name).first()

    assert user1 == db_company.owner


def test_users_company_name(clean_db):
    company = Company()
    company.name = "test name"

    user1 = User()
    user1.username = "Frank"

    db.session.add(user1)
    db.session.add(company)

    company.add_user(user1)

    db.session.commit()

    assert user1.company.name == company.name
