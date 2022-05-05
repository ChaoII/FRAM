import cv2
import time
import platform
import numpy as np
from loguru import logger
from datetime import datetime
from utils import cv_image_to_qimg, crop_image
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, Qt
from jetsonface import FaceStatus
from recognition import FaceRecognitionThread
from jetsonface import FaceProcessHelper


class FaceRecognizeThread(QThread):
    img_finish_signal = pyqtSignal(QImage)
    rec_result_signal = pyqtSignal(dict)
    record_attend_signal = pyqtSignal(list)
    is_person_signal = pyqtSignal()
    det_signal = pyqtSignal(list)

    def __init__(self, camera_index: int = 0,
                 model_base_dir: str = "./models/",
                 font_path: str = "./fonts/simsun.ttc",
                 face_lib_dir: str = "./facelib",
                 face_lib_configure: str = "facelib.json",
                 face_rec_model="face_recognizer.csta",
                 ignore_nums: int = 10,
                 threshold: int = 0.60,
                 cap_size: tuple = (640, 480),
                 tracker_size: tuple = (640, 480),
                 use_gpu: bool = False):
        """
        face_rec core logical
        :param camera_index:camera index,egg,0,1,2,or 3 ...
        :param model_base_dir:
        :param font_path:
        :param face_lib_dir:
        :param face_lib_configure: a json configure file
        :param face_rec_model: optional [light model or heavy model]
        :param ignore_nums: using face tracker get the face id ,when face id keep steady , after ignore_nums
                            frame,face_recognition method will be running immediately
        :param threshold: face recognition confidence light_model is 0.55,full model could keep 0.62
        :param use_gpu:
        """
        super(FaceRecognizeThread, self).__init__()
        # dome some parameters initialed
        self._model_base_dir = model_base_dir
        self._font_path = font_path
        self._face_lib_dir = face_lib_dir
        self._face_lib_configure = face_lib_configure
        self._face_rec_model = face_rec_model
        self._ignore_nums = ignore_nums
        self._threshold = threshold
        self._cap_size = cap_size
        self._tracker_size = tracker_size
        self._camera_index = camera_index
        self._use_gpu = use_gpu
        # 打开记录 type：List[Dict[str,str,str]]
        self._records = []
        # 5min记录一次，如果嫌频率太低，可以降低单位
        self._record_time = 60
        # 上次记录的时间
        self._record_last_time = time.time()
        # 上一帧检测到人脸的id（reid），与真实的id不同
        self._last_id = -1
        self._frame_nums = 0
        self._fc_obj = None
        self._cap = None
        self._gap_w = 0
        self._gap_h = 0

        self._rect = None
        if platform.system() == "Windows":
            self._start_tracker = True
        else:
            self._start_tracker = False
        self._rec_thread: QThread = None

        self.result = {"code": None}
        # do some initial work
        self.init_camera()
        self.init_model()

    @staticmethod
    def gstreamer_pipeline(capture_width, capture_height, display_width, display_height, framerate, flip_method):
        return "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)" + str(capture_width) + ", height=(int)" + \
               str(capture_height) + ", format=(string)NV12, framerate=(fraction)" + str(framerate) + \
               "/1 ! nvvidconv flip-method=" + str(flip_method) + " ! video/x-raw, width=(int)" + \
               str(display_width) + ", height=(int)" + str(
            display_height) + ", format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"

    def init_camera(self):
        """
        初始化摄像头
        :return:
        """
        if platform.system() == "Windows":
            self._cap = cv2.VideoCapture(self._camera_index)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._cap_size[0])
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._cap_size[1])
        else:
            stream_str = self.gstreamer_pipeline(
                capture_width=self._cap_size[0],
                capture_height=self._cap_size[1],
                display_width=self._cap_size[0],
                display_height=self._cap_size[1],
                framerate=20,
                flip_method=6
            )

            self._cap = cv2.VideoCapture(stream_str)
            if self._cap.isOpened():
                self._cap.release()
                self._cap = cv2.VideoCapture(stream_str)

    def init_model(self):
        """
        初始化模型
        :return:
        """
        self._fc_obj = FaceProcessHelper(self._model_base_dir, self._font_path, self._tracker_size,
                                         face_rec_model=self._face_rec_model,
                                         threshold=self._threshold,
                                         use_gpu=self._use_gpu)
        self._fc_obj.create_face_feature_DB_by_json(self._face_lib_dir, self._face_lib_configure)

        self._rec_thread = FaceRecognitionThread(self._fc_obj)
        if platform.system() == "Windows":
            self._rec_thread.face_recognition_signal.connect(self.on_face_rec_result, Qt.BlockingQueuedConnection)
        else:
            self._rec_thread.face_recognition_signal.connect(self.on_face_rec_result)

    def condition_send_attend_signal(self):
        if time.time() - self._record_last_time > self._record_time:
            if len(self._records) != 0:
                self.record_attend_signal.emit(self._records)
                self._records = []
            self._record_last_time = time.time()

    @logger.catch
    def run(self) -> None:
        if not self._cap.isOpened():
            return
        _, frame = self._cap.read()
        _, self._gap_w, self._gap_h = crop_image(frame)
        while True:
            _, frame = self._cap.read()
            # frame = crop_image(frame)
            self.condition_send_attend_signal()
            # frame = np.rot90(frame)[:]
            if self._start_tracker:
                faces_result = self._fc_obj.face_tracker(frame)
                face_nums = len(faces_result)
                if face_nums > 0:
                    # 如果数量超过或者时间超过，并且self._record不为空，那么直接发送
                    data = faces_result[0]
                    face, face_id = data.pos, data.PID
                    self._rect = [face.x, face.y, face.width, face.height]
                    if self._rect is not None:
                        self.det_signal.emit(
                            [self._rect[0] - self._gap_w, self._rect[1] - self._gap_h, self._rect[2], self._rect[3]])
                    # 如果人脸变化，或者达到规定的ignore_nums帧
                    if face_id != self._last_id or self._frame_nums == self._ignore_nums:
                        self._frame_nums = 0
                        self._rec_thread.init_param(frame, face, self._threshold)
                        if not self._rec_thread.isRunning():
                            self._rec_thread.start()
                        self.rec_result_signal.emit(self.result)
                        if self.result["code"] == 1:
                            attend_info = dict()
                            attend_info["id"] = self.result["message"].face_id
                            attend_info["name"] = self.result["message"].face_info
                            attend_info["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
                            self._records.append(attend_info)
                    self._last_id = face_id
                    self._frame_nums = self._frame_nums + 1
                else:
                    self.is_person_signal.emit()
            crop_im, _, _ = crop_image(frame)

            qimg = cv_image_to_qimg(crop_im)
            self.img_finish_signal.emit(qimg)
        self._cap.release()

    def start_tracker(self):
        if not self._start_tracker:
            self._start_tracker = True
            QTimer.singleShot(10000, self.stop_tracker)

    def stop_tracker(self):
        self._start_tracker = False
        self._rect = None
        self.is_person_signal.emit()

    def on_face_rec_result(self, info: dict):
        self.result = info
