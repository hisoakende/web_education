import datetime
from abc import ABC, abstractmethod
from typing import Generator, Any, Union

from other.utils import ClassOrInstanceProperty
from working_with_models.validators import EmailValidator, PersonalDataValidator, \
    ClassNumberValidator, ClassLetterValidator, SubjectNameValidator, GradeValueValidator, PasswordValidator

pk_obj = int


class BaseModel(ABC):
    """Базовый класс модели"""

    _manager = None
    attributes = ['pk']
    related_data = {}

    def __init__(self) -> None:
        self.pk = None

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        for key, value in self.__dict__.items():
            yield key, value

    def __repr__(self):
        s = ', '.join(f'{attr}: {value}' for attr, value in self)
        return f'{self.__class__.__name__}({s})'

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

    attributes = ['first_name', 'second_name', 'patronymic', 'email', 'password']

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


class Teacher(User, BaseModel):
    """
    Модель школьного учителя. Между таблицами 'teachers' и 'classes', 'teachers' и 'subjects'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'teachers'
    attributes = BaseModel.attributes + User.attributes + ['about_person']

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, about_person: str) -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.about_person = about_person


class Class(BaseModel):
    """
    Модель школьного класса. Между таблицами 'classes' и 'teachers', 'classes' и 'subjects'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'classes'
    attributes = BaseModel.attributes + ['number', 'letter', 'classroom_teacher']
    related_data = {'classroom_teacher': Teacher}
    number = ClassNumberValidator()
    letter = ClassLetterValidator()

    def __init__(self, number: int, letter: str, classroom_teacher: Union[pk_obj, Teacher]) -> None:
        super().__init__()
        self.number = number
        self.letter = letter
        self.classroom_teacher = classroom_teacher


class Student(User, BaseModel):
    db_table = 'students'
    attributes = BaseModel.attributes + User.attributes + ['school_class']
    related_data = {'school_class': Class}

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, school_class: Union[pk_obj, 'Class']) -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.school_class = school_class


class Administrator(User, BaseModel):
    db_table = 'administrators'
    attributes = BaseModel.attributes + User.attributes


class Subject(BaseModel):
    """
    Модель школьного предмета. Между таблицами 'subjects' и 'teachers', 'subjects' и 'classes'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'subjects'
    attributes = BaseModel.attributes + ['name']
    name = SubjectNameValidator()

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name


class Grade(BaseModel):
    db_table = 'grades'
    attributes = BaseModel.attributes + ['value', 'student', 'subject', 'teacher', 'date']
    related_data = {'student': Student, 'subject': Subject, 'teacher': Teacher}
    value = GradeValueValidator()

    def __init__(self, value: int, student: Union[pk_obj, Student],
                 subject: Union[pk_obj, Subject], teacher: Union[pk_obj, Teacher],
                 date: datetime.date = datetime.date.today()) -> None:
        super().__init__()
        self.value = value
        self.student = student
        self.subject = subject
        self.teacher = teacher
        self.date = date
