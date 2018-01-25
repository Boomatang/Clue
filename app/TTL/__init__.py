from flask import Blueprint

TTL = Blueprint('TTL', __name__)

from . import views, errors
from ..models import Permission


@TTL.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
