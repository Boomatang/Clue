from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, make_response, session, config

from config import Config
from . import main
from .forms import CSVForm, BasicForm
from werkzeug.utils import secure_filename
import os
from ..smart import BOM


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


@main.route('/form1', methods=['POST', 'GET'])
def bom_start():
    form = CSVForm()

    if form.validate_on_submit():
        f = form.csv.data
        session['ref'] = form.name.data
        filename = secure_filename(f.filename)
        # name = os.path.join(Config.UPLOADS, filename)
        name = os.path.join(os.environ.get('CLUE_UPLOADS'), filename)
        f.save(name)
        session['filename'] = str(name)
        return redirect(url_for('.bom_edit'))

    return render_template('/play/bom_start.html', form=form)


@main.route('/form2', methods=['POST', 'GET'])
def bom_edit():
    form = BasicForm()

    bom = BOM(session['filename'])
    keys = bom.keys()
    session_values = []

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

    bom = BOM(session['filename'], ref=session['ref'])
    items = session['values']
    for item in items:
        bom.update_stock(item)
    bom.create_results()
    session.clear()

    return render_template('/play/results.html', bom=bom)