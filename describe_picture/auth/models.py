import hashlib

from describe_picture import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1024), unique=True)
    password = db.Column(db.String(256))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            new_password = hashlib.sha256(kwargs['password'].encode()).hexdigest()
            self.password = new_password

    def check_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest() == self.password