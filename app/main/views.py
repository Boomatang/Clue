from flask import render_template, redirect, url_for, abort, flash, request, \
    current_app, session
from pprint import pprint

from app import db
from app.models import MaterialSize, BomFile, MaterialLength, BomSession, BomSessionLength, BomSessionSize, BomResult, \
    BomResultMaterial, BomResultBeam, BomResultBeamPart, BomResultMissingPart
from app.smart import RawBomFile, CreateBom
from . import main
from .forms import CSVForm, BasicForm, BarSpacer, BOMUpload
from werkzeug.utils import secure_filename
import os
from ..smart import BOM, BarSpacingCalculator
from ..utils import *


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


@main.route('/dashboard', methods=['POST', 'GET'])
def dashboard():

    BOM_results = BomResult.query.order_by(BomResult.timestamp).all()
    temp = []
    for r in BOM_results:
        temp.append(r)

    BOM_results = temp.reverse()
    return render_template('user/dashboard.html', BOM_results=temp)

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

    return render_template('play/bom_start.html', form=form)


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

    return render_template('play/bom_edit.html', keys=keys, form=form)


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

    return render_template("play/results.html", bom=bom)

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
        return render_template('utls/bar-spacer.html', form=form, bar=bar)

    return render_template('utls/bar-spacer.html', form=form, bar=bar)

# This section is for the material library


@main.route('/material', methods=['POST', 'GET'])
def material_library():
    size = MaterialSize.query.order_by(MaterialSize.size).all()[:]
    if not len(size):
        return render_template('materials/no_materials.html')
    return render_template('materials/index.html', units=size)


@main.route('/material/<material_id>', methods=['POST', 'GET'])
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


@main.route('/material/add', methods=['POST', 'GET'])
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


@main.route('/material/missing', methods=['POST', 'GET'])
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
            return redirect(url_for('.BOM_setup'))

        else:
            flash('There was some error with your input please try again')
            return redirect(url_for('.material_missing'))

    return render_template('materials/missing.html', material=material)

# This section is to do with uploading and creating the BOM


@main.route('/BOM/upload', methods=['POST', 'GET'])
def BOM_upload():
    form = BOMUpload()

    if form.validate_on_submit():
        f = form.file_name.data
        filename = secure_filename(f.filename)

        name = os.path.join(os.environ.get('CLUE_UPLOADS', '/home/boomatang/Public'), filename)

        if not file_ext_checker(str(name)):
            flash('File type was not a CSV file type.', 'Error')
            return redirect(url_for('.BOM_upload'))

        f.save(name)

        d = RawBomFile(name)

        entry = d.return_entry()
        entry.comment = form.comment.data
        db.session.add(entry)
        db.session.commit()
        entry.configure_file()

        session['file'] = entry.id

        return redirect(url_for('.BOM_setup'))

    return render_template('BOM/upload.html', form=form)


@main.route('/BOM/setup', methods=['POST', 'GET'])
def BOM_setup():

    bom = BomFile.query.filter_by(id=session['file']).first()

    materials = bom.materials_required()
    materials_used = []

    for material in materials:
        item = MaterialSize.query.filter_by(size=material).first()
        if item is not None:
            materials_used.append(item)
        else:
            session['material_missing'] = material
            return redirect(url_for('.material_missing'))

    if request.method == "POST":
        values = []

        # create a session object
        # passer keys
        # key values to session object
        """
        dict = {material: size,
                lengths: [ints],
                default: int}
        """
        for material in materials:
            value = {'material': material,
                     'lengths': []}
            for item in request.values.items(multi=True):
                if item[0].startswith(material):

                    if key_preferred(item[0]):
                        preferred_length = MaterialLength.query.filter_by(id=int(item[1])).first()
                        value['default'] = preferred_length.length

                    if key_checkbox(item[0]):
                        length = MaterialLength.query.filter_by(id=int(item[1])).first()
                        value['lengths'].append(length.length)
            values.append(value)

        entry = BomSession()

        db.session.add(entry)
        db.session.commit()
        for value in values:

            beams = BomSessionSize(size=value['material'], default=value['default'])
            entry.sizes.append(beams)
            db.session.add(beams)
            db.session.commit()
            for length in value.get('lengths', None):
                if length is not None:
                    beam = BomSessionLength(length=length)
                    beams.lengths.append(beam)

        db.session.commit()

        session['session_id'] = entry.id

        return redirect(url_for('.BOM_calculate'))

    return render_template('BOM/setup.html', materials=materials_used)


@main.route('/BOM/calculate')
def BOM_calculate():

    setup_id = session['session_id']
    data_id = session['file']

    BOM = CreateBom(setup_id, data_id)
    BOM.run()

    values = BOM.beams
    missing = BOM.un_cut_parts

    result: BomResult = BomResult()
    item: BomFile = BomFile.query.filter_by(id=session['file']).first()
    result.comment = item.comment
    item.results.append(result)
    db.session.add(result)
    db.session.commit()

    for key in values.keys():
        material = BomResultMaterial(size=key)
        result.material.append(material)
        db.session.commit()

        for beam in values[key]:
            b = BomResultBeam(length=beam['length'], waste=beam['waste'])
            material.beams.append(b)
            db.session.commit()

            for thing in beam['items']:
                part = BomResultBeamPart(item_no=beam['items'][thing]['item'],
                                         length=beam['items'][thing]['length'],
                                         qty=beam['items'][thing]['qty'])
                b.parts.append(part)
                db.session.commit()

        for item in missing:
            if key == item['description']:
                part_missing = BomResultMissingPart(item_no=item['item'], length=item['length'], qty=item['missing'])
                material.missing.append(part_missing)
                db.session.commit()
    return redirect(url_for('.BOM_result', result_id=result.id))


@main.route('/BOM/result/<result_id>', methods=['POST', 'GET'])
def BOM_result(result_id):
    result: BomResult = BomResult.query.filter_by(id=result_id).first_or_404()

    session['file'] = result.file_id

    return render_template('BOM/results.html', result=result)


@main.route('/BOM/results/remove/<result_id>', methods=['POST', 'GET'])
def BOM_remove_result(result_id):
    result: BomResult = BomResult.query.filter_by(id=result_id).first_or_404()
    massage = f"Your about to remove result {result.id}: {result.comment}"
    if request.method == "POST":
        print(request.values)
        for item in request.values.items(multi=True):
            if item[0] == 'disagree':
                return redirect(url_for('.dashboard'))
            print(item)
        print('deleting the item')
        result.delete()
        db.session.commit()
        return redirect(url_for('.dashboard'))

    return render_template('user/yes_no.html', massage=massage)

# This section has helper methods


def key_preferred(value: str):
    if value.endswith('preferred'):
        return True
    else:
        return False


def key_checkbox(value: str):
    if value.endswith('checkboxes'):
        return True
    else:
        return False


def error_builder(errors):
    msg = 'There was a problem with: '

    for error in errors:
        msg = msg + error + " "

    return msg


def flash_massages(massage_list):
    for massage in massage_list:
        if massage[1] is None:
            status = 'General'
        else:
            status = massage[1]
        flash(massage[0], status)
