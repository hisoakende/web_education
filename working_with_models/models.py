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
    attributes = ('pk',)
    related_data = {}

    def __init__(self) -> None:
        self.pk = None

    def __iter__(self) -> Generator[tuple[str, Any], None, None]:
        for key, value in self.__dict__.items():
            yield key, value

    def __repr__(self):
        s = ', '.join(f'{attr}: {value}' for attr, value in self)
        return f'{self.__class__.__name__}({s})'

    def __eq__(self, other):
        return hash(self) == hash(other)

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

    attributes = BaseModel.attributes + ('first_name', 'second_name', 'patronymic', 'email', 'password')
    attributes_ru = ('имя', 'фамилия', 'отчество', 'email', 'пароль')

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

    def __str__(self):
        return f'{self.second_name} {self.first_name[0]}. {self.patronymic[0]}.'


class Teacher(User, BaseModel):
    """
    Модель школьного учителя. Между таблицами 'teachers' и 'classes', 'teachers' и 'subjects'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'teachers'
    attributes = User.attributes + ('about_person', 'is_active')
    attributes_ru = User.attributes_ru + ('об учителе', 'активный ли учитель')
    name_ru = 'учитель'

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, about_person: str, is_active: bool = False) -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.about_person = about_person
        self.is_active = is_active


class Class(BaseModel):
    """
    Модель школьного класса. Между таблицами 'classes' и 'teachers', 'classes' и 'subjects'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'classes'
    attributes = BaseModel.attributes + ('number', 'letter', 'classroom_teacher')
    attributes_ru = ('номер', 'буква', 'классный руководитель')
    related_data = {'classroom_teacher': Teacher}
    name_ru = 'класс'

    number = ClassNumberValidator()
    letter = ClassLetterValidator()

    def __init__(self, number: int, letter: str, classroom_teacher: Union[pk_obj, Teacher]) -> None:
        super().__init__()
        self.number = number
        self.letter = letter
        self.classroom_teacher = classroom_teacher

    def __str__(self) -> str:
        return str(self.number) + self.letter


class Student(User, BaseModel):
    """Модель ученика. Ученик может просматривать учителей, которые ведут у него занятия, а также свои оценки"""

    db_table = 'students'
    attributes = User.attributes + ('school_class', 'is_active')
    attributes_ru = User.attributes_ru + ('класс', 'активный ли ученик')
    related_data = {'school_class': Class}
    name_ru = 'ученик'

    def __init__(self, first_name: str, second_name: str, patronymic: str,
                 email: str, password: str, school_class: Union[pk_obj, 'Class'], is_active: bool = False) -> None:
        super().__init__(first_name, second_name, patronymic, email, password)
        self.school_class = school_class
        self.is_active = is_active

    def __hash__(self) -> int:
        return hash(self.email)


class Administrator(User, BaseModel):
    """
    Модель администратора. Администратор добавляет в систему учителей/учеников,
    может создавать классы, просматривать оценки любого ученика и ставить их ему и т.д.
    """

    db_table = 'administrators'
    attributes = User.attributes
    name_ru = 'администратор'


class Subject(BaseModel):
    """
    Модель школьного предмета. Между таблицами 'subjects' и 'teachers', 'subjects' и 'classes'
    связь многие-ко-многим. В коде модели это никак не отражено
    """

    db_table = 'subjects'
    attributes = BaseModel.attributes + ('name',)
    attributes_ru = ('название',)
    name_ru = 'предмет'

    name = SubjectNameValidator()

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class Grade(BaseModel):
    """Модель школьной оценки"""

    db_table = 'grades'
    attributes = BaseModel.attributes + ('value', 'student', 'subject', 'date')
    attributes_ru = ('значение', 'ученик', 'предмет', 'дата')
    related_data = {'student': Student, 'subject': Subject}
    name_ru = 'оценка'

    value = GradeValueValidator()

    def __init__(self, value: int, student: Union[pk_obj, Student], subject: Union[pk_obj, Subject],
                 date: datetime.date = datetime.date.today()) -> None:
        super().__init__()
        self.value = value
        self.student = student
        self.subject = subject
        self.date = date


class Period(BaseModel):
    """Период успеваемости. Например, четверть или полугодие"""

    db_table = 'periods'
    attributes = BaseModel.attributes + ('start', 'finish', 'is_current')
    attributes_ru = ('начальная дата', 'конечная дата', 'текущий ли период')
    name_ru = 'период успеваемости'

    def __init__(self, start: datetime.date, finish: datetime.date, is_current: bool = False) -> None:
        super().__init__()
        self.start = start
        self.finish = finish
        self.is_current = is_current

    def __str__(self) -> str:
        return f'{self.start}/{self.finish}'


class SubjectClassTeacher(BaseModel):
    """Связка учителя, предмета, который он преподает, и класса, у которого он ведет этот предмет"""

    db_table = 'subject_class_teacher'
    attributes = BaseModel.attributes + ('subject', 'school_class', 'teacher')
    attributes_ru = ('предмет', 'класс', 'учитель')
    related_data = {'subject': Subject, 'school_class': Class, 'teacher': Teacher}
    name_ru = 'связка предмет-класс-учитель'

    def __init__(self, subject: Union[pk_obj, Subject],
                 school_class: Union[pk_obj, Class], teacher: Union[pk_obj, Teacher]) -> None:
        super().__init__()
        self.subject = subject
        self.school_class = school_class
        self.teacher = teacher
