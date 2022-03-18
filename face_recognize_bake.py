import cv2
import time
from loguru import logger
from datetime import datetime
from utils import cv_image_to_qimg, crop_image
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from jetsonface import FaceProcessHelper


class FaceRecognizeThread(QThread):
    img_finish_signal = pyqtSignal(QImage)
    rec_result_signal = pyqtSignal(list)
    record_attend_signal = pyqtSignal(list)
    is_person_signal = pyqtSignal()

    def __init__(self, camera_index: int = 0,
                 model_base_dir: str = "./models/",
                 font_path: str = "./fonts/simsun.ttc",
                 face_lib_dir: str = "./facelib",
                 face_lib_configure: str = "facelib.json",
                 face_rec_model="face_recognizer_light.csta",
                 record_freq=20,
                 ignore_nums: int = 40,
                 threshold: int = 0.44,
                 target_size: tuple = (640, 480),
                 use_gpu: bool = False,
                 is_single=True):
        """
        face_rec core logical
        :param camera_index:camera index,egg,0,1,2,or 3 ...
        :param model_base_dir:
        :param font_path:
        :param face_lib_dir:
        :param face_lib_configure: a json configure file
        :param face_rec_model: optional [light model or heavy model]
        :param record_freq: along record_freq times, trigger a data written
        :param ignore_nums: using face tracker get the face id ,when face id keep steady , after ignore_nums
                            frame,face_recognition method will be running immediately
        :param threshold: face recognition confidence light_model is 0.55,full model could keep 0.62
        :param target_size: show frame size,caution:the size need be supported by your camera
        :param use_gpu:
        :param is_single: now, it is supported single face,because multiply faces could degrade performance
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
        self._target_size = target_size
        self._camera_index = camera_index
        self._use_gpu = use_gpu
        self._is_single = is_single
        # 当打卡记录达到record_freq时，进行一次信息存储
        self._record_freq = record_freq
        # 打开记录 type：List[Dict[str,str,str]]
        self._records = []
        # 当前已经记录的打开数量
        self._record_nums = 0
        # 5min记录一次，如果嫌频率太低，可以降低单位ms
        self._record_time = 300000
        # 上次记录的时间
        self._record_last_time = time.time()

        # 上一帧检测到人脸的id（reid），与真实的id不同
        self._last_id = -1
        self._frame_nums = 0
        self._fc_obj = None
        self._cap = None
        self._is_stop = False
        self._start_tracker = True

        # do some initial work
        self.init_camera()
        self.init_model()

    def init_camera(self):
        """
        初始化摄像头
        :return:
        """
        self._cap = cv2.VideoCapture(self._camera_index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._target_size[0])
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._target_size[1])

    def init_model(self):
        """
        初始化模型
        :return:
        """
        self._fc_obj = FaceProcessHelper(self._model_base_dir, self._font_path, self._target_size,
                                         face_rec_model=self._face_rec_model,
                                         threshold=self._threshold,
                                         use_gpu=self._use_gpu)
        self._fc_obj.create_face_feature_DB_by_json(self._face_lib_dir, self._face_lib_configure)

    @logger.catch
    def run(self) -> None:
        while True:
            if self._is_stop:
                break
            if self._cap.isOpened():
                _, frame = self._cap.read()
                if not self._start_tracker:
                    qimg = cv_image_to_qimg(crop_image(frame))
                    self.img_finish_signal.emit(qimg)
                    continue
                faces_result = self._fc_obj.face_tracker(frame)
                face_nums = len(faces_result)
                if face_nums <= 0:
                    self.is_person_signal.emit()

                if self._is_single and face_nums > 1:
                    logger.warning("当前人数" + "face_nums" + ",目前仅支持单人脸解锁。。。。。。")
                labels = []
                # 如果数量超过或者时间超过，并且self._record不为空，那么直接发送
                if self._record_nums == self._record_freq or time.time() - self._record_last_time > self._record_time:
                    if len(self._records) != 0:
                        self.record_attend_signal.emit(self._records)
                        self._record_nums = 0
                        self._records = []
                        self._record_last_time = time.time()

                for i, data in enumerate(faces_result):
                    face, face_id = data.pos, data.PID
                    # 如果人脸变化，或者达到规定的ignore_nums帧
                    if face_id != self._last_id or self._frame_nums == self._ignore_nums:
                        self._frame_nums = 0
                        # ----关键点检测----
                        points = self._fc_obj.face_marker(frame, [face.x, face.y, face.width, face.height])
                        point_py = [[point.x, point.y] for point in points]
                        ret = self._fc_obj.face_recognition(frame, point_py)
                        # -------------信号发送逻辑请在这里编写------------------
                        # 发送io信号-----该处作为打卡可能不需要了

                        if ret.confidence < self._threshold:
                            color = [0, 0, 255]
                            self.rec_result_signal.emit(["未知", datetime.now().time().strftime("%H:%M:%S"), False])
                        else:
                            self.rec_result_signal.emit(
                                [ret.face_info, datetime.now().time().strftime("%H:%M:%S"), True])
                            color = [0, 255, 0]
                            attend_info = dict()
                            attend_info["id"] = ret.face_id
                            attend_info["name"] = ret.face_info
                            attend_info["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")
                            logger.info(f"打卡成功,打卡人:【{ret.face_info}】")
                            self._records.append(attend_info)
                            self._record_nums += 1
                        print(ret.confidence)
                        label = ret.face_info + str(ret.confidence)[:7]
                    labels.append(label)
                    if len(labels) == 0:
                        continue
                    self._fc_obj.draw_img(color, labels, [face.x, face.y],
                                          [face.x + face.width, face.y + face.height], frame)
                    self._last_id = face_id
                self._frame_nums = self._frame_nums + 1
                # ----------------------------------------------
                qimg = cv_image_to_qimg(crop_image(frame))
                self.img_finish_signal.emit(qimg)
        self._cap.release()

    def stop(self):
        logger.info("stop thread")
        self._is_stop = True

    def start_tracker(self):
        if not self._start_tracker:
            self._start_tracker = True
            QTimer.singleShot(10000, self.stop_tracker)

    def stop_tracker(self):
        self._start_tracker = False
        self.is_person_signal.emit()