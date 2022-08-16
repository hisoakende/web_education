import datetime
from abc import ABC, abstractmethod
from typing import Generator, Any

from other.utils import ClassOrInstanceProperty
from working_with_models.validators import PasswordValidator, EmailValidator, PersonalDataValidator, \
    ClassNumberValidator, ClassLetterValidator, SubjectNameValidator, GradeValueValidator


class BaseModel(ABC):
    """
    Кроме того, как обязать иметь атрибут 'db_table'
    у дочерних классов, базовый класс представления таблиц нужен,
    чтобы зарегистрировать экземпляр 'TablesManager' в дочерних моделях
    """

    _manager = None
    related_data = ()

    def __init__(self) -> None:
        self.pk = None

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        for key, value in self.__dict__.items():
            yield key, value

    @ClassOrInstanceProperty
    def manager(self) -> 'TablesManager':
        self._manager._model = self
        return self._manager

    @property
    @abstractmethod
    def db_table(self):
        pass


class User:
    """Базовое представление пользователя"""

    first_name = PersonalDataValidator()
    second_name = PersonalDataValidator()
    patronymic = PersonalDataValidator()
    email = EmailValidator()
    password = PasswordValidator()

    def __init__(self, first_name: str, second_name: str,
                 patronymic: str, email: str, password: str) -> None:
        super().__init__()
        self.first_name = first_name
        self.second_name = second_name
        self.patronymic = patronymic
        self.email = email
        self.password = password


class Student(User, BaseModel):
    db_table = 'students'
    related_data = ('class_',)

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, class_: 'Class') -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.class_ = class_


class Class(BaseModel):
    """Модель школьного класса"""

    db_table = 'classes'
    related_data = ('classroom_teacher', 'teachers', 'subjects')
    number = ClassNumberValidator()
    letter = ClassLetterValidator()

    def __init__(self, number: int, letter: str, classroom_teacher: 'Teacher',
                 teachers: list['Teacher'], subjects: list['Subject']) -> None:
        super().__init__()
        self.number = number
        self.letter = letter
        self.classroom_teacher = classroom_teacher
        self.teachers = teachers
        self.subjects = subjects


class Teacher(User, BaseModel):
    db_table = 'teachers'
    related_data = ('subjects', 'classes')

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, about_person: str,
                 subjects: list['Subject'], classes: list[Class]) -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.about_person = about_person
        self.subjects = subjects
        self.classes = classes


class Administrator(User, BaseModel):
    db_table = 'administrators'


class Subject(BaseModel):
    db_table = 'subjects'
    related_data = ('teachers', 'classes')
    name = SubjectNameValidator()

    def __init__(self, name: str, teachers: list[Teacher], classes: list[Class]) -> None:
        super().__init__()
        self.name = name
        self.teachers = teachers
        self.classes = classes


class Grade(BaseModel):
    db_table = 'grades'
    related_data = ('student', 'subject', 'teacher')
    value = GradeValueValidator()

    def __init__(self, value: int, student: Student,
                 subject: Subject, teacher: Teacher,
                 date: datetime.date = datetime.date.today()) -> None:
        super().__init__()
        self.value = value
        self.student = student
        self.subject = subject
        self.teacher = teacher
        self.date = date
