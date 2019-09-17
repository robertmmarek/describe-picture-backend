import os

from flask import Blueprint, json, jsonify, abort, request, current_app, url_for
from .models import Upload, Resource, UploadSchema, ResourceSchema
from describe_picture import db

file_upload_bp = Blueprint('file_upload', __name__, url_prefix='/file-upload')

#Upload

@file_upload_bp.route('/uploads', methods=['GET'])
def upload_list():
    uploads = Upload.query.all()
    return jsonify({
        'data': {
            'uploads': UploadSchema().dump(uploads, many=True)
        }
    })

@file_upload_bp.route('/uploads/<int:id>', methods=['GET'])
def upload_get(id):
    upload = Upload.query.filter_by(id=id).first()

    if upload is not None:
        return jsonify({
            'data': UploadSchema().dump(upload)
        })
    else:
        abort(404)

def _create_available_filepath(filepath):
    while os.path.isfile(filepath):
        head, tail = os.path.split(filepath)
        filepath = os.path.join(head, 'dup_'+tail)
    return filepath

def _create_resource(filepath):
    new_resource = Resource()
    new_resource.filePath = filepath
    db.session.add(new_resource)
    return new_resource

def _create_upload(filepath, resource):
    new_upload = Upload()
    new_upload.resource = resource
    db.session.add(new_upload)
    return new_upload

@file_upload_bp.route('/uploads', methods=['POST'])
def upload_create():
    if 'file' not in request.files:
        abort(400)

    file = request.files['file']
    if file.filename == '':
        abort(400)

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
    filepath = _create_available_filepath(filepath)

    try:
        file.save(filepath)
        new_resource = _create_resource(filepath)
        new_upload = _create_upload(filepath, new_resource)
        db.session.commit()
    except Exception as e:
        print(e)
        new_resource = None

    if new_resource is not None:
        return jsonify({
            'data': {
                'resourceURL': new_resource.resourceURL(),
                'upload': UploadSchema().dump(new_upload)
            }
        })
    else:
        abort(500)
    
def upload_get(request):
    pass

def upload_update(request):
    pass

def upload_delete(request):
    pass

@file_upload_bp.route('/resources/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def resource_detail():
    response = None
    if request.method == 'GET':
        response = upload_get(request)
    elif request.method == 'PUT':
        response = upload_update(request)
    elif request.method == 'DELETE':
        response = upload_delete(request)

    return response

