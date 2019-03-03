from flask import Blueprint

cert = Blueprint("cert", __name__)

from . import views
