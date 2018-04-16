import os

from flask import flash, redirect, url_for, session, render_template, request
from werkzeug.utils import secure_filename

from app.cutlist import cutlist
from app.cutlist.forms import CSVForm, BasicForm
from app.smart import BOM
from app.utils import file_ext_checker, isFloat, flash_massages


@cutlist.route('/form1', methods=['POST', 'GET'])
def bom_start():
    form = CSVForm()

    if form.validate_on_submit():
        f = form.csv.data

        filename = secure_filename(f.filename)
        name = os.path.join(os.environ.get('CLUE_UPLOADS', os.environ.get('HOME') + '/Public'), filename)

        f.save(name)

        if not file_ext_checker(str(name)):
            flash('File type was not a CSV file type.', 'Error')
            return redirect(url_for('.bom_start'))

        session['filename'] = str(name)

        if isFloat(form.saw.data):
            session['saw'] = float(form.saw.data)
        else:
            session['saw'] = float(form.saw.default)
            flash(f'The entered saw margin value was not a number. '
                  f'The default value of {form.saw.default} will be used.')
        if form.name.data:
            session['ref'] = form.name.data
        else:
            base_name = os.path.basename(name)

            temp = os.path.splitext(base_name)[0]
            session['ref'] = temp
            flash(f'No reference number was given. Using file file name as reference : {temp}.')

        return redirect(url_for('.bom_edit'))

    return render_template('play/bom_start.html', form=form)


@cutlist.route('/form2', methods=['POST', 'GET'])
def bom_edit():
    form = BasicForm()
    try:
        bom = BOM(session['filename'])
    except KeyError:
        return redirect(url_for('.bom_start'))

    keys = bom.keys()
    session_values = []
    flash_massages(bom.massages)

    if form.is_submitted():
        for item in request.values.items(multi=True):
            print(f"Item been passed in is {item}")
            session_values.append(item)

        session['values'] = session_values
        return redirect(url_for('.result'))

    return render_template('play/bom_edit.html', keys=keys, form=form)


@cutlist.route('/result')
def result():
    try:
        bom = BOM(session['filename'], ref=session['ref'])
    except KeyError:

        return redirect(url_for('.bom_start'))

    items = session['values']
    bom.set_saw_error_value(session['saw'])
    for item in items:
        bom.update_stock(item)
    bom.create_results()
    flash_massages(bom.massages)
    session.clear()

    return render_template('play/results.html', bom=bom)
