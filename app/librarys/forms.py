from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import html_params

from app.models import MaterialSize, MaterialClass


class ChoicesBase:
    def __init__(self, material_id):
        self.choices = self._get_choices(material_id)
        self.name = None
        self.id = None

    def iter_choices(self):
        for choice in self.choices:
            yield choice

    @staticmethod
    def _get_choices(material_id=None):
        result = []
        size: MaterialSize = MaterialSize.query.filter_by(id=material_id).first_or_404()

        for length in size.lengths:
            result.append((length.id, length.length, False))

        return result


class ClassList(ChoicesBase):
    def __init__(self, company):
        ChoicesBase.__init__(self, None)
        self.choices = self._get_choices(company=company)

    @staticmethod
    def _get_choices(material_id=None, company=None):
        results = []

        for item in MaterialClass.query.filter_by(company=company).all():
            results.append((item.id, item.name, False))

        return results


def select_multi_checkbox(field, ul_class="", **kwargs):
    """When this is called you need to pipe it through safe"""
    kwargs.setdefault("type", "checkbox")
    field_id = kwargs.pop("id", field.id)
    html = [u'<div class="list" %s>' % html_params(id=field_id, class_=ul_class)]
    for value, label, checked in field.iter_choices():
        choice_id = u"%s-%s" % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options["checked"] = "checked"
        html.append(u'<div class="item">')
        html.append(u'<div class="ui toggle checkbox">')
        html.append(u'<label for="%s">%s</label>' % (field_id, label))
        html.append(u"<input %s /> " % html_params(**options))
        html.append(u"</div>")
        html.append(u"</div>")
        html.append(u"<br>")

    html.append(u"</div>")
    return u"".join(html)


def material_classes():
    things = []

    values = MaterialClass.query.all()[:]
    for value in values:
        things.append((value.id, value.name))

    return things


def material_default_class(material):
    result = MaterialSize.query.filter_by(id=material).first_or_404()
    return result.type.id


class AddClass(FlaskForm):
    name = StringField(
        "Class Name", validators=[DataRequired("A class name is required")]
    )
    description = TextAreaField("Description of Class")
    submit = SubmitField("Submit")


class testform(FlaskForm):
    add = StringField("Add Beam Length")
    choice = SelectField("Select Material Class")
    submit = SubmitField("Update Material")

    def __init__(self, material_id):
        FlaskForm.__init__(self)
        choices = ChoicesBase(material_id)

        choices.id = "remove"
        choices.name = "remove"
        self.check = select_multi_checkbox(choices)
        self.choice.choices = material_classes()


class RemoveClassForm(FlaskForm):
    submit = SubmitField("Remove Material Class")

    def __init__(self, company, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        choices = ClassList(company=company)

        choices.id = "remove"
        choices.name = "remove"
        self.check = select_multi_checkbox(choices)
