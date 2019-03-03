from flask import render_template, abort, request, current_app
from flask_login import login_required

from app.decorators import company_asset
from . import main


@main.route("/shutdown")
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        abort(500)
    shutdown()
    return "Shutting down..."


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/test")
def item_testing():
    return render_template("test.html")


@main.route("/test/<asset>")
@login_required
@company_asset()
def test_asset(asset):
    return render_template("main/test_token.html", asset=asset)


@main.route("/some_test")
@login_required
def test():
    return render_template("main/test.html")
