import uuid
from concurrent.futures import ThreadPoolExecutor

import cv2

from libs.face_recognition import ALG

import numpy as np

from settings import NUM_MAX_THREADS


class FaceRecognition:
    """Service for using face recognition."""
    def __init__(self, video_path, threshold=80):
        """
        Sets model's parameters.
        Args:
            video_path (str): path to video
            threshold (int): model's threshold
        """
        self.face_cascade_path = cv2.data.haarcascades + ALG
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        self.faces_list = []
        self.names_list = []
        self.threshold = 80
        self.video = cv2.VideoCapture(video_path)

    def process(self):
        """
        Process of recognition faces in video by frames.
        Writes id as uuid4.
        Returns:
            tuple: with list of faces and list of names
        """
        pool = ThreadPoolExecutor(max_workers=NUM_MAX_THREADS)

        while True:
            ret, frame = self.video.read()
            if not ret:
                break

            pool.submit(self._process_frame, frame)

        pool.shutdown()
        self._close()
        return self.faces_list, self.names_list

    def _process_frame(self, frame):
        """
        Frame processing.
        Args:
            frame (cv2.typing.MatLike): cv2 frame

        Returns:
            None:
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            cur_face = gray[y:y + h, x:x + w]
            rec = cv2.face.LBPHFaceRecognizer.create()
            rec.train([cur_face], np.array(0))
            f = True
            for face in self.faces_list:
                _, confidence = rec.predict(face)
                if confidence < self.threshold:
                    f = False

            if f:
                label = uuid.uuid4()
                self.faces_list.append(cur_face)
                self.names_list.append(label)

    def _close(self):
        """
        Closes video and destroys all windows.
        Returns:
            None:
        """
        self.video.release()
        cv2.destroyAllWindows()
