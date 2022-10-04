import logging
import sqlite3


class BotDB:
    def __init__(self):
        self.conn = sqlite3.connect("../db/data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys=ON")

    def add_group(self, g_name):  # добавить группу
        new_id = None
        try:
            result = self.cursor.execute("INSERT INTO groups(g_name) VALUES((?))", (g_name,))
            new_id = result.lastrowid
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return new_id

    def delete_group(self, g_id, g_name):  # удалить группу
        result = "Something went wrong"
        try:
            self.cursor.execute("DELETE FROM groups WHERE (g_id = (?) AND g_name = (?))",
                                (g_id, g_name))
            result = "Successful delete"
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def set_group_dates(self, g_id, g_name, flight, arrival) -> str:  # задать группе дату прибытия и отбытия
        if not self.__check_access(g_id, g_name):
            return "Bad access"
        result = "Something went wrong"
        try:
            self.cursor.execute("UPDATE groups SET flight = (?), arrival = (?) WHERE g_id = (?)",
                                (flight, arrival, g_id))
            result = "Successful update"
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def view_group(self, g_id, g_name):  # посмотреть участников группы
        if not self.__check_access(g_id, g_name):
            return None
        result = None
        try:
            query = self.cursor.execute("SELECT u_name, city FROM users WHERE g_id = (?)", (g_id,))
            result = query.fetchall()
        except sqlite3.Error as error:
            logging.warning(error)
        return result

    def get_all_groups(self):  # увидеть все группы
        result = None
        try:
            result = self.cursor.execute("SELECT * FROM groups")
            result = result.fetchall()
        except sqlite3.Error as error:
            logging.warning(error)
        return result

    def add_user(self, g_id, g_name, u_name, city) -> str:  # добавить пользователя в группу
        if not self.__check_access(g_id, g_name):
            return "Bad access"
        result = "Something went wrong"
        try:
            query = self.cursor.execute("SELECT * FROM users WHERE (u_name = (?) AND g_id = (?))",
                                        (u_name, g_id))
            if len(query.fetchall()):
                result = "User with this name already exist in the group"
            else:
                self.cursor.execute("INSERT INTO users(u_name, city, g_id) VALUES((?), (?), (?))",
                                    (u_name, city, g_id))
                result = "Successful add"
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def delete_user(self, g_id, g_name, u_name) -> str:  # убрать юзера из группы
        if not self.__check_access(g_id, g_name):
            return "Bad access"
        result = "Something went wrong"
        try:
            self.cursor.execute("DELETE FROM users WHERE (g_id = (?) AND u_name = (?))",
                                (g_id, u_name))
            result = "Successful delete"
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def update_user(self, g_id, g_name, u_name, new_city) -> str:  # обновить город пользователя
        if not self.__check_access(g_id, g_name):
            return "Bad access"
        result = "Something went wrong"
        try:
            self.cursor.execute("UPDATE users SET city = (?) WHERE (g_id = (?) AND u_name = (?))",
                                (new_city, g_id, u_name))
            result = "Successful delete"
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def get_all_users(self):  # посмотреть на все группы
        result = None
        try:
            result = self.cursor.execute("SELECT * FROM users")
            result = result.fetchall()
        except sqlite3.Error as error:
            logging.warning(error)
        return result

    def __check_access(self, g_id, g_name):  # проверить совпадает ли id и имя группы
        result = False
        try:
            query = self.cursor.execute("SELECT g_name FROM groups WHERE g_id = (?)", (g_id,))
            g_names = query.fetchall()
            if len(g_names) and g_names[0][0] == g_name:
                result = True
        except sqlite3.Error as error:
            logging.warning(error)
        return result

    def __del__(self):
        self.conn.close()


def create_table():  # дроп старых и создание новых таблиц
    conn = None
    try:
        conn = sqlite3.connect("../db/data.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE groups")
        cursor.execute("DROP TABLE users")
    except sqlite3.Error as error:
        logging.warning(error)
    finally:
        if conn:
            conn.close()

    try:
        conn = sqlite3.connect("../db/data.db")
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE groups("
            "g_id INTEGER PRIMARY KEY, "
            "g_name varchar(20) NOT NULL, "
            "flight date, "
            "arrival date)")
        cursor.execute(
            "CREATE TABLE users("
            "u_name varchar(20) NOT NULL, "
            "city varchar(20) NOT NULL, "
            "g_id INTEGER NOT NULL, "
            "FOREIGN KEY (g_id) REFERENCES groups(g_id) ON DELETE CASCADE)")
        conn.commit()
    except sqlite3.Error as error:
        logging.warning(error)
    finally:
        if conn:
            conn.close()