from flask import render_template, abort, request, \
    current_app
from . import main


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


@main.route('/test')
def item_testing():
    return render_template('test.html')
