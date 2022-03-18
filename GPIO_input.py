import time
from loguru import logger
from PyQt5.QtCore import QThread, pyqtSignal
import Jetson.GPIO as GPIO


class DetectorPersonThread(QThread):
    people_entry_signal = pyqtSignal()

    def __init__(self, input_pin: int = 32):
        """
        DetectorPersonThread which carry the GPIO input
        :param: input_pin
        """
        super(DetectorPersonThread, self).__init__()
        self._input_pin = input_pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._input_pin, GPIO.IN)

    def run(self):
        while True:
            try:
                sense = GPIO.input(self._input_pin)
                if sense == 0:
                    time.sleep(0.1)
                    self.people_entry_signal.emit()
            except Exception as e:
                logger.error(e)
