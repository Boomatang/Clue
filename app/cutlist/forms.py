from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired


class CSVForm(FlaskForm):
    name = StringField('What ID to use?')
    csv = FileField('Upload File', validators=[DataRequired()])
    saw = StringField('Set saw margin value', default='50', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BasicForm(FlaskForm):
    submit = SubmitField('Submit')
