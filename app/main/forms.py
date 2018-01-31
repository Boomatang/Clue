from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class BasicForm(FlaskForm):
    submit = SubmitField('Submit')


class CSVForm(FlaskForm):
    name = StringField('What ID to use?', validators=[DataRequired()])
    csv = FileField('Upload File', validators=[DataRequired()])
    submit = SubmitField('Submit')


class BarSpacer(FlaskForm):
    post_to_post = StringField('Spacing between posts', default='1500', validators=[DataRequired()])
    spacing = StringField('Target bar gap', default='100', validators=[DataRequired()])
    bar_size = StringField('Bar size', default='12', validators=[DataRequired()])
    submit = SubmitField('Calculate')
