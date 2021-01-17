from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .__init__ import db, login_manager
from .models import User

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        print(len(request.form))
        #TODO fill in register code
        email = request.form["email"]
        name = request.form["name"]
        pwd1 = request.form["password1"]
        pwd2 = request.form['password2']

        error = None

        if not email:
            error = "Email is required."
        elif not name:
            error = "Name is required."
        elif not pwd1:
            error = "Password is required."
        elif not pwd2:
            error = "Re-entered password is required."
        elif pwd1 != pwd2:
            error = "Passwords do not match."
        elif User.query.filter_by(email=email).first() is not None:
            error = "An account with this email address already exists."

        if error is None:
            new_user = User(
                name = name,
                email = email,
                password = pwd1
            )
            db.session.add(new_user)
            db.session.commit()
        
        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == "GET":
        #TODO Fill in login code
        pass

    return render_template('auth/login.html')



