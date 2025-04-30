from typing import ClassVar, Optional, Tuple, List
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error
from worker import AtomicInteger

# *************** Database ***************

class Database:
    DATABASE_ID: ClassVar[AtomicInteger] = AtomicInteger()
    def __init__(self, name, host, user, password) -> None:
        self.__pool = MySQLConnectionPool(pool_name=f"Database-{Database.DATABASE_ID.get_and_increment()}", database=name, host=host, user=user, password=password, autocommit=False)
    def select(self, statement: str, values: Optional[Tuple] = None) -> List[Tuple]:
        try:
            connection = self.__pool.get_connection()
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, values or ())
            return cursor.fetchall()
        except Error: raise RuntimeError("Database query execution failed") # watchdog
        finally:
            if cursor: cursor.close()
            if connection: connection.close()
    def execute(self, statement: str, values: Optional[Tuple] = None) -> None:
        try:
            connection = self.__pool.get_connection()
            cursor = connection.cursor(prepared=True)
            cursor.execute(statement, values or ())
            connection.commit()
        except Error: raise RuntimeError("Database query execution failed") # watchdog
        finally:
            if cursor: cursor.close()
            if connection: connection.close()
    def __enter__(self) -> Database: return self
    def __exit__(self) -> None: self.__pool.close()