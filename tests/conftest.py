import pytest
from flask import url_for

from app import create_app, db
from app.auth_models import User, Company
from app.models import BomSession, BomSessionLength, BomSessionSize, BomResult
from app.smart import RawBomFile, CreateBom


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    create_company()

    yield app

    db.session.remove()
    db.drop_all()


@pytest.fixture(scope="function")
def clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    create_company()
    yield app


@pytest.fixture(scope="session")
def session_clean_db(app):
    db.session.remove()
    db.drop_all()
    db.create_all()
    yield app


def create_company():
    user1 = User(
        username="User1", email="user1@example.com", password="cat", confirmed=True
    )
    user2 = User(
        username="User2", email="user2@example.com", password="cat", confirmed=True
    )
    user3 = User(
        username="User3", email="user3@example.com", password="cat", confirmed=True
    )
    user4 = User(
        username="User4", email="user4@example.com", password="cat", confirmed=True
    )

    company1 = Company(name="ExampleCompanyOne.com")
    company2 = Company(name="ExampleCompanyTwo.com")

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
    data = {"email": "user1@example.com", "password": "cat"}
    response = client.post(url_for("auth.login"), data=data, follow_redirects=True)

    return response


@pytest.fixture()
def csv_file(tmpdir):
    p = tmpdir.mkdir("sub").join("sample.csv")
    p.write(
        "ITEM NO.,PART NUMBER,DESCRIPTION,3D-Bounding Box Length,3D-Bounding Box Width,3D-Bounding Box Thickness,"
        "LENGTH,QTY.\n "
        "1,18-06-148-J01-A01,,,,,,3\n"
        "1.1,  18-06-148-J01-P01,,,,,,3\n"
        "1.1.1,    ,large,,,,6000,3"
    )

    return p


@pytest.fixture()
def setup_for_creating_bom(clean_db, csv_file):

    raw: RawBomFile = RawBomFile(csv_file)
    entry = raw.return_entry()
    db.session.add(entry)

    bom_session: BomSession = BomSession(id=1)
    db.session.add(bom_session)

    length = BomSessionLength(length=6500, size_id=1)

    db.session.add(length)

    size = BomSessionSize(
        id=1, size="large", session_id=1, lengths=[length], default=6500
    )
    db.session.add(size)

    db.session.commit()
    entry.configure_file()


@pytest.fixture()
def simple_bom(client, setup_for_creating_bom):

    bom = CreateBom(setup=1, data=1)
    bom.run()

    login_standard_user(client)
    result: BomResult = bom.create_result()

    return result
