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
        return url_for('file_upload.resource_detail', id=self.id)


class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))  
    resource = db.relationship('Resource', backref=db.backref('upload'))  


class ResourceSchema(Schema):
    id = fields.Integer(dump_only=True)
    filePath = fields.String()

class UploadSchema(Schema):
    id = fields.Integer(dump_only=True)
    resource = fields.Nested(ResourceSchema)


