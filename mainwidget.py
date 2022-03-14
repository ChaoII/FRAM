from PySide2 import QtCore
from PySide2.QtGui import QImage, QPixmap
from PySide2 import QtWidgets
from ui.ui_main_widget import Ui_Form
from PySide2.QtCore import Slot
from face_recognize import FaceRecognizeThread


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 实例化UI对象
        self.ui.setupUi(self)  # 初始化
        self.face_rec = FaceRecognizeThread()
        self.face_rec.img_finish_signal.connect(self.show_img, QtCore.Qt.ConnectionType.BlockingQueuedConnection)
        self.face_rec.start()

    @Slot(QImage)
    def show_img(self, qimg):
        self.ui.image_label.setPixmap(QPixmap.fromImage(qimg))
