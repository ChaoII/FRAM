import cv2
import numpy as np
from PyQt5.QtGui import QImage


def cv_image_to_qimg(img: np.ndarray):
    height, width, channels = img.shape
    step = 3 * width
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB, )
    qimg = QImage(img.data, width, height, step, QImage.Format_RGB888)
    return qimg


def crop_image(img: np.ndarray, target_size: tuple = (600, 1024)):
    # 取小的边长为主
    h, w, c = img.shape
    rate_w = w / target_size[0]
    rate_h = h / target_size[1]
    w_div_h = target_size[0] / target_size[1]
    gap_w = 0
    gap_h = 0
    if rate_h < rate_w:
        h_t = h
        w_t = int(h_t * w_div_h)
        img_crop = img[:, int((w - w_t) / 2):int((w - w_t) / 2 + w_t)]
        gap_w = int((w - w_t) / 2)
    else:
        w_t = w
        h_t = w_t / w_div_h
        img_crop = img[int((h - h_t) / 2):int((h - h_t) / 2 + h_t), :]
        gap_h = int((h - h_t) / 2)
    return img_crop, gap_w, gap_h
