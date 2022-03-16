import os
from typing import List
import pandas as pd
from PyQt5.QtCore import QThread


class AttendRecordThread(QThread):
    def __init__(self, filename: str, face_infos: list):
        """
        """
        super(AttendRecordThread, self).__init__()
        self._file_path = os.path.join("attend", filename)
        self._face_infos = face_infos

    def run(self):
        print("-----------------------")
        if not os.path.exists(self._file_path):
            df = pd.DataFrame(data=[], index=None, columns=["name", "datetime"])
            df.to_excel(self._file_path)

        df = pd.read_excel(self._file_path, index_col=0)
        new_info = pd.DataFrame(data=self._face_infos, index=None, columns=["name", "datetime"])
        df = df.append(new_info, ignore_index=True)
        df.to_excel(self._file_path)
