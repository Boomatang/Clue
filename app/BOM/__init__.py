from flask import Blueprint

BOM = Blueprint('BOM', __name__)

from . import views
