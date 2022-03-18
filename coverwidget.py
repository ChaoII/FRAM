from datetime import datetime
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5 import QtWidgets
from ui.ui_cover import Ui_Form


class CoverWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 实例化UI对象
        self.ui.setupUi(self)  # 初始化
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self._update_time)

    def _update_time(self):
        cur_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ui.cur_time.setText(" " + cur_time)
