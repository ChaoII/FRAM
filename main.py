import os
import PySide2
from PySide2 import QtWidgets
from mainwidget import MyWidget
dir_name = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dir_name, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    # widget.resize(300, 200)
    widget.show()

    sys.exit(app.exec_())
