from PyQt5.QtCore import QThread
from playsound import playsound
import os

pwd = os.path.dirname(__file__)


class PlayAudioThread(QThread):
    def __init__(self):
        super(PlayAudioThread, self).__init__()

    def run(self):
        playsound(os.path.join(pwd, "./audio/thanks.wav"))
