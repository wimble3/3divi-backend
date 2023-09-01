from enum import Enum


ALG = "haarcascade_frontalface_default.xml"


class FaceRecognitionStatusEnum(Enum):
    PROCESS = "process"
    PAUSE = "pause"
    READY = "ready"
    RESUME = "resume"
