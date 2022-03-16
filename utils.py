import cv2
import numpy as np
from PyQt5.QtGui import QImage


def cv_image_to_qimg(img: np.ndarray):
    height, width, channels = img.shape
    step = 3 * width
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB, )
    qimg = QImage(img.data, width, height, step, QImage.Format_RGB888)
    return qimg
