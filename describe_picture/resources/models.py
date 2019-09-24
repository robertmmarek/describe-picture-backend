import os
import enum

from describe_picture import db
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from flask import url_for
from urllib.parse import urljoin


class FileTypes(enum.Enum):
    IMAGE = 1
    OTHER = 2

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filePath = db.Column(db.String(1024), unique=True)
    resourceType = db.Column(db.Enum(FileTypes))

    def doExists(self):
        return os.path.isfile(self.filePath)

    def resourceURL(self):
        return url_for('resources.file_detail', id=self.id)


class ResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    filePath = fields.String()
    resourceType = EnumField(FileTypes)



