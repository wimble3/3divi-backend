import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import cv2

from app import redis_service

from libs.face_recognition import ALG, FaceRecognitionStatusEnum

import numpy as np

from settings import NUM_MAX_THREADS


class FaceRecognition:
    """Service for using opencv face recognition."""
    def __init__(self, file_id, video_path, threshold=80):
        """
        Sets model’s parameters.
        Args:
            file_id (str): file id
            video_path (str): path to video
            threshold (int): model’s threshold
        """
        self.face_cascade_path = cv2.data.haarcascades + ALG
        self.face_cascade = cv2.CascadeClassifier(self.face_cascade_path)
        self.faces_list = []
        self.names_list = []
        self.threshold = threshold
        self.video_path = video_path
        self.video = cv2.VideoCapture(self.video_path)
        self.frame_count = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_num = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))
        self.file_id = file_id
        self.status = FaceRecognitionStatusEnum.PROCESS
        self.persons = 0

    def process(self):
        """
        Process of recognition faces in video by frames.
        Writes id as uuid4.
        Returns:
            tuple: with list of faces and list of names
        """
        pool = ThreadPoolExecutor(max_workers=NUM_MAX_THREADS)

        # redis_data = redis_service.get(self.file_id)
        # self.status = redis_data.get("status")
        # if self.status == FaceFaceRecognitionStatusEnum.READY:
        #     return

        while True:
            if self.status == FaceRecognitionStatusEnum.RESUME:
                resume_data = redis_service.get(self.file_id)
                self.faces_list = resume_data.get("faces_list")
                self.names_list = resume_data.get("names_list")
                self.frame_num = resume_data.get("frame")
                self.persons = resume_data.get("persons")

                logging.info(
                    f"\nFile id: {self.file_id} | Resume\n"
                    f"Frame: {self.frame_num}")
                for i in range(self.frame_num + 1):
                    self.video.read()
                    self.frame_num += 1
                self.status = FaceRecognitionStatusEnum.PROCESS

            ret, frame = self.video.read()

            if not ret:
                break

            self.frame_num = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))
            pool.submit(self._process_frame, frame, self.frame_num)

        pool.shutdown(wait=True)
        self._close()

        if self.frame_num == self.frame_count:
            self.status = FaceRecognitionStatusEnum.READY

        logging.info(
            f"\n-----\n"
            f"File id: {self.file_id} CLOSED!\n"
            f"Frame: {self.frame_num}/{self.frame_count}\n"
            f"Persons: {self.persons}\n"
            f"Status: {self.status}\n"
            f"-----\n")

        redis_service.update(
            self.file_id,
            {
                "file_id": self.file_id,
                "faces_list": self.faces_list,
                "names_list": self.names_list,
                "status": str(self.status),
                "frame": f"{str(self.frame_num)}/{str(self.frame_count)}",
                "persons": str(self.persons),
                "filepath": self.video_path
            }
        )
        return self.faces_list, self.names_list

    def _process_frame(self, frame, frame_num):
        """
        Frame processing.
        Args:
            frame (cv2.typing.MatLike): cv2 frame
            frame_num (int): current frame number

        Returns:
            None:
        """
        if self.status == FaceRecognitionStatusEnum.PAUSE:
            logging.info(
                f"File id: {self.file_id} | Paused by user"
                f"Frame: {self.frame_num}")
            return

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
                label = str(uuid.uuid4())
                self.faces_list.append(cur_face.tolist())
                self.names_list.append(label)
                self.persons += 1

        redis_service.update(
            self.file_id,
            {
                "file_id": self.file_id,
                "faces_list": self.faces_list,
                "names_list": self.names_list,
                "status": str(self.status),
                "frame": f"{str(self.frame_num)}/{str(self.frame_count)}",
                "persons": str(self.persons),
                "filepath": self.video_path
            }
        )
        logging.info(
            f"\n-----\n"
            f"File id: {self.file_id}\n"
            f"Frame: {frame_num}/{self.frame_count} passed\n"
            f"Persons: {self.persons}\n"
            f"Status: {self.status}\n"
            f"-----\n")

    def _close(self):
        """
        Closes video and destroys all windows.
        Returns:
            None:
        """
        self.video.release()
        cv2.destroyAllWindows()
        logging.info(f"File: {self.file_id} | All windows destroys")
