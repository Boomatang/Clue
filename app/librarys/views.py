from flask import render_template, request, flash, redirect, url_for, session

from app.librarys import library
from app.models import MaterialSize
from app.utils import isInt, hasName, hasValues, error_builder


@library.route('/material', methods=['POST', 'GET'])
def material_library():
    size = MaterialSize.query.order_by(MaterialSize.size).all()[:]
    if not len(size):
        return render_template('materials/no_materials.html')
    return render_template('materials/index.html', units=size)


@library.route('/materials/<material_id>', methods=['POST', 'GET'])
def material_view(material_id):

    unit: MaterialSize = MaterialSize.query.filter_by(id=material_id).first_or_404()

    if request.method == "POST":

        new_length = request.form.get('new-length')
        if len(new_length):
            if isInt(new_length):
                unit.add_length(new_length)
                flash(f"{new_length} has been added to {unit.size}")
                return redirect(url_for(".material_view", material_id=material_id))

            else:
                flash('The length most be a whole number.', 'error')
                return redirect(url_for(".material_view", material_id=material_id))

        remove_lengths = request.form.getlist('checkboxes')
        remove_lengths = [int(l) for l in remove_lengths]

        if len(remove_lengths):
            unit.remove_lengths(remove_lengths)
            flash(f"{remove_lengths} has been removed from {unit.size}")
            return redirect(url_for(".material_view", material_id=material_id))

    return render_template('materials/view.html', unit=unit)

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


@library.route('/material/missing', methods=['POST', 'GET'])
def material_missing():
    material = session['material_missing']

    if request.method == "POST":

        size = material
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
            return redirect(url_for('BOM.BOM_setup'))

        else:
            flash('There was some error with your input please try again')
            return redirect(url_for('.material_missing'))

    return render_template('materials/missing.html', material=material)