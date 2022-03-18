import os
import pandas as pd
from PyQt5.QtCore import QThread
from loguru import logger


class AttendRecordThread(QThread):
    def __init__(self, filename: str, face_infos: list):
        """
        打卡记录存储线程
        :param filename:打开记录文件名
        :param face_infos: 人脸信息，【id,name,datetime】
        """
        super(AttendRecordThread, self).__init__()
        self._file_path = os.path.join("attend", filename)
        self._face_infos = face_infos

    @logger.catch
    def run(self):
        if not os.path.exists(self._file_path):
            df = pd.DataFrame(data=[], index=None, columns=["id", "name", "datetime"])
            df.to_excel(self._file_path)
            logger.warning(f"文件【{self._file_path}】不存在,完成文件创建")

        df = pd.read_excel(self._file_path, index_col=0)
        new_info = pd.DataFrame(data=self._face_infos, index=None, columns=["id", "name", "datetime"])
        df = pd.concat([df, new_info], ignore_index=True)
        df = df.groupby("id").apply(
            lambda x: x.sort_values(by='datetime', ascending=True).iloc[[0, -1], :]).reset_index(drop=True)

        try:
            df.to_excel(self._file_path)
        except PermissionError as e:
            logger.error(f"打卡记录写入失败，失败原因：【permission denied，检查文件是否被占用】")
