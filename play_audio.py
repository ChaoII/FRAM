from PyQt5.QtCore import QThread
from playsound import playsound


class PlayAudioThread(QThread):
    def __init__(self):
        super(PlayAudioThread, self).__init__()

    def run(self):
        playsound("./audio/thanks.wav")
