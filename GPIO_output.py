import time
from PySide2.QtCore import QThread
import Jetson.GPIO as GPIO


class DetectorPersonThread(QThread):
    def __init__(self, signal: Queue, output_pin: int = 33, val: int = 0, frequency: int = 50, delay=0.05):
        """
        DetectorPersonThread which carry the GPIO output
        :param signal:trigger signal，a queue which is thread safe
        :param output_pin:io number
        :param val: pwm duty cycle
        :param frequency:pwm frequency
        """
        super(DetectorPersonThread, self).__init__()
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(output_pin, GPIO.OUT)
        self.P = GPIO.PWM(output_pin, frequency).start(val)
        self.signal = signal
        self.delay = delay

    def run(self):
        while True:
            if self.signal.get():
                try:
                    self.P.ChangeDutyCycle(100)
                    time.sleep(self.delay)
                    self.P.ChangeDutyCycle(0)
                    self.signal.empty()
                except Exception as e:
                    self.signal.empty()
                    print(str(e))
