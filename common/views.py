from flask import abort
from flask.views import MethodView

class APIView(MethodView):
    """ Generic API, all the API views will inherit for this base class
        every dispatch method will return an invalid request message, every
        child class must implements this methods properly
        More info about flask class based views here
        http://flask.pocoo.org/docs/views/#method-based-dispatching.
    """

    @property
    def json_result(self):
        ENDPOINT = '/mymusic/api/v1.0/'
        return {'ENDPOINT': ENDPOINT}

    def get(self):
        abort(400)

    def post(self):
        abort(400)

    def put(self):
        abort(400)

    def delete(self):
        abort(400)
