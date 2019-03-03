from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


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
