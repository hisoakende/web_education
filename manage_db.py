import psycopg2
from psycopg2.extensions import connection, cursor

from data_structures import Request
from exceptions import ManyInstanceOfDatabaseError, DontExistUnexecutedRequests


class Database:
    """
    Класс, позволяющий работать с базой данных.
    Совершает обработку запросов, выполненяет транзакции
    """

    __instance = None

    def __new__(cls, *args, **kwargs) -> 'Database':
        if cls.__instance:
            raise ManyInstanceOfDatabaseError('Может сущестовать только один экземпляр базы данных')
        cls.__instance = super().__new__(cls)
        return cls.__instance

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

    def __connect_to_db(self) -> connection:
        return psycopg2.connect(
            database=self.__database,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )

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

    def __processing_requests(self, conn: connection) -> None:
        self.check_to_requests_exist()
        with conn.cursor() as cur:
            self.__execute_requests(cur)

    def execute_transaction(self) -> None:
        with self.__connect_to_db() as conn:
            self.__processing_requests(conn)
        conn.close()

    @property
    def output(self) -> list[tuple]:
        result = self._output
        self._output = None
        return result
