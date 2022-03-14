import cv2
from utils import cv_image_to_qimg
from PySide2.QtCore import QThread
from PySide2.QtCore import Signal
from PySide2.QtGui import QImage


class FaceRecognizeThread(QThread):
    img_finish_signal = Signal(QImage)

    def __init__(self):
        super(FaceRecognizeThread, self).__init__()
        self.cap = cv2.VideoCapture(0)
        self.is_close = False

    def run(self) -> None:
        while not self.is_close:
            if self.cap.isOpened():
                _, frame = self.cap.read()
                ##
                ## add some niubi algorithm
                ##
                qimg = cv_image_to_qimg(frame)
                self.img_finish_signal.emit(qimg)
