import psycopg2
from psycopg2.extensions import connection

from exceptions import ManyInstanceOfDatabaseError


class Database:
    """Класс, позволяющий работать с базой данных"""

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

    def connect_to_db(self) -> connection:
        return psycopg2.connect(
            database=self.__database,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )
