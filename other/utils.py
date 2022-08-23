import datetime
from typing import Union, Generator

from psycopg2.sql import Identifier, Composed, SQL

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


def get_data_to_write_to_db(model: 'BaseModel') -> tuple[list[str], list[Union[int, str]]]:
    """Возвращает подготовленные для записи в БД данные"""
    columns, arguments = [], []
    for attr, value in model:
        if attr == 'pk':
            continue
        add_data_to_lists(attr, value, arguments, columns, model)
    return columns, arguments


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


def get_identifiers(*args: str) -> list[Identifier]:
    return [Identifier(column) for column in args]


def get_sql_for_creation_method(columns_sql: str, arguments_sql: str,
                                identifiers: list[Identifier]) -> Composed:
    s = 'INSERT INTO {} ' + f'({columns_sql})' + f' VALUES ({arguments_sql})'
    return get_sql(identifiers, s)


def get_data_for_join_part_of_sql(model: 'BaseModel') -> tuple[str, list[Identifier]]:
    s, identifiers_for_join = [], []
    for attr in model.related_data:
        s.append('JOIN {} ON {}.{} = {}.{}')
        related_table_name = model.related_data[attr].db_table
        identifiers_for_join += get_identifiers(related_table_name, model.db_table,
                                                attr + '_id', related_table_name, 'id')
    return ' '.join(s), identifiers_for_join


def get_sql(identifiers: list[Identifier], *args: str) -> Composed:
    return SQL(' '.join(args)).format(*identifiers)


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
    """
    Заменяет словари (главный и вложенные) с данными на экземпляры моделей.
    Возвращает готовую к использованию модель
    """
    for related_model, related_model_class in model.related_data.items():
        dict_line[related_model] = get_dict_line_like_model(related_model_class, dict_line[related_model])
    return get_dict_line_like_model(model, dict_line)


def get_dict_line_like_model(model: 'BaseModel', dict_line: dict[str, ValuesTypesFromDB]) -> 'BaseModel':
    pk = dict_line.pop('pk')
    obj = model(**dict_line)
    obj.pk = pk
    return obj


def get_column_view_for_db(model: 'BaseModel', attr: str) -> str:
    if attr == 'pk':
        return 'id'
    elif attr in model.related_data:
        return f'{attr}_id'
    return attr


def get_table_and_column_for_where_part(model: 'BaseModel', condition: str) -> tuple[str, str]:
    condition = condition.split('__')
    if len(condition) == 2 and condition[0] in model.related_data:
        return model.related_data[condition[0]].db_table, condition[1]
    return model.db_table, condition[0]


def process_attr_and_value_for_where_part(model: 'BaseModel', attr: str,
                                          value: ModelValuesTypes) -> tuple[str, Union[int, str]]:
    if attr == 'pk':
        attr = 'id'
    return process_pair_of_attr_and_value(attr, value, model)


def get_table_attr_value_for_where_part(model: 'BaseModel', condition: str,
                                        value: ModelValuesTypes) -> tuple[str, str, Union[int, str]]:
    table, attr = get_table_and_column_for_where_part(model, condition)
    attr, value = process_attr_and_value_for_where_part(model, attr, value)
    return table, attr, value


def get_data_for_where_part_of_sql(model: 'BaseModel',
                                   **kwargs: ModelValuesTypes) -> tuple[str, list[Identifier], list[int, str]]:
    s, identifiers, arguments = [], [], []
    for condition, condition_value in kwargs.items():
        s.append('{}.{} = %s')
        table, attr, condition_value = get_table_attr_value_for_where_part(model, condition, condition_value)
        identifiers += get_identifiers(table, attr)
        arguments.append(condition_value)
    return f'WHERE {" AND ".join(s)}', identifiers, arguments


def get_data_for_set_part_of_sql(model: 'BaseModel') -> tuple[str, list[Identifier], list[Union[int, str]]]:
    attrs, arguments = get_data_to_write_to_db(model)
    s = ', '.join('{} = %s' for _ in range(len(attrs)))
    return f'SET {s}', get_identifiers(*attrs), arguments
