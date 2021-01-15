from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .__init__ import db, login_manager
from .models import User

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        email = request.form["email"]
        name = request.form["name"]
        pwd1 = request.form["pwd1"]
        pwd2 = request.form['pwd2']

    return render_template('auth/register.html')



