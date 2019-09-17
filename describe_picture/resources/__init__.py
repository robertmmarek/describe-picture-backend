import os

from flask import Blueprint, json, jsonify, abort, request, current_app, url_for
from .models import Resource, ResourceSchema
from describe_picture import db

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

#Upload

@resources_bp.route('/files', methods=['GET'])
def upload_list():
    uploads = Upload.query.all()
    return jsonify({
        'data': {
            'uploads': UploadSchema().dump(uploads, many=True)
        }
    })

@resources_bp.route('/files/<int:id>', methods=['GET'])
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

@resources_bp.route('/files', methods=['POST'])
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
        db.session.commit()
    except Exception as e:
        print(e)
        new_resource = None

    if new_resource is not None:
        return jsonify({
            'data': {
                'resourceURL': new_resource.resourceURL(),
                'resource': ResourceSchema().dump(new_resource)
            }
        })
    else:
        abort(500)
    
def file_get(request):
    pass

def file_update(request):
    pass

def file_delete(request):
    pass

@resources_bp.route('/files/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def file_detail():
    response = None
    if request.method == 'GET':
        response = upload_get(request)
    elif request.method == 'PUT':
        response = upload_update(request)
    elif request.method == 'DELETE':
        response = upload_delete(request)

    return response

