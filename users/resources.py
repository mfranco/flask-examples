from common.resources import BaseResource
from users.models import User

class UserResource(BaseResource):
    __model__ = User

    def __init__(self, data, **kwargs):
        super(UserResource, self).__init__(data, **kwargs)
        self._is_valid = True
