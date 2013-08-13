class BaseResource(object):
    """
    Validation logic for user json strcture must be implemented here
    """
    __model__ = None

    def __init__(self, dict_data, model=None, **kwargs):
        self._is_valid = False
        self._dict_data = dict_data
        if model:
            self.__model__ = model

    def is_valid(self):
        return self._is_valid

    def to_serializable_dict(self):
        try:
            return self.__model__.to_serializable_dict()
        except:
            return {}

    def add(self):
        self.__model__ = self.__model__(**self._dict_data)
        self.__model__.add()

    def update(self):
        for key, value in self._dict_data.items():
            if 'id' != key:
                setattr(self.__model__, key, value)
        self.__model__.update()
