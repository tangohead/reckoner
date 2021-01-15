import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

import click

from flask_login import LoginManager

from .models import *

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(test_config=None):
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

    #db.init_app(app)
    app.cli.add_command(init_db_command)

    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
        db.init_app(app)
        login_manager.init_app(app)
    

    # Register auth routes
    from . import auth
    app.register_blueprint(auth.bp)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()