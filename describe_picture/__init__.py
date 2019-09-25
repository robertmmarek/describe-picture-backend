import flask
import os
import click

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

db = SQLAlchemy()

def init_database():
    from describe_picture.resources.models import Resource
    from describe_picture.auth.models import User
    db.drop_all()
    db.create_all()

def add_user(username, password):
    from describe_picture.auth.models import User
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object('describe_picture.config.default.Config')
    db.init_app(app)

    if 'SETTINGS_FILE' in os.environ:
        app.config.from_envvar('SETTINGS_FILE')

    from describe_picture.resources import resources_bp
    app.register_blueprint(resources_bp)

    from describe_picture.auth import auth_bp
    app.register_blueprint(auth_bp)


    @app.cli.command('init-database')
    def _init_database():
        init_database()

    @app.cli.command('add-user')
    @click.argument("username")
    @click.argument("password")
    def _add_user(username, password):
        add_user(username, password)

    return app


