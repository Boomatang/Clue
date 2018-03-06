from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, session
from . import main
from .forms import CSVForm, BasicForm, BarSpacer
from werkzeug.utils import secure_filename
import os
from ..smart import BOM, BarSpacingCalculator
from ..utils import file_ext_checker, isFloat


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
def index():
    return render_template('index.html')


# This section is for the create cutting list

@main.route('/form1', methods=['POST', 'GET'])
def bom_start():
    form = CSVForm()

    if form.validate_on_submit():
        f = form.csv.data

        filename = secure_filename(f.filename)
        name = os.path.join(os.environ.get('CLUE_UPLOADS'), filename)

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

    return render_template('/play/bom_start.html', form=form)


@main.route('/form2', methods=['POST', 'GET'])
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
            # bom.update_stock(item)
            session_values.append(item)
        # print(help(request.values)) 
        
        # bom.create_results()

        session['values'] = session_values
        return redirect(url_for('.result'))

    return render_template('/play/bom_edit.html', keys=keys, form=form)


@main.route('/result')
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

    return render_template('/play/results.html', bom=bom)

# this section is for calculates


@main.route('/bar-spacer', methods=['POST', 'GET'])
def bar_spacer():
    form = BarSpacer()
    bar = None

    if form.validate_on_submit():
        between_post = form.post_to_post.data
        gap = form.spacing.data
        size = form.bar_size.data

        all = [between_post, gap, size]

        for a in all:
            if isFloat(a):
                pass
            else:
                flash('All you\'re input needs to be a number.', 'error')
                return redirect(url_for('.bar_spacer'))

        bar = BarSpacingCalculator(float(gap), float(between_post), float(size))
        return render_template('/utls/bar-spacer.html', form=form, bar=bar)

    return render_template('/utls/bar-spacer.html', form=form, bar=bar)

# This section is for the material library


@main.route('/material', methods=['POST', 'GET'])
def material_library():
    units = [1, 2, 3, 4, 5, 6]
    return render_template('/materials/index.html', units=units)


@main.route('/material/<material_id>', methods=['POST', 'GET'])
def material_view(material_id):
    print(material_id)
    return render_template('/materials/view.html')


@main.route('/material/add', methods=['POST', 'GET'])
def material_add():
    return render_template('/materials/add.html')


# This section has helper methods


def flash_massages(massage_list):
    for massage in massage_list:
        if massage[1] is None:
            status = 'General'
        else:
            status = massage[1]
        flash(massage[0], status)
