import datetime
import pytest
import re
from flask import url_for

from app import db
from app.models import Project
from tests.conftest import login_standard_user


def test_add_project_to_db(client, clean_db):
    entry = Project()

    entry.client = "project client"
    entry.name = "project name"
    entry.job_number = "project job number"
    entry.timestamp = datetime.datetime.now()
    entry.last_active = datetime.datetime.now()

    db.session.add(entry)
    db.session.commit()

    db_entry = Project.query.first_or_404()

    assert entry == db_entry


def test_index_has_table(client):
    login_standard_user(client)
    page = client.get(url_for("project.index"))
    search = b'<table id="project_table"'
    assert re.search(search, page.data)


def test_adding_project_on_page(client, clean_db):
    data = {
        "job number": "18-09-275",
        "project": "Sample Project",
        "client": "Project Client",
    }
    login_standard_user(client)
    client.post(
        url_for("project.add"),
        data={
            "job_number": data["job number"],
            "project": data["project"],
            "client": data["client"],
        },
        follow_redirects=True,
    )
    db_entry = Project.query.filter_by(job_number=data["job number"]).first()

    assert data["job number"] == db_entry.job_number


@pytest.mark.xfail()
def test_project_view(client, clean_db):
    data = {
        "job number": "18-09-275",
        "project": "Sample Project",
        "client": "Project Client",
    }

    entry = Project(
        job_number=data["job number"], name=data["project"], client=data["client"]
    )

    db.session.add(entry)
    db.session.commit()

    search_job_number = f"Job Number : {entry.job_number}"
    search_project = f"Project : {entry.name}"
    search_client = f"Client : {entry.client}"

    page = client.get(url_for("project.view", id=entry.id))

    search_data = str(page.data)

    assert re.search(search_job_number, search_data)
    assert re.search(search_project, search_data)
    assert re.search(search_client, search_data)
