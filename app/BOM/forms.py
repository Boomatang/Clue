from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, SelectField
from wtforms.validators import DataRequired

from app.models import Project
from app.utils import logger


def get_projects(company):
    """Get a list of project that a user has access too"""

    choices = []

    values = Project.query.filter_by(company=company).order_by(Project.job_number).all()[:]

    if len(values) == 0:
        logger.info("There was no project for the company when building the form")
    else:

        choices.append(("None", "Select Project Or No Project"))

        for value in values:
            value_name = f"{value.job_number} - {value.name}"
            value_id = value.id

            choices.append((value_id, value_name))
    return choices


class BOMUpload(FlaskForm):
    job_number = StringField("Job number")
    comment = StringField("Add a comment for use Later")
    file_name = FileField(
        "Upload File, This should be a CSV file.", validators=[DataRequired()]
    )

    projects = SelectField("Select a Project")

    submit = SubmitField("Submit")

    def __init__(self, company):
        FlaskForm.__init__(self)
        self.projects.choices = get_projects(company)
