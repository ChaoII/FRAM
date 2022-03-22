import platform
from datetime import date, datetime
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5 import QtWidgets
# from serial_input import DetectorPersonThread
from ui.ui_main_widget import Ui_Form
from face_recognize import FaceRecognizeThread
from attend_record import AttendRecordThread
from loguru import logger


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 实例化UI对象
        self.ui.setupUi(self)  # 初始化
        # self.setWindowFlags(Qt.FramelessWindowHint)

        self.ui.widget.setVisible(False)
        self.face_rec = FaceRecognizeThread(use_gpu=platform.system() != "Windows")
        # self.people_rec = DetectorPersonThread()
        # self.people_rec.people_entry_signal.connect(self.on_detective_people, Qt.BlockingQueuedConnection)
        # self.people_rec.start()
        # 实时画面传输信号
        self.face_rec.img_finish_signal.connect(self.show_img, Qt.BlockingQueuedConnection)
        # 打卡信息保存信号
        self.face_rec.record_attend_signal.connect(self.delt, Qt.BlockingQueuedConnection)
        # 识别结果信号-触发显示信息
        self.face_rec.rec_result_signal.connect(self.change_sign_info, Qt.BlockingQueuedConnection)
        # 判断是否有人脸的信号--触发控件 visible
        self.face_rec.is_person_signal.connect(self.set_cover_invisible, Qt.BlockingQueuedConnection)
        QTimer.singleShot(500, self.face_rec.start)
        # 显示字体大小
        self.cur_font_size = 15
        self.font_size_rate = self.cur_font_size / self.geometry().height()
        # 时间显示定时器
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.ui.label_time.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        timer.start(1000)

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
        th = AttendRecordThread(records)
        th.start()
        th.wait()

    @pyqtSlot(list)
    def change_sign_info(self, info: list):
        # 设置样式
        self.ui.sign_name.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:#0dc839;")
        self.ui.sign_time.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:#0dc839;")
        self.ui.widget.setStyleSheet("#widget{background-color: rgba(46, 255, 0, 40);}")
        # 设置文字
        self.ui.sign_name.setText(info[0])
        self.ui.sign_time.setText(info[1])
        # 设置图片
        self.ui.label_attend_img.setPixmap(QPixmap("./resource/images/signin_success.png"))

        if not info[2]:
            self.ui.sign_name.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:red;")
            self.ui.sign_time.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:red;")
            self.ui.widget.setStyleSheet("#widget{background-color: rgba(255, 0, 0, 40);}")
            self.ui.label_attend_img.setPixmap(QPixmap("./resource/images/signin_fail.png"))

        if not self.ui.widget.isVisible():
            logger.warning("set visible")
            self.ui.widget.setVisible(True)

    def set_cover_invisible(self):
        if self.ui.widget.isVisible():
            self.ui.widget.setVisible(False)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        if not self.isActiveWindow():
            logger.warning("activate window")
            self.activateWindow()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:

        self.ui.image_label.resize(self.geometry().width(), self.geometry().height())
        cur_height_ = self.geometry().height()
        cur_with_ = self.geometry().width()
        #
        # self.ui.cover.move(0, 0)
        self.ui.cover.resize(cur_with_, cur_height_)

        self.cur_font_size = self.font_size_rate * self.geometry().height()
        self.ui.label_1.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:#ffffff;")
        self.ui.label_2.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:#ffffff;")
        self.ui.label_time.setStyleSheet(f"font-size:{self.cur_font_size}pt; font-weight:600;color:rgb(85, 85, 85);")

    def on_detective_people(self):
        self.face_rec.start_tracker()

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_F:
            if not self.isFullScreen():
                self.showFullScreen()
            else:
                self.showNormal()
