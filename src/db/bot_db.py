import logging
import sqlite3
from enum import Enum

FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


class DBStatus(Enum):
    SUCCESS = 1
    WARNING = 2
    BAD_ACCESS = 3
    ALREADY_EXIST = 4


class UserGroupDB:
    def __init__(self, path: str):
        self.conn = None
        self.path = path
        try:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys=ON")
        except sqlite3.Error as error:
            logger.warning(error)
            raise error  # Критическая ситуация, иначе будет UB

    def add_group(self, g_name: str):  # добавить группу
        new_id = None
        status = DBStatus.WARNING
        try:
            result = self.cursor.execute("INSERT INTO groups(g_name) VALUES((?))", (g_name,))
            new_id = result.lastrowid
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return new_id, status

    def delete_group(self, g_id: int, g_name: str):  # удалить группу
        if not self._check_access(g_id, g_name):
            return DBStatus.BAD_ACCESS
        status = DBStatus.WARNING
        try:
            self.cursor.execute("DELETE FROM groups WHERE (g_id = (?) AND g_name = (?))",
                                (g_id, g_name))
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return status

    def set_group_dates(self, g_id: int, g_name: str, flight: str,
                        arrival: str) -> DBStatus:  # задать группе дату прибытия и отбытия
        if not self._check_access(g_id, g_name):
            return DBStatus.BAD_ACCESS
        status = DBStatus.WARNING
        try:
            self.cursor.execute("UPDATE groups SET flight = (?), arrival = (?) WHERE g_id = (?)",
                                (flight, arrival, g_id))
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return status

    def view_group(self, g_id: int, g_name: str):  # посмотреть участников группы
        result = None
        if not self._check_access(g_id, g_name):
            return result
        try:
            query = self.cursor.execute("SELECT u_name, city FROM users WHERE g_id = (?)", (g_id,))
            result = query.fetchall()
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def get_all_groups(self):  # увидеть все группы
        result = None
        try:
            result = self.cursor.execute("SELECT * FROM groups")
            result = result.fetchall()
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def add_user(self, g_id: int, g_name: str, u_name: str, city: str) -> DBStatus:  # добавить пользователя в группу
        if not self._check_access(g_id, g_name):
            return DBStatus.BAD_ACCESS
        result = DBStatus.WARNING
        try:
            query = self.cursor.execute("SELECT * FROM users WHERE (u_name = (?) AND g_id = (?))",
                                        (u_name, g_id))
            if len(query.fetchall()):
                result = DBStatus.ALREADY_EXIST
            else:
                self.cursor.execute("INSERT INTO users(u_name, city, g_id) VALUES((?), (?), (?))",
                                    (u_name, city, g_id))
                result = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def delete_user(self, g_id: int, g_name: str, u_name: str) -> DBStatus:  # убрать юзера из группы
        if not self._check_access(g_id, g_name):
            return DBStatus.BAD_ACCESS
        status = DBStatus.WARNING
        try:
            self.cursor.execute("DELETE FROM users WHERE (g_id = (?) AND u_name = (?))",
                                (g_id, u_name))
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return status

    def update_user(self, g_id: int, g_name: str, u_name: str,
                    new_city: str) -> DBStatus:  # обновить город пользователя
        if not self._check_access(g_id, g_name):
            return DBStatus.BAD_ACCESS
        status = DBStatus.WARNING
        try:
            self.cursor.execute("UPDATE users SET city = (?) WHERE (g_id = (?) AND u_name = (?))",
                                (new_city, g_id, u_name))
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return status

    def get_all_users(self):  # посмотреть на все группы
        result = None
        try:
            result = self.cursor.execute("SELECT * FROM users")
            result = result.fetchall()
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def _check_access(self, g_id: int, g_name: str):  # проверить совпадает ли id и имя группы
        result = False
        try:
            query = self.cursor.execute("SELECT g_name FROM groups WHERE g_id = (?)", (g_id,))
            g_names = query.fetchall()
            if len(g_names) and g_names[0][0] == g_name:
                result = True
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def recreate_table(self):  # дроп старых и создание новых таблиц
        status = DBStatus.WARNING
        try:
            self.cursor.execute("DROP TABLE groups")
            self.cursor.execute("DROP TABLE users")
        except sqlite3.Error as error:
            logger.warning(error)

        try:
            self.cursor.execute(
                "CREATE TABLE groups("
                "g_id INTEGER PRIMARY KEY, "
                "g_name varchar(20) NOT NULL, "
                "flight date, "
                "arrival date)")
            self.cursor.execute(
                "CREATE TABLE users("
                "u_name varchar(20) NOT NULL, "
                "city varchar(20) NOT NULL, "
                "g_id INTEGER NOT NULL, "
                "FOREIGN KEY (g_id) REFERENCES groups(g_id) ON DELETE CASCADE)")
            self.conn.commit()
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
            status = DBStatus.WARNING
        finally:
            return status

    def __del__(self):
        if self.conn:
            self.conn.close()
