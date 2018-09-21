import datetime
from flask import render_template, flash, url_for, redirect

from app import db
from app.models import Project
from app.project import project
from app.project.form import AddProject


@project.route('/')
def index():

    projects = Project.query.order_by(Project.job_number.desc())[:]

    return render_template("project/index.html", projects=projects)


@project.route('/add', methods=['GET', 'POST'])
def add():
    form = AddProject()
    if form.validate_on_submit():
        entry = Project()
        entry.job_number = form.job_number.data
        entry.client = form.client.data
        entry.name = form.project.data
        entry.timestamp = datetime.datetime.now()
        db.session.add(entry)
        db.session.commit()
        flash("Project added")
        return redirect(url_for('project.view', id=entry.id))

    return render_template('project/add.html', form=form)


@project.route("/project/<id>")
def view(id):

    db_entry: Project = Project.query.filter_by(id=id).first_or_404()
    db_entry.last_active = datetime.datetime.now()

    return render_template('project/view.html', project=db_entry)
