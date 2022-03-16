import os
import PyQt5
from PyQt5 import QtWidgets
from mainwidget import MyWidget

dir_name = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dir_name, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    widget = MyWidget()
    # widget.resize(300, 200)
    widget.showFullScreen()

    sys.exit(app.exec_())
