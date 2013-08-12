from flask import Flask, jsonify, request

from common.views import APIView
from users.models import User


class UserValidator():
     def __init__(self, data):
         self._is_valid = True

     def is_valid(self):
         return self._is_valid

class UserAPIView(APIView):
    def get(self):
        return jsonify(self.json_result)

    def post(self):
        response = {}
        validator = UserValidator(request.json)
        if validator.is_valid():
            try:
                user = User(**request.json)
                user.add()
                response['user'] = user.to_serializable_dict()
            except Exception as error:
                print error
                pass
        return jsonify(response)

    def put(self):
        response = {}
        response.update(self.json_result)
        return jsonify(response)

    def delete(self):
        response = {}
        response.update(self.json_result)
        return jsonify(response)

app = Flask(__name__)
app.add_url_rule('/users/', view_func=UserAPIView.as_view('users'))
