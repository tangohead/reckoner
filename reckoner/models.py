from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

from flask_login import UserMixin

import click

from .__init__ import db

class Reckon(db.Model):
    """
    A Reckon, i.e. a question posed by a user to which all users can reply.

    This may have multiple ReckonOptions, ReckonResponses, ReckonOptionResponses and one SettledReckon.
    """
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(240), nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    edit_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ended = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref=db.backref('reckons', lazy=True))

class ReckonOption(db.Model):
    """
    Describes an option for a Reckon, i.e. one of the possible
    answers
    """
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(240), nullable=False)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)

    reckon = db.relationship('Reckon', backref=db.backref('options', lazy=True))

class ReckonResponse(db.Model):
    """
    Describes a response to a Reckon, i.e. a user making an estimate 
    for each of the ReckonOptions associated with that reckon.

    This describes the response as a whole, with individual estimates stored in ReckonOptionResponse.
    """
    id = db.Column(db.Integer, primary_key=True)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    response_date = db.Column(db.DateTime, nullable=False)
    
    reckon = db.relationship('Reckon', backref=db.backref('responses', lazy=True))
    user = db.relationship('User', backref=db.backref('responses', lazy=True))
    

class ReckonOptionResponse(db.Model):
    """
    A single response to a ReckonOption, which belongs to a ReckonResponse. A user may have multiple ReckonOptionResponses per ReckonResponse.
    """
    id = db.Column(db.Integer, primary_key=True)
    reckon_response_id = db.Column(db.Integer, db.ForeignKey('reckon_response.id'), nullable=False)
    reckon_option_id = db.Column(db.Integer, db.ForeignKey('reckon_option.id'), nullable=False)
    probability = db.Column(db.Float, nullable=False)

    reckon_response = db.relationship('ReckonResponse', backref=db.backref('response_answers', lazy=True))
    reckon_option = db.relationship('ReckonOption', backref=db.backref('responses', lazy=True))

class SettledReckon(db.Model):
    """
    The settlement for a Reckon, i.e. the final result. One SettledReckon per Reckon.
    """
    id = db.Column(db.Integer, primary_key=True)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False, unique=True)
    reckon_option_id = db.Column(db.Integer, db.ForeignKey('reckon_option.id'), nullable=False)
    settled_date = db.Column(db.DateTime, nullable=False)

    reckon_settle = db.relationship('Reckon', backref=db.backref('settled', lazy=True))


class User(db.Model, UserMixin):
    """
    A simple model for a site user.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String, nullable=False)

    # Change this to creator
    reckon = db.relationship('Reckon', backref=db.backref('creator', lazy=True))
    reckon_response = db.relationship('ReckonResponse', backref=db.backref('reckon_responses', lazy=True))

class UserReckonScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reckon_id = db.Column(db.Integer, db.ForeignKey('reckon.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Float, nullable=False)

    user = db.relationship('User', backref=db.backref('scores', lazy=True))

# Define command line arg called init-db 
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables"""
    db.create_all()
    click.echo("Initialised the database.")