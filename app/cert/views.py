import os
import uuid

from flask import render_template, url_for, redirect, request, session, flash, send_file
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename

from app import db
from app.cert import cert
from app.cert.forms import CertForm
from app.models import Certs
from app.smart import cert_editing
from app.utils import file_ext_checker
from datetime import datetime
from manage import app


@cert.route('/', methods=['GET', 'POST'])
def index():
    form = CertForm(CombinedMultiDict((request.files, request.form)))

    if form.validate_on_submit():

        f = form.cert_folder.data
        filename = secure_filename(f.filename)

        if not file_ext_checker(str(filename), '.zip'):
            flash('File type was not a zip file type.', 'Error')
            return redirect(url_for('cert.index'))

        filename = uuid.uuid4()

        name = os.path.join(os.environ.get('CLUE_UPLOADS', '/home/boomatang/Public'),
                            'cert_uploads', str(filename) + '.zip')

        f.save(name)

        db_entry = Certs(date=datetime.now())
        db_entry.upload_file = name

        db.session.add(db_entry)
        db.session.commit()
        print(f"The db_entry ID = {db_entry.id}")
        session["cert_id"] = db_entry.id
        return redirect(url_for("cert.file_upload"))

    history = Certs.query.order_by(Certs.date.desc())[:]

    return render_template('certs/index.html', form=form, history=history)


@cert.route('/upload', methods=['GET', 'POST'])
def file_upload():
    cert_id = session["cert_id"]
    cert_editing(cert_id, app)

    return render_template('certs/upload_complete.html', cert_id=cert_id)


@cert.route('/download/<cert>')
def download(cert):

    db_entry = Certs.query.filter_by(id=cert).first_or_404()

    return send_file(db_entry.download_file, as_attachment=True)
