class JsonSerializer(object):
    """
    Very simple model serializer
    """
    def to_serializable_dict(self):
        serialized_dict = {}
        for key in self.__table__.c.keys():
            serialized_dict[key] = getattr(self, key)
        return serialized_dict
