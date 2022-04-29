from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from datetime import datetime
from jetsonface import FaceStatus
from loguru import logger


class FaceRecognitionThread(QThread):
    face_recognition_signal = pyqtSignal(dict)

    def __init__(self, face_obj):
        super(FaceRecognitionThread, self).__init__()
        self._face_obj = face_obj
        self._frame = None
        self._face = None
        self._threshold = 6.0

    def init_param(self, frame, face, threshold):
        self._frame = frame
        self._face = face
        self._threshold = threshold

    def run(self):
        box = [self._face.x, self._face.y, self._face.width, self._face.height]
        points = self._face_obj.face_marker(self._frame, box)
        point_py = [[point.x, point.y] for point in points]
        # 人脸活体检测
        status = self._face_obj.face_anti_spoofing(self._frame, box, point_py)
        # status = 0
        if status != FaceStatus.REAL:
            logger.critical("可能的攻击人脸")
            self.face_recognition_signal.emit(
                {'code': -1, "time": datetime.now().time().strftime("%H:%M:%S"), "message": "攻击人脸"})

        else:
            # 人脸识别
            ret = self._face_obj.face_recognition(self._frame, point_py)
            if ret.confidence < self._threshold:
                self.face_recognition_signal.emit(
                    {"code": 0, "time": datetime.now().time().strftime("%H:%M:%S"), "message": "未知人脸"})
                logger.warning(f"未知人脸,confidence:{ret.confidence:.2f}")
            else:
                logger.info(ret.confidence)
                self.face_recognition_signal.emit(
                    {"code": 1, "time": datetime.now().time().strftime("%H:%M:%S"), "message": ret})
