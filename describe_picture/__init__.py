import flask
import os

from flask import Flask

def create_app(config_filename='/config/default.py'):
    app = Flask(__name__)
    app.config.from_object('describe_picture.config.default')

    if 'SETTINGS_FILE' in os.environ:
        app.config.from_envvar('SETTINGS_FILE')

    return app