from sqlalchemy.exc import IntegrityError

from flask import render_template, request, flash, redirect, url_for, session, logging

from app import db
from app.librarys import library
from app.librarys.forms import AddClass, testform, RemoveClassForm
from app.models import MaterialSize, MaterialClass
from app.utils import isInt, hasName, hasValues, error_builder
from manage import app


@library.route('/', methods=['POST', 'GET'])
def material_library():
    size = MaterialSize.query.order_by(MaterialSize.size).all()[:]
    types = []
    for item in MaterialClass.query.order_by(MaterialClass.name).all()[:]:
        if item.has_materials():
            types.append(item)
    if not len(size):
        return render_template('materials/no_materials.html')

    return render_template('materials/index.html', units=size, types=types)


@library.route('/<material_id>', methods=['POST', 'GET'])
def material_view(material_id):

    unit: MaterialSize = MaterialSize.query.filter_by(id=material_id).first_or_404()
    choice = unit.class_id

    form = testform(material_id)

    if form.is_submitted():
        print(request.form.getlist('remove'))
        remove_lengths = request.form.getlist('remove')
        remove_lengths = [int(l) for l in remove_lengths]

        print(remove_lengths)
        if len(remove_lengths):
            unit.remove_lengths(remove_lengths)
            flash(f"{remove_lengths} has been removed from {unit.size}")

        new_length = form.add.data
        if len(new_length):
            if isInt(new_length):
                unit.add_length(new_length)
                flash(f"{new_length} has been added to {unit.size}")

            else:
                flash('The length most be a whole number.', 'error')

        if form.choice.data != choice:
            unit.class_id = form.choice.data
            db.session.add(unit)
            db.session.commit()

        # return redirect(url_for(".material_view", material_id=material_id))
        return redirect(url_for(".material_library"))

    return render_template('materials/view.html', unit=unit, form=form, choice=choice)


@library.route('/material-edit', methods=['POST', 'GET'])
def material_edit():

    if request.method == 'POST':
        flash('Got Post')

        for item in request.values.items(multi=True):
            print(item)

    return render_template('materials/edit.html')


@library.route('/material/add', methods=['POST', 'GET'])
def material_add():

    if request.method == "POST":

        size = request.form.get('size')
        lengths = request.form.getlist('lengths')

        checked_lengths = []
        failed_lengths = []

        for length in lengths:
            if isInt(length):
                checked_lengths.append(int(length))
            else:
                failed_lengths.append(length)

        if len(failed_lengths) > 1:
            flash(error_builder(failed_lengths))

        if hasName(size) and hasValues(checked_lengths):
            MaterialSize.add_new_material(size, checked_lengths)
            flash(f'{size} has been added to the database')

        else:
            flash('There was some error with your input please try again')
            return redirect(url_for('.material_add'))

        print(f'this was the size {size}')
        print(f'lengths are {checked_lengths}')

    return render_template('materials/add.html')


def get_choices():
    results = []

    for item in MaterialClass.query.all():
        local = {
            "id": item.id,
            "description": item.name,
            "selected": False,
        }

        if item.name == "Undefined":
            local["selected"] = True

        results.append(local)

    return results


@library.route('/missing', methods=['POST', 'GET'])
def material_missing():
    material = session['material_missing']
    choices = get_choices()

    if request.method == "POST":

        size = material
        lengths = request.form.getlist('lengths')
        group = request.form.get('choice')

        checked_lengths = []
        failed_lengths = []

        for length in lengths:
            if isInt(length):
                checked_lengths.append(int(length))
            else:
                failed_lengths.append(length)

        if len(failed_lengths) > 1:
            flash(error_builder(failed_lengths))

        if hasName(size) and hasValues(checked_lengths):
            MaterialSize.add_new_material(size, checked_lengths, group=group)
            flash(f'{size} has been added to the database')
            return redirect(url_for('BOM.BOM_setup'))

        else:
            flash('There was some error with your input please try again')
            return redirect(url_for('.material_missing'))

    return render_template('materials/missing.html', material=material, choices=choices)


@library.route("/classes", methods=["POST", "GET"])
def material_classes():
    add_form = AddClass(prefix="add_form")
    remove_form = RemoveClassForm(prefix="remove_form")

    if add_form.is_submitted():
        if add_form.validate():
            material_class = MaterialClass(
                name=add_form.name.data,
                description=add_form.description.data
            )
            try:
                db.session.add(material_class)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                flash("There was an error saving your entry. It looks like that name was used before.")
            return redirect(url_for(".material_classes"))

        else:
            flash_form_errors(add_form)

    if remove_form.is_submitted():
        data = request.form.getlist('remove')
        if len(data):
            default = MaterialClass.query.filter_by(name="Undefined").first_or_404()
            remove = False
            for item in data:
                if isInt(item):
                    entry: MaterialClass = MaterialClass.query.filter_by(id=int(item)).first_or_404()

                    if entry.id != default.id:
                        for material in entry.materials:
                            default.materials.append(material)

                        entry.materials = []
                        db.session.delete(entry)
                        remove = True
                    else:
                        flash(f"You cannot remove the {default.name} class. Its a system default.")
            db.session.add(default)
            db.session.commit()
            if remove:
                flash("Material Class has been removed.")
            return redirect(url_for(".material_classes"))

    return render_template('materials/classes.html', add_form=add_form, remove_form=remove_form)


def flash_form_errors(form):
    for error in form.errors:
        if error != "csrf_token":
            flash(form.errors[error][0])
