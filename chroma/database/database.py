from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error
from typing import ClassVar
from worker import AtomicInteger

# *************** Exception ***************

class DatabaseException(Exception):
    """Raised when there is a problem with Database"""

# *************** Database ***************

class Database:
    DATABASE_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self, name, host, user, password) -> None:
        self.__pool = MySQLConnectionPool(pool_name=f"Database-{Database.DATABASE_ID.get_and_increment()}", database=name, host=host, user=user, password=password)
    def select(self) -> list:
        connection = self.__pool.get_connection()
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, values)
            return cursor.fetchall()
        except Error: raise RuntimeError("Database query execution failed") # watchdog
        finally: cursor.close(), connection.close()
    def execute(self, statement, values) -> None:
        connection = self.__pool.get_connection()
        try:
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, values)
            connection.commit()
        except Error: raise RuntimeError("Database query execution failed") # watchdog
        finally: cursor.close(), connection.close()