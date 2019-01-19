#!/usr/bin/env python
import os

from app.auth_models import User, UserRole, Company, CompanyFeature, Asset

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app.models import MaterialClass


app = create_app(os.getenv('CLUE_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, MaterialClass=MaterialClass,
                User=User, Company=Company, Asset=Asset,
                UserRole=UserRole, CompanyFeature=CompanyFeature,
                )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade

    # migrate database to latest revision
    upgrade()


def set_up():
    db.create_all()
    UserRole.insert_roles()
    CompanyFeature.insert_features()
    MaterialClass.setup()


@manager.command
def sample_data():
    set_up()

    user1 = User(username='User1', email='user1@example.com', password='cat', confirmed=True)
    user2 = User(username='User2', email='user2@example.com', password='cat', confirmed=True)
    user3 = User(username='User3', email='user3@example.com', password='cat', confirmed=True)
    user4 = User(username='User4', email='user4@example.com', password='cat', confirmed=True)

    company1 = Company(name='ExampleCompanyOne.com')
    company2 = Company(name='ExampleCompanyTwo.com')

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)

    company1.add_user(user1)
    company1.add_user(user2)
    company1.set_company_owner(user1)
    company1.add_asset('company1_asset')
    db.session.add(company1)

    company2.add_user(user3)
    company2.add_user(user4)
    company2.set_company_owner(user3)
    company2.add_asset('company2_asset')
    db.session.add(company2)

    db.session.commit()


if __name__ == '__main__':
    manager.run()
