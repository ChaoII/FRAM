import playsound
import time
from PyQt5.QtCore import QThread
from playsound import playsound
from loguru import logger

import os

pwd = os.path.dirname(__file__)


class PlayAudioThread(QThread):
    def __init__(self):
        super(PlayAudioThread, self).__init__()

    def run(self):
        try:
            time.sleep(2)
            playsound(os.path.join(pwd, "./audio/thanks.wav"))
        except Exception as e:
            logger.error(f"语音播放失败，失败原因:{e}")
