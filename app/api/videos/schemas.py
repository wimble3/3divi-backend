from app import ma


class VideoSchema(ma.Schema):
    """Schema for representation Video model."""
    id = ma.UUID(dump_only=True)
    # data = ma.Dict()
    status = ma.Str()
    frame = ma.Integer()
    persons = ma.Integer()
    filepath = ma.Str()


class VideoResponseSchema(ma.Schema):
    """Schema for response which contains VideoSchema."""
    message = ma.Str(example="Server response message")
    result = ma.Bool(example=True)
    video = ma.Nested(VideoSchema)
