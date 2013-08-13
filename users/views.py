from flask import Flask, jsonify, request

from common.views import APIView
from users.auth import auth_required
from users.resources import UserResource

class UserAPIView(APIView):
    @auth_required
    def get(self, user=None, **kwargs):
        return self.json_response(data=user.to_serializable_dict())


    def post(self):
        response = {}
        user_resource = UserResource(request.json)
        if user_resource.is_valid():
            try:
                user_resource.add()
                response['user'] = user_resource.to_serializable_dict()
            except Exception as error:
                print error
                pass
        return self.json_response(data=response)

    @auth_required
    def put(self, user=None, **kwargs):
        response = {}
        user_resource = UserResource(request.json, model=user)
        
        return self.json_response(data=response)

    def delete(self):
        response = {}

        response.update(self.json_result)
        return self.json_response(data=response)

app = Flask(__name__)
app.add_url_rule('/users/', view_func=UserAPIView.as_view('users'))
