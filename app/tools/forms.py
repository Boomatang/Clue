from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BarSpacer(FlaskForm):
    post_to_post = StringField('Spacing between posts', default='1500', validators=[DataRequired()])
    spacing = StringField('Target bar gap', default='100', validators=[DataRequired()])
    bar_size = StringField('Bar size', default='12', validators=[DataRequired()])
    submit = SubmitField('Calculate')
