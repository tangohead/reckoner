from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

from flask_login import UserMixin

import click
# app = Flask(__name__)

#db = SQLAlchemy()
from .__init__ import db

class Reckon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(240), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    edit_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ended = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref=db.backref('reckons', lazy=True))

class ReckonAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)
    reckon_option_id = db.Column(db.Integer, db.ForeignKey('reckon_option.id'), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)

    reckon = db.relationship('Reckon', backref=db.backref('answer', lazy=True))
    

class ReckonOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(240), nullable=False)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)

    reckon = db.relationship('Reckon', backref=db.backref('options', lazy=True))

class ReckonResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reckon_option_id = db.Column(db.Integer, db.ForeignKey('reckon_option.id'), nullable=False)
    probability = db.Column(db.Float, nullable=False)
    response_date = db.Column(db.DateTime, nullable=False)
    
    reckon = db.relationship('Reckon', backref=db.backref('responses', lazy=True))
    user = db.relationship('User', backref=db.backref('responses', lazy=True))
    reckon_option = db.relationship('ReckonOption', backref=db.backref('responses', lazy=True))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)

    reckon = db.relationship('Reckon', backref=db.backref('reckons_made', lazy=True))
    reckon_response = db.relationship('ReckonResponse', backref=db.backref('reckon_responses', lazy=True))



# Define command line arg called init-db 
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables"""
    db.create_all()
    click.echo("Initialised the database.")