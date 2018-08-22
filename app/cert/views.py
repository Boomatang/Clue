from flask import render_template

from app.cert import cert


@cert.route('/', methods=['GET', 'POST'])
def index():
    return render_template('certs/index.html')


@cert.route('/upload', methods=['GET', 'POST'])
def file_upload():
    return render_template('certs/upload_complete.html')
