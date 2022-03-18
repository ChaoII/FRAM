import os
import sys
import PyQt5
from PyQt5 import QtWidgets
from mainwidget import MyWidget
from loguru import logger

logger.add("./logs/log_{time}.log", rotation="00:00", retention="10 days")

dir_name = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dir_name, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "jetsonface"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MyWidget()
    # widget.resize(300, 200)
    widget.show()

    sys.exit(app.exec_())
