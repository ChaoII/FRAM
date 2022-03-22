import serial
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal


class DetectorPersonThread(QThread):
    people_entry_signal = pyqtSignal()

    def __init__(self, com='/dev/ttyTHS1', port=115200, timeout=2):
        """
        DetectorPersonThread which carry the GPIO input
        :param: input_pin
        """
        super(DetectorPersonThread, self).__init__()
        self.com = com
        self.port = port
        self.timeout = timeout

    def run(self):
        while True:
            try:
                fh_data = serial.Serial(self.com, self.port, timeout=self.timeout).read(7).hex()
                if fh_data[0:2] == '01':
                    fh_datas = int(fh_data[6:10], 16) / 10
                    if fh_datas > 30 or fh_datas <= 90:
                        self.people_entry_signal.emit()
            except Exception as e:
                logger.error(e)
