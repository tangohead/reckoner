import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

import click

from flask_login import LoginManager, current_user

from flask import flash, redirect, url_for, request

from flask_talisman import Talisman

from .models import *

import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
    """[summary]

    Parameters
    ----------
    test_config : Dict, optional
        Dictionary describing test configuration, by default None

    Returns
    -------
    app
        Created application object
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ["SECRET_KEY"],
    )

    csp = {
        'default-src': [
                '\'self\'',
                'cdnjs.cloudflare.com',
                'cdn.jsdelivr.net'
            ]
        }

    Talisman(app, content_security_policy=csp)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Set up DB initialisation command
    app.cli.add_command(init_db_command)

    # Set up SQLAlchemy and login manager
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
            os.environ["POSTGRES_USER"],
            os.environ["POSTGRES_PASSWORD"],
            os.environ["POSTGRES_HOSTNAME"],
            os.environ["POSTGRES_PORT"],
            os.environ["POSTGRES_DB"]
        )
        db.init_app(app)
        login_manager.init_app(app)
    
    # Register auth routes
    from . import auth
    app.register_blueprint(auth.bp)

    # Register reckon routes
    from . import reckons
    app.register_blueprint(reckons.bp)

    @app.route('/')
    def index():
        """ 
        Simple index, either putting the user to the login page or to
        view reckons
        """
        if current_user.is_authenticated:
            return redirect(url_for('reckons.view'))
        else:
            return redirect(url_for('auth.login'))


    return app



@login_manager.user_loader
def load_user(user_id):
    """Load user function as required by user loader

    Parameters
    ----------
    user_id : int
        User ID to load

    Returns
    -------
    User
        User object for matching ID, or None if the user doesn't exist
    """
    return User.query.filter_by(id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized():
    """Handler for unauthorised access (i.e. not logged in)

    Returns
    -------
    Response
        Response object describing what to do next
    """
    flash({
        "message": "You need to be logged in to do that.",
        "style": "danger"
        })
    return redirect(url_for('auth.login'))