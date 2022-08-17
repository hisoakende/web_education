import datetime
from typing import Union

from psycopg2.sql import Identifier, Composed, SQL

from other.data_structures import DataForCreateRequest
from other.exceptions import ManyInstanceOfClassError

alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'


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
    """Возвращает данные для создания SQL запроса"""
    columns, arguments = [], []
    for attr, value in model:
        if attr == 'pk':
            continue
        elif attr in model.related_data:
            value = get_pk_related_entry(value)
        elif isinstance(value, datetime.date):
            value = process_date_for_request(value)
        arguments.append(value)
        columns.append(attr)
    return DataForCreateRequest(columns, arguments)


def get_strings_for_sql(count: int) -> list[str]:
    """Возващает строки видов '{}, {}, {}' и '%s, %s, %s' для создания SQL запроса"""
    r = [', '.join(s for _ in range(count)) for s in ('{}', '%s')]
    return r


def get_identifiers_for_request(columns: list[str]) -> list[Identifier]:
    return [Identifier(column) for column in columns]


def get_sql_insert_for_request(columns_sql: str, arguments_sql: str,
                               identifiers: list[Identifier]) -> Composed:
    return SQL('INSERT INTO {} ' + f'({columns_sql})' + f' VALUES ({arguments_sql})').format(*identifiers)
