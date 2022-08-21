import datetime
from typing import Union, Generator

from psycopg2.sql import Identifier, Composed, SQL

from other.data_structures import DataForCreateRequest
from other.exceptions import ManyInstanceOfClassError

alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

ModelValuesTypes = Union[int, str, datetime.date, 'BaseModel']
ValuesTypesFromDB = Union[int, str, datetime.date]
RawOutputData = tuple[Union[int, str, datetime.date], ...]
RawDictOutputData = dict[str, Union[int, str, datetime.date]]
DictOutputData = dict[str, Union[int, str, datetime.date, 'DictOutputData']]


class Singleton:
    """Класс, реализующий паттерн singleton. Не дает создавать более одного экземпляра данного класса"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            raise ManyInstanceOfClassError
        cls.__instance = super().__new__(cls)
        return cls.__instance


class ClassOrInstanceProperty:

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        if instance:
            return self.fget(instance)
        return self.fget(owner)


def process_date_for_request(date: datetime.date) -> str:
    return f'{date.year}/{date.month}/{date.day}'


def get_pk_related_entry(value: Union['BaseModel', int]) -> int:
    if type(value) == int:
        return value
    return value.pk


def get_data_for_create_saving_request(model: 'BaseModel') -> DataForCreateRequest:
    """Возвращает данные для создания SQL запроса, сохраняющего данные"""
    columns, arguments = [], []
    for attr, value in model:
        if attr == 'pk':
            continue
        add_data_to_lists(attr, value, arguments, columns, model)
    return DataForCreateRequest(columns, arguments)


def add_data_to_lists(attr: str, value: ModelValuesTypes,
                      arguments: list, columns: list, model: 'BaseModel') -> None:
    """Добавляет данные в списки аргументов и столбцов для создания запроса к БД"""
    attr, value = process_pair_of_attr_and_value(attr, value, model)
    arguments.append(value)
    columns.append(attr)


def process_pair_of_attr_and_value(attr: str, value: ModelValuesTypes,
                                   model: 'BaseModel') -> tuple[str, Union[int, str]]:
    if attr in model.related_data:
        value = get_pk_related_entry(value)
        attr = attr + '_id'
    elif isinstance(value, datetime.date):
        value = process_date_for_request(value)
    return attr, value


def get_strings_for_sql(count: int) -> list[str]:
    """Возващает строки видов '{}, {}, {}' и '%s, %s, %s' для создания SQL запроса, сохраняющего данные"""
    return [', '.join(s for _ in range(count)) for s in ('{}', '%s')]


def get_identifiers_for_request(columns: list[str]) -> list[Identifier]:
    return [Identifier(column) for column in columns]


def get_sql_for_creation_method(columns_sql: str, arguments_sql: str,
                                identifiers: list[Identifier]) -> Composed:
    return SQL('INSERT INTO {} ' + f'({columns_sql})' + f' VALUES ({arguments_sql})').format(*identifiers)


def get_data_for_join_part_of_sql(model: 'BaseModel') -> tuple[str, list[Identifier]]:
    s, identifiers = '', []
    for attr in model.related_data:
        s += 'JOIN {} ON {}.{} = {}.id '
        related_table_name = model.related_data[attr].db_table
        identifiers += [Identifier(related_table_name), Identifier(model.db_table),
                        Identifier(attr + '_id'), Identifier(related_table_name)]
    return s, identifiers


def get_sql_for_all_method(join_part: str, identifiers: list[Identifier]) -> Composed:
    first_part = 'SELECT * FROM {} '
    return SQL(first_part + join_part).format(*identifiers)


def get_all_output_like_dict(model: 'BaseModel',
                             output: list[RawOutputData]) -> list[DictOutputData]:
    return [process_raw_line_of_output(raw_line, model) for raw_line in output]


def process_raw_line_of_output(line: tuple[ValuesTypesFromDB, ...], model: 'BaseModel') -> DictOutputData:
    get_value = get_value_from_collection(line)
    dict_line = get_raw_line_like_dict(get_value, model)
    replace_pk_with_dict(dict_line, get_value, model)
    return dict_line


def get_raw_line_like_dict(value: Generator[Union[int, str, datetime.date], None, None],
                           model: 'BaseModel') -> RawDictOutputData:
    return {attr: next(value) for attr in model.attributes}


def get_value_from_collection(collection: tuple) \
        -> Generator[Union[int, str, datetime.date], None, None]:
    for value in collection:
        yield value


def replace_pk_with_dict(dict_line: RawDictOutputData,
                         get_value: Generator[Union[int, str, datetime.date], None, None],
                         model: 'BaseModel') -> None:
    """Заменяет первичные ключи связанных моделей в словаре dict_line, на словари с данными"""
    for related_model, related_model_class in model.related_data.items():
        dict_line[related_model] = get_raw_line_like_dict(get_value, related_model_class)


def get_all_output_like_model(model: 'BaseModel', output: list[DictOutputData]):
    return [process_dict_line(model, dict_line) for dict_line in output]


def process_dict_line(model: 'BaseModel', dict_line: DictOutputData) -> 'BaseModel':
    """Заменяет словари (главный и вложенные) с данными на экземпляры моделей.
    Возврвщает готовую к использованию модель"""
    for related_model, related_model_class in model.related_data.items():
        dict_line[related_model] = get_dict_line_like_model(related_model_class, dict_line[related_model])
    return get_dict_line_like_model(model, dict_line)


def get_dict_line_like_model(model: 'BaseModel', dict_line: dict[str, ValuesTypesFromDB]) -> 'BaseModel':
    pk = dict_line.pop('pk')
    obj = model(**dict_line)
    obj.pk = pk
    return obj
