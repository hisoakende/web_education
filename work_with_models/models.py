from abc import ABC, abstractmethod

from other.utils import ClassOrInstanceProperty
from validators import UserNameValidator, EmailValidator, PasswordValidator


class BaseModel(ABC):
    """
    Кроме того, как обязать иметь атрибут 'db_name'
    у дочерних классов, базовый класс представления таблиц нужен,
    чтобы зарегистрировать экземпляр 'TablesManager' в дочерних классах
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
    username = UserNameValidator()
    email = EmailValidator()
    password = PasswordValidator()

    def __init__(self, username: str, email: str, password: str) -> None:
        self.username = username
        self.email = email
        self.password = password

    @property
    @abstractmethod
    def user_type(self):
        pass


class SuperUser(AbstractUser):
    user_type = 'superuser'
