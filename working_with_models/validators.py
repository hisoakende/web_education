from string import ascii_letters, digits
from typing import Iterable


class BaseValidator:
    _alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    def __set_name__(self, owner: 'BaseModel', name: str) -> None:
        self.name = name

    def check_for_characters(self, value: set, characters: Iterable) -> None:
        if not value.issubset(characters):
            raise ValueError(f'Поле {self.name} содержит недопустимые символы')

    @staticmethod
    def check_for_string(value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('Аргумент должен быть строкой')


class PersonalDataValidator(BaseValidator):

    def check_for_length(self, value: str) -> None:
        if len(value) >= 20:
            raise ValueError(f'Поле {self.name} - слишком длинное')

    def __set__(self, instance: 'AbstractUser', value: str) -> None:
        self.check_for_string(value)
        self.check_for_length(value)
        self.check_for_characters(set(value.lower()), self._alphabet_ru)
        instance.__dict__[self.name] = value.lower().capitalize()


class EmailValidator(BaseValidator):
    __allowed_characters = ascii_letters + digits + '-.@_'

    @staticmethod
    def check_for_special_characters(value: str) -> None:
        if '@' not in value:
            raise ValueError('Недопустимый email')

    def __set__(self, instance: 'AbstractUser', value: str):
        self.check_for_string(value)
        self.check_for_special_characters(value)
        self.check_for_characters(set(value.lower()), self.__allowed_characters)
        instance.__dict__[self.name] = value


class PasswordValidator:
    pass
