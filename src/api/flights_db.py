import logging
import os.path
import sqlite3
from enum import Enum
class DBStatus(Enum):
    SUCCESS = 1
    WARNING = 2
    BAD_ACCESS = 3
    ALREADY_EXIST = 4


FORMAT = '%(asctime)s - [%(levelname)s] -  %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


class FlightsDB:
    def __init__(self, path):
        print(os.path.exists(path))
        print('Create from', path)

        self.conn = None
        self.path = path
        try:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self.cursor.execute("PRAGMA foreign_keys=ON")
        except sqlite3.Error as error:
            logger.warning(error)

            raise error  # Критическая ситуация, иначе будет UB

    def get_all_flights(self) -> list:
        result = []
        try:
            result = self.cursor.execute("SELECT * FROM flights")
            result = result.fetchall()
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def __add_flight(self, orig: str, dest: str, flight_date: str, price: int, last_upd: str) -> DBStatus:
        result = DBStatus.WARNING
        try:
            self.cursor.execute(
                "INSERT INTO flights(orig, dest, flight_date, price, last_upd) VALUES((?), (?), (?), (?), (?))",
                (orig, dest, flight_date, price, last_upd))
            result = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logging.warning(error)
        self.conn.commit()
        return result

    def __flights_exist(self, orig: str, dest: str) -> bool:
        result = False
        try:
            query = self.cursor.execute("SELECT 1 FROM flights WHERE (orig = (?) AND dest = (?))", (orig, dest))
            output = query.fetchall()
            if len(output) > 0:
                result = True
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def __update_flight(self, orig: str, dest: str, flight_date: str, price: int, last_upd: str) -> DBStatus:
        status = DBStatus.WARNING
        try:
            self.cursor.execute("UPDATE flights SET flight_date = (?), price = (?), last_upd = (?) "
                                "WHERE (orig = (?) AND dest = (?))",
                                (flight_date, price, last_upd, orig, dest))
            status = DBStatus.SUCCESS
        except sqlite3.Error as error:
            logger.warning(error)
        self.conn.commit()
        return status

    def add_or_update_flight(self, orig: str, dest: str, flight_date: str, price: int, last_upd: str) -> DBStatus:
        if self.__flights_exist(orig, dest):
            return self.__update_flight(orig, dest, flight_date, price, last_upd)
        return self.__add_flight(orig, dest, flight_date, price, last_upd)

    def get_flight_price(self, orig: str, dest: str) -> int:
        result = None
        try:
            query = self.cursor.execute("SELECT price FROM flights WHERE (orig = (?) AND dest = (?))", (orig, dest))
            output = query.fetchall()
            if len(output) > 0:
                result = output[0][0]
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def get_flight_last_upd(self, orig: str, dest: str) -> str:
        result = None
        try:
            query = self.cursor.execute("SELECT last_upd FROM flights WHERE (orig = (?) AND dest = (?))", (orig, dest))
            output = query.fetchall()
            if len(output) > 0:
                result = output[0][0]
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def get_flight_date(self, orig: str, dest: str) -> str:
        result = None
        try:
            query = self.cursor.execute("SELECT flight_date FROM flights WHERE (orig = (?) AND dest = (?))",
                                        (orig, dest))
            output = query.fetchall()
            if len(output) > 0:
                result = output[0][0]
        except sqlite3.Error as error:
            logger.warning(error)
        return result

    def recreate_table(self) -> DBStatus:
        status = DBStatus.WARNING

        try:
            self.cursor.execute("DROP TABLE flights")
        except sqlite3.Error as error:
            logger.warning(error)

        try:
            self.cursor.execute(
                "CREATE TABLE flights("
                "orig varchar(20) NOT NULL, "
                "dest varchar(20) NOT NULL, "
                "flight_date date, "
                "price INTEGER,"
                "last_upd date,"
                "primary key (orig, dest))")
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
