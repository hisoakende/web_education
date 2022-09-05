from typing import Callable

import psycopg2
import psycopg2.extras
from psycopg2.extensions import cursor

from other.data_structures import Request
from other.exceptions import DontExistUnexecutedRequests
from other.utils import Singleton


class Database(Singleton):
    """
    Класс, позволяющий работать с базой данных.
    Совершает обработку запросов, выполненяет транзакции
    """

    def __init__(self, database: str,
                 user: str, password: str,
                 host: str, port: str) -> None:
        self.__database = database
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__unexecuted_requests = []
        self._output = None

    def __connect_to_db(self) -> None:
        self.conn = psycopg2.connect(database=self.__database,
                                     user=self.__user,
                                     password=self.__password,
                                     host=self.__host,
                                     port=self.__port)

    def add_unexecuted_request(self, request: Request) -> None:
        if not isinstance(request, Request):
            raise TypeError('Запрос не является экземпляром класса \'Request\'')
        self.__unexecuted_requests.append(request)

    def check_to_requests_exist(self) -> None:
        if not self.__unexecuted_requests:
            raise DontExistUnexecutedRequests('Отстувуют запросы для обработки')

    def __execute_one_request(self, cur: cursor, request: Request) -> None:
        cur.execute(*request[:2])
        if request.type == 'with_output':
            self._output = cur.fetchall()

    def __execute_requests(self, cur: cursor) -> None:
        for request in self.__unexecuted_requests:
            self.__execute_one_request(cur, request)
        self.__unexecuted_requests = []

    def __processing_requests(self) -> None:
        with self.conn.cursor() as cur:
            self.__execute_requests(cur)

    @staticmethod
    def __process_connection(func: Callable) -> Callable:
        def wrapper(self: 'Database') -> None:
            self.check_to_requests_exist()
            self.__connect_to_db()
            func(self)
            self.conn.close()

        return wrapper

    @__process_connection
    def execute_requests(self) -> None:
        self.__processing_requests()
        self.conn.commit()

    @__process_connection
    def execute_transaction(self) -> None:
        with self.conn:
            self.__processing_requests()

    @property
    def output(self) -> list[tuple]:
        result = self._output
        self._output = None
        return result
