import platform
from datetime import date
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtWidgets
# from GPIO_input import DetectorPersonThread
from ui.ui_main_widget import Ui_Form
from face_recognize import FaceRecognizeThread
from attend_record import AttendRecordThread
from coverwidget import CoverWidget
from loguru import logger


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 实例化UI对象
        self.ui.setupUi(self)  # 初始化
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.cover = CoverWidget()
        self.cover.show()
        self.cover.ui.widget.setVisible(False)
        self.face_rec = FaceRecognizeThread(use_gpu=platform.system() != "Windows")
        # self.people_rec = DetectorPersonThread()
        # self.people_rec.people_entry_signal.connect(self.on_detective_people, Qt.DirectConnection)
        # self.people_rec.start()
        # 实时画面传输信号
        self.face_rec.img_finish_signal.connect(self.show_img, Qt.ConnectionType.DirectConnection)
        # 打卡信息保存信号
        self.face_rec.record_attend_signal.connect(self.delt, Qt.DirectConnection)
        # 识别结果信号-触发显示信息
        self.face_rec.rec_result_signal.connect(self.change_sign_info, Qt.DirectConnection)
        # 判断是否有人脸的信号--触发控件 visible
        self.face_rec.is_person_signal.connect(self.set_cover_visible, Qt.DirectConnection)
        QTimer.singleShot(50, self.face_rec.start)

    @pyqtSlot(QImage)
    def show_img(self, qimg):
        scaled_img = qimg.scaled(self.ui.image_label.size(),
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
        self.ui.image_label.setPixmap(QPixmap.fromImage(scaled_img))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.face_rec.isRunning():
            self.face_rec.stop()
            self.face_rec.wait()

    @pyqtSlot(list)
    def delt(self, records: list):
        # calculate filename
        filename = date.today().strftime("%Y-%m-%d") + ".xls"
        th = AttendRecordThread(filename, records)
        th.start()
        th.wait()

    @pyqtSlot(list)
    def change_sign_info(self, info: list):
        self.cover.ui.sign_name.setText(info[0])
        self.cover.ui.sign_time.setText(info[1])
        self.cover.ui.sign_name.setStyleSheet("font-size:14pt; font-weight:600;color:#0dc839;")
        self.cover.ui.sign_time.setStyleSheet("font-size:14pt; font-weight:600;color:#0dc839;")
        self.cover.ui.label_5.setPixmap(QPixmap("./resource/images/signin_success.png"))
        self.cover.ui.widget.setStyleSheet("#widget{background-color: rgba(46, 255, 0, 40);}")
        if not info[2]:
            self.cover.ui.sign_name.setStyleSheet("font-size:14pt; font-weight:600;color:red;")
            self.cover.ui.sign_time.setStyleSheet("font-size:14pt; font-weight:600;color:red;")
            self.cover.ui.label_5.setPixmap(QPixmap("./resource/images/signin_fail.png"))
            self.cover.ui.widget.setStyleSheet("#widget{background-color: rgba(255, 0, 0, 40);}")
        if not self.cover.ui.widget.isVisible():
            logger.warning("set visible")
            self.cover.ui.widget.setVisible(True)

    def set_cover_visible(self):
        if self.cover.ui.widget.isVisible():
            self.cover.ui.widget.setVisible(False)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if not self.cover.isActiveWindow():
            logger.warning("activate window")
            self.cover.activateWindow()

    def moveEvent(self, a0: QtGui.QMoveEvent) -> None:
        self.cover.move(self.pos())
        self.cover.activateWindow()

    def on_detective_people(self, ):
        self.face_rec.start_tracker()
