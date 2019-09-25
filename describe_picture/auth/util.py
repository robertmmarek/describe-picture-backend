from describe_picture.auth.models import User
from functools import wraps
from flask import request, abort, current_app


def basic_auth(req):
    auth = req.authorization
    if auth is not None:
        user = User.query.filter_by(username=auth.username).first()
    else:
        abort(401)
    
    if user is not None:
        return user.check_password(auth.password)
    else:
        return False

def combine_auth(*auths):
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            combined = [True]
            with current_app.app_context():
                for el in auths:
                    if type(el) == list:
                        combined.append(any([sub(request) for sub in el]))
                    else:
                        combined.append(el(request))

            if all(combined):
                return f(*args, **kwargs)
            else:
                abort(401)
        
        return decorated_func
    return decorator

