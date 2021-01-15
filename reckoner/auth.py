from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .__init__ import db, login_manager
from .models import User

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == "POST":
        pass

    return render_template('auth/register.html')



