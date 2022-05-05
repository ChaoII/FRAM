import sqlite3
from loguru import logger
from PyQt5.QtCore import QThread


class AttendRecordThread(QThread):
    def __init__(self, face_infos: list):
        """
        打卡记录存储线程
        :param face_infos: 人脸信息，【id,name,datetime】
        """

        super(AttendRecordThread, self).__init__()
        self._face_infos = face_infos
        # table【attend】 出勤表

    @logger.catch
    def run(self):
        # sql 连接必须在线程内创建
        conn = sqlite3.connect("attend.db")
        cursor = conn.cursor()
        face_infos = []
        face_ids = []
        for face_info_ in self._face_infos:
            if face_info_["id"] not in face_ids:
                face_infos.append((face_info_["id"], face_info_["name"], face_info_["datetime"]))
                face_ids.append(face_info_["id"])
        sql = f"insert into attend (staff_id,name,attend_time)values (?,?,?)"
        logger.info(sql)
        try:
            cursor.executemany(sql, face_infos)
            conn.commit()
        except Exception as e:
            logger.error(e)
            conn.rollback()
        conn.close()
