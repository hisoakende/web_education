from abc import ABC, abstractmethod

from other.utils import ClassOrInstanceProperty
from working_with_models.validators import PasswordValidator, EmailValidator, PersonalDataValidator


class BaseModel(ABC):
    """
    Кроме того, как обязать иметь атрибут 'db_name'
    у дочерних классов, базовый класс представления таблиц нужен,
    чтобы зарегистрировать экземпляр 'TablesManager' в дочерних моделях
    """

    _manager = None

    @ClassOrInstanceProperty
    def manager(self):
        self._manager._work_table = self.db_table
        return self._manager

    @property
    @abstractmethod
    def db_table(self):
        pass


class AbstractUser(BaseModel):
    """Базовое представление пользователя"""

    db_table = 'users'

    first_name = PersonalDataValidator()
    second_name = PersonalDataValidator()
    patronymic = PersonalDataValidator()
    email = EmailValidator()
    password = PasswordValidator()

    def __init__(self, first_name: str, second_name: str, patronymic: str, email: str, password: str) -> None:
        self.first_name = first_name
        self.second_name = second_name
        self.patronymic = patronymic
        self.email = email
        self.password = password

    @property
    @abstractmethod
    def user_type(self):
        pass


class SuperUser(AbstractUser):
    user_type = 'superuser'
