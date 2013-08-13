from functools import wraps
from flask import jsonify, request

from users.models import User


def return_error():
    return jsonify({'error': 'you do not have access'})

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Check if api_access_token and api_username
           headers are setted and check credentials
        """
        if 'api_access_token' not in request.headers or 'api_username' not in request.headers:
            return return_error()
        else:
            token = request.headers['api_access_token']
            username = request.headers['api_username']
            try:
                user = User.authenticate(username, token)
                kwargs['user'] = user 
                return f(*args, **kwargs)
            except Exception as error:
                #import ipdb; ipdb.set_trace()
                return return_error()
    return decorated_function
