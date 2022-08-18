from typing import Callable, Union

from psycopg2.sql import Identifier

from interaction_with_db.manage_db import Database
from other.data_structures import Request
from other.utils import Singleton, get_data_for_create_saving_request, get_identifiers_for_request, \
    get_strings_for_sql, get_sql_for_create_method, get_data_for_join_part_of_sql, get_sql_for_all_method
from working_with_models.models import BaseModel


class RequestFactory:

    @staticmethod
    def all(model: BaseModel) -> Request:
        """Запрос, возвращающий все записи из БД"""

        join_part, identifiers = get_data_for_join_part_of_sql(model)
        identifiers.insert(0, Identifier(model.db_table))
        sql = get_sql_for_all_method(join_part, identifiers)
        return Request(sql, [], 'with_output')

    @staticmethod
    def create(model: BaseModel) -> Request:
        """
        Запрос, создающий новую запись в БД
        Для этого запроса в полях внешних ключей нужно указывать
        либо pk записи связанной таблицы, либо экземпляр модели, с присутсвующим pk
        """

        columns, arguments = get_data_for_create_saving_request(model)
        columns_sql, arguments_sql = get_strings_for_sql(len(arguments))
        identifiers = get_identifiers_for_request([model.db_table] + columns)
        sql = get_sql_for_create_method(columns_sql, arguments_sql, identifiers)
        return Request(sql, arguments, 'without_output')


def process_output(output):
    """Обработка сырых данных из БД"""
    return output


class TablesManager(Singleton):
    """
    Класс для работы с таблицами базы данных.
    Получает запросы из класса 'RequestFactory' и передает их в экземпляр класс 'Database'.
    Из 'Database' получает данные, передает в обработчик и возвращает обработанные данные.

    Запросы, не нуждающиеся в коммите, выполняются автоматически.
    Запрос, нуждающийся в коммите, можно выполнить сразу же, указав 'execution'=True
    Запросы, не нуждающиеся в коммите, по умолчанию просто добавляются в экземпляр класса 'Database'
    (ВНИМАНИЕ: при автоматическом исполнении какого-либо запроса другие запросы,
    находящиеся в '__unexecuted_requests' экзеспляра класса 'Database', будут исполнены)

    Работа класса: TablesManager.allowed_method(table_name, **kwargs)

    _model - модель, с которой ведется работа в данный момент. Значение этого атрибута
    устанавливает сама модель перед вызовом метода этого класса
    """

    __allowed_methods = ('all', 'create')
    __methods_with_result = ('all',)
    __methods_with_kwargs = ()

    def __init__(self, database: Database) -> None:
        self.__db = database
        self._model: Union[None, BaseModel] = None

    def __check_for_kwargs_dont_exist(self) -> None:
        if self.arguments_for_request:
            raise TypeError('Аргументы должны отсутсвовать')

    def __get_request(self) -> Request:
        if self.method in self.__methods_with_kwargs:
            return self.method_to_get_request(self._model, **self.arguments_for_request)
        self.__check_for_kwargs_dont_exist()
        return self.method_to_get_request(self._model)

    def __register_request(self) -> None:
        self.method_to_get_request = getattr(RequestFactory, self.method)
        request = self.__get_request()
        self.__db.add_unexecuted_request(request)

    def __execute_requests_if_necessary(self) -> None:
        """Метод выполняет все запросы, находящиеся в экземпляре класса Database"""
        if self.method in self.__methods_with_result or self.execution:
            self.__db.execute_requests()

    def __check_execution_type(self) -> None:
        if not isinstance(self.execution, bool):
            raise TypeError('Аругемент execution должен быть булевым значением')

    def __set_execution_value(self, kwargs: dict[str, Union[int, str]]) -> None:
        if 'execution' in kwargs:
            self.execution = kwargs.pop('execution')
            self.__check_execution_type()
        else:
            self.execution = False

    def __process_kwargs(self, **kwargs: Union[int, str]) -> None:
        self.__set_execution_value(kwargs)
        self.arguments_for_request = kwargs

    def __wrapper_process_method(self) -> Callable:
        def __process_method(**kwargs: Union[int, str]) -> list:
            self.__process_kwargs(**kwargs)
            self.__register_request()
            self.__execute_requests_if_necessary()
            return process_output(self.__db.output)

        return __process_method

    def __getattr__(self, method: str) -> Callable:
        if method not in self.__allowed_methods:
            raise AttributeError(f'Метод {method} не разрешен')
        self.method = method
        return self.__wrapper_process_method()


def register_tables_manager(manager: 'TablesManager') -> None:
    BaseModel._manager = manager
