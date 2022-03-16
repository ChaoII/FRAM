from datetime import date
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import QtWidgets
from ui.ui_main_widget import Ui_Form
from face_recognize import FaceRecognizeThread
from attend_record import AttendRecordThread


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 实例化UI对象
        self.ui.setupUi(self)  # 初始化
        self.face_rec = FaceRecognizeThread()
        self.face_rec.img_finish_signal.connect(self.show_img)
        self.face_rec.record_attend_signal.connect(self.delt)

        self.face_rec.start()

    @pyqtSlot(QImage)
    def show_img(self, qimg):
        scaled_img = qimg.scaled(self.ui.image_label.size(),
                                 Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
        self.ui.image_label.setPixmap(QPixmap.fromImage(scaled_img))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.face_rec.isRunning():
            self.face_rec.stop()
            self.face_rec.quit()
            self.face_rec.wait()

    def delt(self, records: list):
        # calculate filename
        filename = date.today().strftime("%Y-%m-%d") + ".xls"
        th = AttendRecordThread(filename, records)
        th.start()
        th.wait()
