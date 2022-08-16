import datetime
from typing import Union

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


def get_args_for_insert(model: 'BaseModel') -> list[int, str]:
    result = []
    for attr, value in model:
        if attr == 'pk':
            continue
        elif attr in model.related_data:
            value = get_pk_related_entry(value)
        elif isinstance(value, datetime.date):
            value = process_date_for_request(value)
        result.append(value)
    return result
