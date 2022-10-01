from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits, punctuation
from typing import Iterable, Any

from other.exceptions import ValidationError
from other.utils import alphabet_ru, get_password_hash


class BaseValidator:

    def __set_name__(self, owner: 'BaseModel', name: str) -> None:
        self.name = name
        self.name_ru = owner.attributes_ru[owner.attributes.index(name) - 1]

    def check_for_characters(self, value: str, characters: Iterable) -> None:
        value = set(value.lower())
        if not value.issubset(characters):
            raise ValidationError(f'Поле \'{self.name_ru}\' содержит недопустимые символы')

    @staticmethod
    def check_for_string(value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('Аргумент должен быть строкой')

    def check_for_range(self, value: int, min_length: int, max_length: int) -> None:
        if value not in range(min_length, max_length + 1):
            raise ValidationError(f'Неккореткное значение поля \'{self.name_ru}\'. '
                                  f'Допустимый диапозон - [{min_length}; {max_length}]')

    def __set__(self, instance: 'BaseModel', value: Any) -> None:
        instance.__dict__[self.name] = value


class PersonalDataValidator(BaseValidator):

    def __set__(self, instance: 'User', value: str) -> None:
        self.check_for_string(value)
        self.check_for_range(len(value), 2, 20)
        self.check_for_characters(value, alphabet_ru)
        super().__set__(instance, value.lower().capitalize())


class EmailValidator(BaseValidator):
    __allowed_characters = ascii_letters + digits + '-.@_'

    @staticmethod
    def check_for_at(value: str) -> None:
        if '@' not in value:
            raise ValidationError('Недопустимый email')

    def __set__(self, instance: 'User', email: str) -> None:
        self.check_for_string(email)
        self.check_for_at(email)
        self.check_for_range(len(email), 3, 256)
        self.check_for_characters(email, self.__allowed_characters)
        super().__set__(instance, email)


class PasswordValidator(BaseValidator):
    __allowed_characters = ascii_letters + digits + punctuation

    @staticmethod
    def check_for_certain_characters(password: str, characters: str) -> None:
        password, characters = set(password), set(characters)
        if not password.intersection(characters):
            raise ValidationError(
                f'В пароле должен присутствовать хотя бы один символ из следующей коллекции: \n {characters}')

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

    def is_hash(self, password: str) -> bool:
        try:
            self.check_for_range(len(password), 64, 64)
        except ValidationError:
            return False
        return True

    def __set__(self, instance: 'User', password: str) -> None:
        if self.is_hash(password):
            hash_ = password
        else:
            self.check_for_string(password)
            self.check_for_range(len(password), 8, 25)
            self.check_for_characters(password, self.__allowed_characters)
            self.check_for_security(password)
            hash_ = get_password_hash(instance.second_name + password + instance.email)
        super().__set__(instance, hash_)


class ClassNumberValidator(BaseValidator):

    def __set__(self, instance: 'Class', number: int) -> None:
        self.check_for_range(number, 1, 11)
        super().__set__(instance, number)


class ClassLetterValidator(BaseValidator):

    @staticmethod
    def check_for_correct_letter(letter: str) -> None:
        if letter.lower() not in list(alphabet_ru):
            raise ValidationError('Неккоректная буква класса')

    def __set__(self, instance: 'Class', letter: str) -> None:
        self.check_for_correct_letter(letter)
        super().__set__(instance, letter.upper())


class SubjectNameValidator(BaseValidator):

    def __set__(self, instance: 'Subject', name: str) -> None:
        self.check_for_range(len(name), 2, 100)
        self.check_for_characters(name, alphabet_ru + ' ')
        super().__set__(instance, name.lower().capitalize())


class GradeValueValidator(BaseValidator):

    def __set__(self, instance: 'Grade', value: int) -> None:
        self.check_for_range(value, 1, 5)
        super().__set__(instance, value)
