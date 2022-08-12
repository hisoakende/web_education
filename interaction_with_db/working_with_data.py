from typing import Callable, Union

from psycopg2.sql import SQL, Identifier

from interaction_with_db.manage_db import Database
from other.data_structures import Request
from other.utils import Singleton
from working_with_models.models import BaseModel


class RequestFactory:

    @classmethod
    def all(cls, model: BaseModel, **kwargs):
        sql = SQL('SELECT * FROM {}').format(Identifier(model.db_table))
        return Request(sql, tuple(), 'with_output')


def process_output(output):
    """Обработка сырых данных из БД"""
    return output


class TablesManager(Singleton):
    """
    Класс для работы с таблицами базы данных.
    Получает запросы из класса 'SQLRequestFactory' и передает их в класс 'Database'.
    Из 'Database' получает данные, передает в обработчик и возвращает их.

    Для запросов, нуждающихся в коммите, нужно явно вызвать метод 'execute_transaction'
    класса 'Database'

    Работа класса: TablesManager.allowed_method(table_name, **kwargs)
    _model - модель, с которой ведется работа в данных момент. Значение этого атрибута
    устанавливает сама модель перед вызовом метода этого класса
    """

    __allowed_methods = ('all',)
    __methods_without_commit = ('all',)

    def __init__(self, database: Database) -> None:
        self.__db = database
        self._model: Union[None, BaseModel] = None

    def __register_request(self, method: str, **kwargs) -> None:
        request = getattr(RequestFactory, method)(self._model, **kwargs)
        self.__db.add_unexecuted_request(request)

    def __get_request_result(self, method: str) -> Union[None, list[tuple]]:
        if method in self.__methods_without_commit:
            self.__db.execute_transaction()
            return process_output(self.__db.output)

    def __wrapper_process_method(self, method: str) -> Callable:
        def __process_method(**kwargs) -> Union[None, list[tuple]]:
            self.__register_request(method, **kwargs)
            self._model = None
            return self.__get_request_result(method)

        return __process_method

    def __getattr__(self, method) -> Callable:
        if method not in self.__allowed_methods:
            raise AttributeError(f'Метода {method} не существует')
        return self.__wrapper_process_method(method)


def register_tables_manager(manager: 'TablesManager') -> None:
    BaseModel._manager = manager