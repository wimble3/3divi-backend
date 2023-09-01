from sqlalchemy import UUID

from app import db

from libs.face_recognition import FaceRecognitionStatusEnum

from sqlalchemy.dialects.postgresql import JSONB

from settings import DB_TBL_PRFX


class Video(db.Model):
    __tablename__ = f"{DB_TBL_PRFX}videos"

    id = db.Column(UUID(as_uuid=True), primary_key=True)
    data = db.Column(JSONB)
    status = db.Column(db.Enum(FaceRecognitionStatusEnum))
    frame = db.Column(db.Integer)
    persons = db.Column(db.Integer)
    filepath = db.Column(db.String)
