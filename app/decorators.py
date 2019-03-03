from functools import wraps
from flask import abort
from flask_login import current_user


def company_asset():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.company_asset(*args, **kwargs):
                abort(404)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def feature_required(feature):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.company.can(feature):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(None)(f)
