from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import Required


class BasicForm(FlaskForm):
    submit = SubmitField('Submit')


class CSVForm(FlaskForm):
    name = StringField('What ID to use?', validators=[Required()])
    csv = FileField('Upload File', validators=[Required()])
    submit = SubmitField('Submit')

