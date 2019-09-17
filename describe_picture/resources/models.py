from describe_picture import db
from marshmallow import Schema, fields
from flask import url_for
from urllib.parse import urljoin
import os


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filePath = db.Column(db.String(1024), unique=True)

    def doExists(self):
        return os.path.isfile(self.filePath)

    def resourceURL(self):
        return url_for('resources.file_detail', id=self.id)


class ResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    filePath = fields.String()



