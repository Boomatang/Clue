import datetime
from flask import render_template, flash, url_for, redirect, request, current_app
from flask_login import login_required, current_user

from app import db
from app.decorators import company_asset
from app.models import Project, BomResult
from app.project import project
from app.project.form import AddProject, AddBOMToProjectForm
from app.smart.smart import find_project_id_from_id


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


@project.route("/<asset>")
@login_required
@company_asset()
def view(asset):
    db_entry: Project = Project.query.filter_by(asset=asset).first_or_404()
    db_entry.last_active = datetime.datetime.now()

    page = request.args.get("page", 1, type=int)
    pagination = (
        BomResult.query.filter_by(company=current_user.company.id, project_id=db_entry.id)
            .order_by(BomResult.timestamp.desc())
            .paginate(page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False)
    )
    BOM_results = pagination.items

    return render_template("project/view.html",
                           project=db_entry,
                           BOM_results=BOM_results,
                           pagination=pagination
                           )


@project.route("/bom/<asset>", methods=['GET', 'POST'])
@login_required
@company_asset()
def add_project_to_bom(asset):
    """Add a project to an existing BOM"""

    form = AddBOMToProjectForm(current_user.company.id)

    if form.submit.data:
        new_project_id = form.projects.data

        project_id = find_project_id_from_id(new_project_id)

        bom: BomResult = BomResult.query.filter_by(asset=asset).first()
        bom.project_id = project_id
        db.session.commit()

        flash("Project has been add to BOM")
        return redirect(url_for('BOM.BOM_result', asset=asset))

    return render_template("project/bom_add.html", form=form)
