import datetime
from flask import render_template, flash, url_for, redirect
from flask_login import login_required, current_user

from app import db
from app.decorators import company_asset
from app.models import Project
from app.project import project
from app.project.form import AddProject


@project.route("/")
@login_required
def index():

    projects = Project.query.filter_by(company=current_user.company.id).order_by(
        Project.job_number.desc()
    )[:]

    return render_template("project/index.html", projects=projects)


@project.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = AddProject()
    if form.validate_on_submit():
        entry = Project()
        entry.job_number = form.job_number.data
        entry.client = form.client.data
        entry.name = form.project.data
        entry.timestamp = datetime.datetime.now()
        entry.company = current_user.company.id
        db.session.add(entry)
        db.session.commit()

        current_user.company.add_asset(entry.asset)
        db.session.commit()

        flash("Project added")
        return redirect(url_for("project.view", asset=entry.asset))

    return render_template("project/add.html", form=form)


@project.route("/project/<asset>")
@login_required
@company_asset()
def view(asset):

    db_entry: Project = Project.query.filter_by(asset=asset).first_or_404()
    db_entry.last_active = datetime.datetime.now()

    return render_template("project/view.html", project=db_entry)
