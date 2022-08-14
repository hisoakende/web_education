from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Iterable


class BaseValidator:
    _alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    def __set_name__(self, owner: 'BaseModel', name: str) -> None:
        self.name = name

    def check_for_characters(self, value: str, characters: Iterable) -> None:
        value = set(value.lower())
        if not value.issubset(characters):
            raise ValueError(f'Поле {self.name} содержит недопустимые символы')

    @staticmethod
    def check_for_string(value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('Аргумент должен быть строкой')

    def check_for_length(self, value: str, min_length: int, max_length: int) -> None:
        if not (min_length <= len(value) <= max_length):
            raise ValueError(f'Длина поля {self.name} должна находиться '
                             f'в пределах [{min_length}; {max_length}]')


class PersonalDataValidator(BaseValidator):

    def __set__(self, instance: 'AbstractUser', value: str) -> None:
        self.check_for_string(value)
        self.check_for_length(value, 2, 20)
        self.check_for_characters(value, self._alphabet_ru)
        instance.__dict__[self.name] = value.lower().capitalize()


class EmailValidator(BaseValidator):
    __allowed_characters = ascii_letters + digits + '-.@_'

    @staticmethod
    def check_for_at(value: str) -> None:
        if '@' not in value:
            raise ValueError('Недопустимый email')

    def __set__(self, instance: 'AbstractUser', value: str) -> None:
        self.check_for_string(value)
        self.check_for_at(value)
        self.check_for_characters(value, self.__allowed_characters)
        instance.__dict__[self.name] = value


class PasswordValidator(BaseValidator):
    __allowed_characters = ascii_letters + digits + punctuation

    @staticmethod
    def check_for_certain_characters(password: str, characters: str) -> None:
        password, characters = set(password), set(characters)
        if not password.intersection(characters):
            raise ValueError(f'В пароле отсутствует хотя бы один символ из следующей коллекции: \n {characters}')

    def check_for_small_letter(self, password: str) -> None:
        self.check_for_certain_characters(password, ascii_lowercase)

    def check_for_big_letter(self, password: str) -> None:
        self.check_for_certain_characters(password, ascii_uppercase)

    def check_for_digit(self, password: str) -> None:
        self.check_for_certain_characters(password, digits)

    def check_for_special_character(self, password: str) -> None:
        self.check_for_certain_characters(password, punctuation)

    def check_for_security(self, password: str) -> None:
        self.check_for_small_letter(password)
        self.check_for_big_letter(password)
        self.check_for_digit(password)
        self.check_for_special_character(password)

    def __set__(self, instance: 'AbstractUser', value: str) -> None:
        self.check_for_string(value)
        self.check_for_length(value, 8, 25)
        self.check_for_characters(value, self.__allowed_characters)
        self.check_for_security(value)
        instance.__dict__[self.name] = value
