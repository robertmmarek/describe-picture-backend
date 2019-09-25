import pytest
import os
import io
import describe_picture
import shutil
import json

from base64 import b64encode
from describe_picture import db, init_database
from describe_picture.resources.models import Resource, FileTypes
from describe_picture.auth.models import User

TEST_PICTURE = './test_resources/test_picture.png'

def _add_auth_header(headers):
    new_headers = dict(headers)
    user_string = b64encode(b"test:test").decode('utf-8')
    new_headers["Authorization"] = "Basic {}".format(user_string)
    return new_headers

def _clean_temp_upload(app):
    if os.path.isdir(app.config['UPLOAD_FOLDER']):
        shutil.rmtree(app.config['UPLOAD_FOLDER'], ignore_errors=True)

def _create_upload_folder(app):
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

def _initial_database(app):
    with app.app_context():
        init_database()
        resource_1 = Resource()
        resource_1.filePath = 'test_path.jpg'
        resource_1.resourceType = FileTypes.IMAGE
        db.session.add(resource_1)

        resource_2 = Resource()
        resource_2.filePath = 'test_path.something'
        resource_2.resourceType = FileTypes.OTHER
        db.session.add(resource_2)

        test_user = User(username="test", password="test")
        db.session.add(test_user)

        db.session.commit()

        
    
@pytest.fixture
def simple_client():
    os.environ['SETTINGS_FILE'] = "./config/tests.cfg"
    app = describe_picture.create_app()
    _initial_database(app)
    _create_upload_folder(app)
    yield {'client': app.test_client(),
           'upload_dir': app.config['UPLOAD_FOLDER']}
    _clean_temp_upload(app)


def test_file_upload(simple_client):
    client = simple_client['client']
    upload_path = os.path.join(simple_client['upload_dir'], 'test_picture.png')

    data = {}
    data['file'] = (io.BytesIO(b'abcdefg'),
                    'test_picture.png')
    rv = client.post('/resources/files',
                     data=data,
                     headers=_add_auth_header({}),
                     content_type='multipart/form-data',
                     follow_redirects=True)
    assert rv.status_code == 200
    assert os.path.isfile(upload_path)

def test_file_list(simple_client):
    client = simple_client['client']
    rv = client.get('/resources/files', headers=_add_auth_header({}))
    assert rv.status_code == 200
    assert len(rv.json['data']['resources']) == 2
   
def test_file_get_detail(simple_client):
    client = simple_client['client']
    rv = client.get('/resources/files/1', headers=_add_auth_header({}))
    assert rv.status_code == 200
    assert rv.json['data']['resource']['id'] == 1

def test_file_delete(simple_client):
    client = simple_client['client']
    rv = client.delete('/resources/files/1', headers=_add_auth_header({}))
    assert rv.status_code == 200
    assert rv.json['data']['deleted']['id'] == 1

def test_file_update(simple_client):
    client = simple_client['client']
    data = {'data': {
        'filePath': 'modified_path.jpg',
        'resourceType': 'IMAGE'
    }}
    print(_add_auth_header({}))
    rv = client.put('/resources/files/1', 
                    data = json.dumps(data),
                    headers=_add_auth_header({}),
                    content_type='application/json')
    assert rv.status_code == 200
    assert rv.json['data']['new_resource']['filePath'] \
           != rv.json['data']['old_resource']['filePath']
    assert rv.json['data']['new_resource']['filePath'] == 'modified_path.jpg'






