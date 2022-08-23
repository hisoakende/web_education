from typing import Callable

from interaction_with_db.manage_db import Database
from other.data_structures import Request
from other.utils import *
from working_with_models.models import BaseModel


class RequestFactory:
    __all_columns = 'SELECT * FROM {}'
    __update_part = 'UPDATE {}'
    __sort_part = 'ORDER BY {}.{}'
    __delete_part = 'DELETE FROM {}'

    @classmethod
    def all(cls, model: BaseModel) -> Request:
        """Запрос, возвращающий все записи из БД"""

        join_part, identifiers_for_join = get_data_for_join_part_of_sql(model)
        identifiers = get_identifiers(model.db_table) + identifiers_for_join + get_identifiers(model.db_table, 'id')
        sql = get_sql(identifiers, cls.__all_columns, join_part, cls.__sort_part)
        return Request(sql, [], 'with_output')

    @classmethod
    def filter(cls, model: BaseModel, **kwargs) -> Request:
        """
        Запрос, возвращающий все записи, удовлетворяющие условиям, из БД.

        Все условия выборки из словаря 'kwargs' будут проверяться вместе, с помощью 'AND'.
        К условиям выборки можно добавить префикс (имя связанной модели),
        чтобы применить условия к полям связанной модели. Префикс от условия
        отделяется двумя нижними подчеркиваниями '__'. Например: 'model__name'
        """

        join_part, identifiers_for_join = get_data_for_join_part_of_sql(model)
        where_part, identifiers_for_where, arguments = get_data_for_where_part_of_sql(model, **kwargs)
        identifiers = get_identifiers(model.db_table) + identifiers_for_join + \
                      identifiers_for_where + get_identifiers(model.db_table, 'id')
        sql = get_sql(identifiers, cls.__all_columns, join_part, where_part)
        return Request(sql, arguments, 'with_output')

    @classmethod
    def get(cls, model: BaseModel, **kwargs) -> Request:
        """Запрос, возвращающий только одну запись, удовлетворяющую условию, из БД"""
        return cls.filter(model, **kwargs)

    @classmethod
    def save(cls, model: BaseModel) -> Request:
        """Запрос, сохраняющий все изменения модели. Присутствие атрибута 'pk' в модели обязательно"""

        set_part, identifiers_for_set, arguments_set = get_data_for_set_part_of_sql(model)
        where_part, identifiers_for_where, argument_where = get_data_for_where_part_of_sql(model, pk=model.pk)
        identifiers = [Identifier(model.db_table)] + identifiers_for_set + identifiers_for_where
        sql = get_sql(identifiers, cls.__update_part, set_part, where_part)
        return Request(sql, arguments_set + argument_where, 'without_output')

    @staticmethod
    def create(model: BaseModel) -> Request:
        """
        Запрос, создающий новую запись в БД
        Для этого запроса в полях внешних ключей нужно указывать
        либо pk записи связанной таблицы, либо экземпляр модели, с присутсвующим pk
        """

        columns, arguments = get_data_to_write_to_db(model)
        columns_sql, arguments_sql = get_strings_for_sql(len(arguments))
        identifiers = get_identifiers(model.db_table, *columns)
        sql = get_sql_for_creation_method(columns_sql, arguments_sql, identifiers)
        return Request(sql, arguments, 'without_output')

    @classmethod
    def delete(cls, model: 'BaseModel'):
        """Запрос, удаляющий запись из БД"""

        where_part, identifiers_for_where, argument = get_data_for_where_part_of_sql(model, pk=model.pk)
        identifiers = [Identifier(model.db_table)] + identifiers_for_where
        sql = get_sql(identifiers, cls.__delete_part, where_part)
        return Request(sql, argument, 'without_output')


class TablesManager(Singleton):
    """
    Класс для работы с таблицами базы данных.
    Получает запросы из класса 'RequestFactory' и передает их в экземпляр класс 'Database'.
    Получает данные из 'Database', передает в обработчик и возвращает обработанные данные.

    Запросы, не нуждающиеся в коммите, выполняются автоматически.
    Запрос, нуждающийся в коммите, можно выполнить сразу же, указав 'execution'=True
    Запросы, не нуждающиеся в коммите, по умолчанию просто добавляются в экземпляр класса 'Database'
    (ВНИМАНИЕ: при автоматическом исполнении какого-либо запроса другие запросы,
    находящиеся в '__unexecuted_requests' экзеспляра класса 'Database', будут исполнены)

    Работа класса: TablesManager.allowed_method(table_name, **kwargs)

    _model - модель, с которой ведется работа в данный момент. Значение этого атрибута
    устанавливает сама модель перед вызовом метода этого класса
    """

    __allowed_methods = ('all', 'filter', 'get', 'save', 'create', 'delete')
    __methods_with_result = ('all', 'filter', 'get')
    __methods_with_kwargs = ('filter', 'get')

    def __init__(self, database: Database) -> None:
        self.__db = database
        self._model: Union[None, BaseModel] = None

    def __get_request_result_if_necessary(self) -> Union[None, list[BaseModel]]:
        if self.__is_method_with_result():
            result = process_output(self._model, self.__db.output)
            if self.__method == 'get':
                result = result[0]
            return result

    def __check_for_kwargs_dont_exist(self) -> None:
        if self.arguments_for_request:
            raise TypeError('Аргументы должны отсутсвовать')

    def __get_request(self) -> Request:
        if self.__method in self.__methods_with_kwargs:
            return self.method_to_get_request(self._model, **self.arguments_for_request)
        self.__check_for_kwargs_dont_exist()
        return self.method_to_get_request(self._model)

    def __register_request(self) -> None:
        self.method_to_get_request = getattr(RequestFactory, self.__method)
        request = self.__get_request()
        self.__db.add_unexecuted_request(request)

    def __is_method_with_result(self) -> bool:
        return self.__method in self.__methods_with_result

    def __execute_requests_if_necessary(self) -> None:
        """Метод выполняет все запросы, находящиеся в экземпляре класса Database"""
        if self.__is_method_with_result() or self.execution:
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

    def __process_method(self, **kwargs: Union[int, str]) -> Union[None, list[BaseModel]]:
        self.__process_kwargs(**kwargs)
        self.__register_request()
        self.__execute_requests_if_necessary()
        return self.__get_request_result_if_necessary()

    def __getattr__(self, method: str) -> Callable:
        if method not in self.__allowed_methods:
            raise AttributeError(f'Метод {method} не разрешен')
        self.__method = method
        return self.__process_method


def register_tables_manager(manager: 'TablesManager') -> None:
    BaseModel._manager = manager


def process_output(model, raw_output: list[RawOutputData]):
    """Обработка сырых данных из БД"""
    output_dict = get_all_output_like_dict(model, raw_output)
    result = get_all_output_like_model(model, output_dict)
    return result
