from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from flask_login import login_user, login_required, logout_user

from .__init__ import db, login_manager
from .models import User

from urllib.parse import urlparse, urljoin

bp = Blueprint('auth', __name__, url_prefix="/auth")

# From https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work
def is_safe_url(target):
    """Checks if a redirect URL is safe, particularly after login

    Parameters
    ----------
    target : 
        Target URL to check

    Returns
    -------
    Boolean
        True if safe, else False
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Route to handle registering users

    Returns
    -------
    Response
        A response, either the registration page or a redirect to login
    """
    if request.method == "POST":
        print(len(request.form))
        
        email = request.form["email"]
        name = request.form["name"]
        pwd1 = request.form["password1"]
        pwd2 = request.form['password2']

        error = None

        # Basic sanity checks
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
        elif len(pwd1) < 8:
            error = "Password is too short. Must be 8 characters or more."
        elif User.query.filter_by(email=email).first() is not None:
            error = "An account with this email address already exists."

        # Now create the user and commit to the database
        if error is None:
            new_user = User(
                name = name,
                email = email,
                password = generate_password_hash(pwd1)
            )
            db.session.add(new_user)
            db.session.commit()

            flash({
                "message": "Account created successfully. Please log in.",
                "style": "info"
                })
            return redirect(url_for("auth.login"))
        
        # If something has failed, display the error
        flash({"message": error, "style": "danger"})

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Route for logging users in 

    Returns
    -------
    Response
        Either a redirect to the user account page or a failed log in, returning to the log in page.
    """

    if request.method == "POST":
        email = request.form["email"]
        pwd = request.form["password"]

        # Basic sanity checks
        if not email:
            error = "Please enter an email address."
        elif not pwd:
            error = "Please enter a password."
        elif User.query.filter_by(email=email).first() is None:
            error = "Incorrect username or password."
        else:
            # Now get the user to check the password
            user = User.query.filter_by(email=email).first()
            
            # Check the password is correct
            if not check_password_hash(user.password, pwd):
                error = "Incorrect username or password."
            else:
                # Let LoginManager handle the log in
                login_user(user)

                flash("Logged in successfully!")

                next = request.args.get('next')
                if not is_safe_url(next):
                    flask.abort(400)
                
                return redirect(next or url_for('auth.account'))
                
        flash({
            "message": error,
            "style": "danger"
            })
                
    return render_template('auth/login.html')

@bp.route('/account')
@login_required
def account():
    """Route for a simple account page

    Returns
    -------
        Rendered Jinja template
    """
    return render_template('auth/account.html')

@bp.route('/logout')
@login_required
def logout():
    """Route for logout, returning user to login page

    Returns
    -------
    Response
        Response redirecting user to login page
    """
    logout_user()
    flash({"message": "Logout successful.", "style": "info"})
    return redirect(url_for('auth.login'))


