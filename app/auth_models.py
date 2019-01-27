import uuid
from flask import flash, current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, AnonymousUserMixin

from app.email import send_email
from . import db, login_manager


def uuid_key():
    return uuid.uuid4().hex


class Feature:
    FEATURE1 = 0x01
    FEATURE2 = 0x02
    FEATURE3 = 0x04
    FEATURE4 = 0x08
    FEATURE5 = 0x10
    FEATURE6 = 0x20
    FEATURE7 = 0x40
    FEATURE8 = 0x80


class CompanyFeature(db.Model):
    __tablename__ = 'company_features'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    feature = db.Column(db.Integer)
    companies = db.relationship('Company', backref='feature', lazy='dynamic')

    @staticmethod
    def insert_features():
        features = {
            'Level_1': (Feature.FEATURE1 |
                        Feature.FEATURE2 |
                        Feature.FEATURE3, True),
            'Level_2': (Feature.FEATURE1 |
                        Feature.FEATURE2 |
                        Feature.FEATURE3 |
                        Feature.FEATURE4, False),
            'Super': (0xff, False)
        }
        for r in features:
            feature = CompanyFeature.query.filter_by(name=r).first()
            if feature is None:
                feature = CompanyFeature(name=r)
            feature.feature = features[r][0]
            feature.default = features[r][1]
            db.session.add(feature)
        db.session.commit()

    def __repr__(self):
        return f'<Role {self.name}>'


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = UserRole.query.filter_by(name=r).first()
            if role is None:
                role = UserRole(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = db.relationship("Company", back_populates="users", lazy=False)
    admin = db.relationship("Company", back_populates="owner")
    role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
    asset = db.Column(db.String(64), index=True, default=uuid_key)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    @property
    def is_admin(self):
        if self.email == self.company.owner.email:
            return True
        else:
            return False

    def generate_invite_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'invite': self.id})

    @staticmethod
    def confirm_invited_user(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            s.loads(token)
        except ValueError:
            return False
        return True

    @staticmethod
    def load_invited_user(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except ValueError:
            return False

        user_id = data.get('invite')

        user = User.load_user(user_id)

        return user

    @staticmethod
    def load_user(user_id):
        user = User.query.filter_by(id=user_id).first_or_404()

        return user

    def add_asset(self, asset):
        entry = Asset()
        db.session.add(entry)
        entry.asset = asset
        entry.company = self.company
        db.session.commit()

    def company_asset(self, asset):

        db_asset = Asset.query.filter_by(asset=asset).first_or_404()

        if self.company.id == db_asset.company.id:
            return True
        else:
            return False

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def __repr__(self):
        return f'<email : {self.email}>'


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    users = db.relationship("User", back_populates="company")
    owner = db.relationship("User", uselist=False, back_populates="admin")
    assets = db.relationship("Asset", back_populates="company")
    feature_id = db.Column(db.Integer, db.ForeignKey('company_features.id'))
    asset = db.Column(db.String(64), index=True, default=uuid_key)

    def add_user(self, user):
        self.users.append(user)

    def set_company_owner(self, user):
        self.owner = user

    def company_materials_setup(self):
        from app.models import MaterialClass

        MaterialClass.setup(self.id)

    @staticmethod
    def load_company_by_name(name):
        return Company.query.filter_by(name=name).first()

    def add_asset(self, asset):
        entry = Asset()
        entry.asset = asset
        entry.company = self

    def can(self, feature):
        return self.feature is not None and \
               (self.feature.permissions & feature) == feature


class Asset(db.Model):
    __tablename__ = 'asset'
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(64), index=True, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    company = db.relationship("Company", back_populates="assets", lazy=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def email_in_system(email):
    user = User.query.filter_by(email=email).first()

    if user:
        return True
    else:
        return False


def invite_user(email):
    flash(f'Invite email has been set to {email}')

    user = User()
    user.email = email

    db.session.add(user)
    current_user.company.add_user(user)
    db.session.commit()

    token = user.generate_invite_token()
    send_email(user.email, 'You have been invited',
               'auth/email/invite', user=user, token=token)
