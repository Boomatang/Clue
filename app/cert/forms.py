from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.fields import SubmitField


class CertForm(FlaskForm):
    cert_folder = FileField(
        validators=[
            FileRequired(message="You most upload a zip folder to use this services.")
        ]
    )
    submit = SubmitField(label="Upload Zip File")
