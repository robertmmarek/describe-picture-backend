import os

from flask import Blueprint, json, jsonify, abort, request, current_app, url_for, current_app
from .models import Resource, ResourceSchema, FileTypes
from describe_picture import db
from describe_picture.auth.util import combine_auth, basic_auth

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')

#Upload
@resources_bp.route('/files', methods=['GET'])
@combine_auth(basic_auth)
def resource_list(*args):
    resources = Resource.query.all()
    json_rsrc = ResourceSchema().dump(resources, many=True)
    return jsonify({
        'data': {
            'resources': json_rsrc
        }
    })

@resources_bp.route('/files/<int:id>', methods=['GET'])
@combine_auth(basic_auth)
def resource_get(id):
    resource = Resource.query.filter_by(id=id).first()

    if resource is not None:
        return jsonify({
            'data': {
                'resource': ResourceSchema().dump(resource)
            }
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
@combine_auth(basic_auth)
def resource_create(*args):
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
        file_type = file.content_type
        image_file_types = ['image/png',
                            'image/jpg',
                            'image/bmp',
                            'image/gif',
                            ]

        if file_type in image_file_types:
            new_resource.resourceType = FileTypes.IMAGE
        else:
            new_resource.resourceType = FileTypes.OTHER

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

@combine_auth(basic_auth)
def file_get(request, id):
    selected = Resource.query.filter_by(id=id).first()
    if selected is not None:
        return jsonify({
            'data': {
                'resource': ResourceSchema().dump(selected)
            }
        })
    else:
        abort(404)

#required structure of request json:
# {
#    data: {
#       fields of resource data structure
#   }
# }
@combine_auth(basic_auth)
def file_update(request, id):
    selected = Resource.query.filter_by(id=id).first()
    if selected is not None:
        prev = ResourceSchema().dump(selected)
        new_object = ResourceSchema(exclude=['id']).load(request.json['data'], partial=True)

        for key, val in new_object.items():
            if key in selected.__dict__:
                setattr(selected, key, val)

        new = ResourceSchema().dump(selected)
        db.session.commit()

        return jsonify({
            'data': {
                'old_resource': prev,
                'new_resource': new
            }
        })
    else:
        abort(404)

@combine_auth(basic_auth)
def file_delete(request, id):
    selected = Resource.query.filter_by(id=id).first()
    if selected is not None:
        if os.path.isfile(selected.filePath):
            os.remove(selected.filePath)

        old = ResourceSchema().dump(selected)
        db.session.delete(selected)
        db.session.commit()

        return jsonify({
            'data': {
                'deleted': old,
            }
        })
    else:
        abort(404)


@resources_bp.route('/files/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def file_detail(id):
    response = None
    if request.method == 'GET':
        response = file_get(request, id)
    elif request.method == 'PUT':
        response = file_update(request, id)
    elif request.method == 'DELETE':
        response = file_delete(request, id)

    return response

