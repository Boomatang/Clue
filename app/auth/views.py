from flask_login import current_user, login_user, login_required, logout_user

from app import db
from app.auth import auth
from flask import render_template, url_for, redirect, request, flash

from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    PasswordResetRequestForm,
    PasswordResetForm,
    ChangeEmailForm,
    InviteUserForm,
    InvitedUserForm,
)
from app.auth_models import User, Company, email_in_system, invite_user
from app.email import send_email


@auth.before_app_request
def before_request():
    if (
        current_user.is_authenticated
        and not current_user.confirmed
        and request.endpoint[:5] != "auth."
    ):
        return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect("auth.index")
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        form.email.errors.append("Invalid E-mail or Password")
        form.password.errors.append("Invalid E-mail or Password")
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data

        user = User(email=email, username=username)
        user.password = form.password.data

        company = Company()
        company.name = form.company.data

        db.session.add(user)
        db.session.add(company)

        company.set_company_owner(user)
        company.add_user(user)

        db.session.commit()
        company.company_materials_setup()

        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm Your Account",
            "auth/email/confirm",
            user=user,
            token=token,
        )
        flash("A confirmation email has been sent to you by email.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirm Your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash("Your password has been updated.")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/email/reset_password",
                user=user,
                token=token,
                next=request.args.get("next"),
            )
        flash(
            "An email with instructions to reset your password has been " "sent to you."
        )
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password.data):
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                "Confirm your email address",
                "auth/email/change_email",
                user=current_user,
                token=token,
            )
            flash(
                "An email with instructions to confirm your new email "
                "address has been sent to you."
            )
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.")
    return render_template("auth/change_email.html", form=form)


@auth.route("/change-email/<token>")
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("Your email address has been updated.")
    else:
        flash("Invalid request.")
    return redirect(url_for("main.index"))


#  Pages related to the company


@auth.route("/company_settings", methods=["GET", "POST"])
@login_required
def company_settings():

    if current_user.is_admin is not True:
        flash("Access Denied")
        return redirect(url_for("main.index"))

    form = InviteUserForm()
    users = current_user.company.users[:]

    if form.validate_on_submit():
        email = form.email.data

        if email_in_system(email):
            form.email.errors.append("Sorry that email is currently been used")
            return render_template("auth/company_settings.html", users=users, form=form)

        invite_user(email)
        return redirect(url_for("auth.company_settings"))
    return render_template("auth/company_settings.html", users=users, form=form)


@auth.route("/invited/<token>", methods=["GET", "POST"])
def invited(token):
    form = InvitedUserForm()

    if User.confirm_invited_user(token):
        user = User.load_invited_user(token)
        login_user(user)

        if user.confirmed:
            flash("Account already activated!")
            return redirect(url_for("main.index"))

        if form.validate_on_submit():
            user.password = form.password.data
            user.username = form.username.data
            user.confirmed = True

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("main.index"))

    else:
        flash("Unable to confirm your invite")
        return redirect(url_for("main.index"))

    return render_template("auth/invited.html", form=form)


@auth.route("/remove_user/<user_id>")
@login_required
def remove_user(user_id):
    user = User.load_user(user_id)
    if user.is_admin:
        flash("You cannot remove admin accounts. Pleas contact support for help.")
        return redirect(url_for("auth.company_settings"))
    name = user.username
    db.session.delete(user)
    flash(f"{name} been removed from the company")
    return redirect(url_for("auth.company_settings"))


@auth.route("/reset_user_password/<user_id>")
@login_required
def reset_user_password(user_id):
    user = User.load_user(user_id)
    print(user)
    name = user.username
    token = user.generate_reset_token()
    send_email(
        user.email,
        "Reset Your Password",
        "auth/email/reset_password",
        user=user,
        token=token,
        next=request.args.get("next"),
    )

    flash(
        f"An email with instructions to reset {name}'s password has been sent to {name}."
    )
    return redirect(url_for("auth.company_settings"))
