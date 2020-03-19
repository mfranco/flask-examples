class NotFoundError(Exception):
    """
    This exception should be thrown when a query by primary key returns nothing
    """


class InvalidQueryError(Exception):
    """
    This exception should be thrown if an invalid query is attempted
    """
