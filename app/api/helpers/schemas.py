from app import ma


class BinaryResponseSchema(ma.Schema):
    """
    Schema for forming a server response to a binary request.
    Attributes:
        - result: bool, the result of the operation
        - message: str, message from the server
    """
    message = ma.Str(example="Server response message")
    result = ma.Bool(example=True)
