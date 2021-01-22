import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

import click

from flask_login import LoginManager

from flask import flash, redirect, url_for

from .models import *

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

    from . import credentials

    app.config.from_mapping(
        SECRET_KEY=credentials.SECRET_KEY,
        DATABASE=os.path.join(app.instance_path, "reckoner.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Simple page saying hello
    @app.route('/hello')
    def hello():
        return 'Hello world!'

    # Set up DB initialisation command
    app.cli.add_command(init_db_command)

    # Set up SQLAlchemy and login manager
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://{}:{}@localhost:{}/{}".format(
            credentials.DB_USER,
            credentials.DB_PASSWORD,
            credentials.DB_PORT,
            credentials.DB_NAME
        )
        db.init_app(app)
        login_manager.init_app(app)
    
    # Register auth routes
    from . import auth
    app.register_blueprint(auth.bp)

    # Register reckon routes
    from . import reckons
    app.register_blueprint(reckons.bp)

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