from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class BasicForm(FlaskForm):
    submit = SubmitField('Submit')


class CSVForm(FlaskForm):
    name = StringField('What ID to use?')
    csv = FileField('Upload File', validators=[DataRequired()])
    saw = StringField('Set saw margin value', default='50', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BarSpacer(FlaskForm):
    post_to_post = StringField('Spacing between posts', default='1500', validators=[DataRequired()])
    spacing = StringField('Target bar gap', default='100', validators=[DataRequired()])
    bar_size = StringField('Bar size', default='12', validators=[DataRequired()])
    submit = SubmitField('Calculate')


class BOMUpload(FlaskForm):
    comment = StringField('Add a comment for use Later')
    file_name = FileField('Upload File, This should be a CSV file.', validators=[DataRequired()])
    submit = SubmitField('Submit')