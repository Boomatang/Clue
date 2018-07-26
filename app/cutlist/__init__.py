from flask import Blueprint

cutlist = Blueprint('cutlist', __name__)

from . import views
