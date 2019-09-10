import flask
import os
import click

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('describe_picture.config.default.Config')
    db.init_app(app)

    if 'SETTINGS_FILE' in os.environ:
        app.config.from_envvar('SETTINGS_FILE')


    @app.cli.command('init-database')
    def init_database():
        db.drop_all()
        db.create_all()

    return app


