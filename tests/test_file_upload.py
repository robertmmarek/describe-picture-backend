import pytest
import os
import io
import describe_picture
import shutil

from describe_picture import db, init_database
from describe_picture.file_upload.models import Upload, Resource

TEST_PICTURE = './test_resources/test_picture.png'

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
        db.session.add(resource_1)
        upload_1 = Upload(resource=resource_1)
        db.session.add(upload_1)
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
    rv = client.post('/file-upload/uploads',
                     data=data,
                     content_type='multipart/form-data',
                     follow_redirects=True)
    assert rv.status_code == 200
    assert os.path.isfile(upload_path)



