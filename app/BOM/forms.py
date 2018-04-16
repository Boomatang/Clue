from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired


class BOMUpload(FlaskForm):
    comment = StringField('Add a comment for use Later')
    file_name = FileField('Upload File, This should be a CSV file.', validators=[DataRequired()])
    submit = SubmitField('Submit')