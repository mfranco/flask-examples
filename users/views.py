from flask import Flask, jsonify
from common.views import APIView


class UserAPIView(APIView):
    def get(self):
        return jsonify(self.json_result)

    def post(self):
        response = {}
        response.update(self.json_result)
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
