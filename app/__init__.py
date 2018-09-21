from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    # if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
    #     from flask_sslify import SSLify
    #     sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .cutlist import cutlist as cutlist_blueprint
    app.register_blueprint(cutlist_blueprint)

    from .tools import tools as tools_blueprint
    app.register_blueprint(tools_blueprint)

    from .librarys import library as library_blueprint
    app.register_blueprint(library_blueprint, url_prefix="/materials")

    from .BOM import BOM as BOM_blueprint
    app.register_blueprint(BOM_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix="/api/v1")

    from .project import project as project_blueprint
    app.register_blueprint(project_blueprint, url_prefix="/project")

    return app
