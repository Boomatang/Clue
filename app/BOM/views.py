import os

from flask import flash, redirect, url_for, session, render_template, request
from werkzeug.utils import secure_filename

from app import db
from app.BOM import BOM
from app.BOM.forms import BOMUpload
from app.models import BomFile, MaterialSize, MaterialLength, BomSession, BomSessionSize, BomResult,\
    BomResultMaterial, BomResultBeam, BomResultBeamPart, BomResultMissingPart, BomSessionLength
from app.smart import RawBomFile, CreateBom
from app.utils import file_ext_checker, key_preferred, key_checkboxes


@BOM.route('/BOM/upload', methods=['POST', 'GET'])
def BOM_upload():
    form = BOMUpload()

    if form.is_submitted():
        f = form.file_name.data
        filename = secure_filename(f.filename)

        name = os.path.join(os.environ.get('CLUE_UPLOADS', '/home/boomatang/Public'), filename)

        if not file_ext_checker(str(name), '.csv'):
            flash('File type was not a CSV file type.', 'Error')
            return redirect(url_for('.BOM_upload'))

        f.save(name)

        d = RawBomFile(name)

        entry = d.return_entry()
        entry.comment = form.comment.data
        session['job_number'] = form.job_number.data
        db.session.add(entry)
        db.session.commit()
        entry.configure_file()

        session['file'] = entry.id

        return redirect(url_for('.BOM_setup'))

    return render_template('BOM/upload.html', form=form)


@BOM.route('/BOM/setup', methods=['POST', 'GET'])
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
            return redirect(url_for('library.material_missing'))

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

                    if key_checkboxes(item[0]):
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


@BOM.route('/BOM/calculate')
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
    result.job_number = session["job_number"]
    item.results.append(result)
    db.session.add(result)

    for key in values.keys():
        material = BomResultMaterial(size=key)
        result.material.append(material)

        for beam in values[key]:
            b = BomResultBeam(length=beam['length'], waste=beam['waste'])
            material.beams.append(b)

            for thing in beam['items']:
                part = BomResultBeamPart(item_no=beam['items'][thing]['item'],
                                         length=beam['items'][thing]['length'],
                                         qty=beam['items'][thing]['qty'])
                b.parts.append(part)

        for item in missing:
            if key == item['description']:
                part_missing = BomResultMissingPart(item_no=item['item'], length=item['length'], qty=item['missing'])
                material.missing.append(part_missing)
    db.session.commit()
    return redirect(url_for('.BOM_result', result_id=result.id))


@BOM.route('/BOM/result/<result_id>', methods=['POST', 'GET'])
def BOM_result(result_id):
    result: BomResult = BomResult.query.filter_by(id=result_id).first_or_404()

    session['file'] = result.file_id
    # lengths = [6100, 7500, 12000]
    lengths = result.lengths

    lengths.sort()

    return render_template('BOM/results.html', result=result, lengths=lengths)


@BOM.route('/BOM/results/remove/<result_id>', methods=['POST', 'GET'])
def BOM_remove_result(result_id):
    result: BomResult = BomResult.query.filter_by(id=result_id).first_or_404()
    massage = f"Your about to remove result {result.id}: {result.comment}"
    if request.method == "POST":
        print(request.values)
        for item in request.values.items(multi=True):
            if item[0] == 'disagree':
                return redirect(url_for('user.dashboard'))
            print(item)
        print('deleting the item')
        result.delete()
        db.session.commit()
        return redirect(url_for('user.dashboard'))

    return render_template('user/yes_no.html', massage=massage)
