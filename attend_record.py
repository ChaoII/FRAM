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
        for face_info_ in self._face_infos:
            id_ = face_info_["id"]
            name_ = face_info_["name"]
            time_ = face_info_["datetime"]
            sql = f"select staff_id from attend where staff_id = '{id_}' and update_time like '%{time_[:10]}%'"
            logger.info(sql)
            ret = cursor.execute(sql).fetchone()
            if ret is None:
                # 如果id空，那么插入一记录
                sql = f"insert into attend (staff_id,name,start_time,end_time,update_time)values ('{id_}','{name_}'," \
                      f"'{time_}','{time_}','{time_}')"
                logger.info(sql)
                cursor.execute(sql)
                conn.commit()
            else:
                # 就要开始比较了
                sql = f"select start_time,end_time from attend where staff_id = '{id_}' and update_time like '%{time_[:10]}%'"
                logger.info(sql)
                cursor.execute(sql)
                start_time, end_time = cursor.fetchone()
                logger.warning(start_time, end_time)
                if time_ > end_time:
                    end_time = time_
                if time_ < start_time:
                    start_time = time_
                sql = f"update attend set start_time = '{start_time}',end_time='{end_time}',update_time = '{time_}' " \
                      f"where staff_id = '{id_}' and update_time like '%{time_[:10]}%'"
                logger.info(sql)
                cursor.execute(sql)
                conn.commit()
        conn.close()
