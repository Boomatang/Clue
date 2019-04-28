from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

from app.BOM.forms import get_projects


class AddProject(FlaskForm):
    job_number = StringField(
        label="Job Number",
        validators=[DataRequired(message="You must supply a job number")],
    )
    project = StringField(
        label="Project Name",
        validators=[DataRequired(message="You must supply a project name")],
    )
    client = StringField(
        label="Client Name",
        validators=[DataRequired(message="You must supply a client name")],
    )
    submit = SubmitField(label="Add Project")


class AddBOMToProjectForm(FlaskForm):
    projects = SelectField("Select a Project")

    submit = SubmitField("Submit")

    def __init__(self, company):
        FlaskForm.__init__(self)
        self.projects.choices = get_projects(company)
