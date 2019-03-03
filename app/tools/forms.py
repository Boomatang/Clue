from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BarSpacer(FlaskForm):
    post_to_post = StringField(
        "Spacing between posts", default="1500", validators=[DataRequired()]
    )
    spacing = StringField("Target bar gap", default="100", validators=[DataRequired()])
    bar_size = StringField("Bar size", default="12", validators=[DataRequired()])
    submit = SubmitField("Calculate")


class LouverCalculatorForm(FlaskForm):
    width = StringField(
        "Width of Louver",
        validators=[DataRequired(message="You most give a width for the louver")],
    )
    height = StringField(
        "Height of Louver",
        validators=[DataRequired(message="You most give a height for the louver")],
    )

    submit = SubmitField("Calculate")
