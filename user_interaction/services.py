import datetime
import enum
from getpass import getpass
from typing import Type, Union

from prettytable import PrettyTable

from other.exceptions import InstanceCantExist
from user_interaction.enums import CreateUser, EnumSchoolClassConstructor, ProfileType
from user_interaction.messages import print_error
from user_interaction.requesting_data_from_user import get_answer, get_choice
from working_with_models.models import Teacher, Student, Class, Administrator, Grade, Period, SubjectClassTeacher, \
    Subject

profiles = {ProfileType.student: Student,
            ProfileType.teacher: Teacher,
            ProfileType.administrator: Administrator}

UserTypes = Union[Teacher, Student, Administrator]

months_ru = ('Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
             'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря')


class State:
    """'Current_dates' - активные даты, с которыми можно работать
    (ставить и просматривать оценки). Например, четверть или полугодие"""
    user = None
    current_dates = None

    def __new__(cls, *args, **kwargs):
        raise InstanceCantExist


def try_to_create_user(model_class: Type[UserTypes], first_name: str, second_name: str,
                       patronymic: str, email: str, password: str, *additional_field: str) -> UserTypes:
    try:
        user = model_class(first_name, second_name, patronymic, email, password, *additional_field)
    except ValueError as exception:
        print_error(f'{exception}')
    else:
        return user


def get_school_class_from_user() -> Class:
    classes = get_classes_to_select()
    classes_enum = create_enum_of_classes(classes)
    classes_msg = get_str_of_classes_for_msg(classes)
    class_pk = get_choice(classes_enum, f'Введите класс:\n{classes_msg}').value
    return Class.manager.get(pk=class_pk)


def get_additional_field(model_class: Type[UserTypes]) -> Union[None, str, Class]:
    if model_class is Teacher:
        return get_answer('Введите информацию об учителе (например: Учитель географии, стаж - 20 лет):')
    elif model_class is Student:
        return get_school_class_from_user()


def try_to_insert_user_to_db(user: UserTypes) -> bool:
    create_user = get_choice(CreateUser)
    if create_user == CreateUser.no:
        return False
    user.manager.create(execution=True)
    return True


def create_dict_with_user_data(model_class: Type[UserTypes]) -> dict[str, str]:
    result = {'first_name': get_answer(f'Введите имя:'),
              'second_name': get_answer(f'Введите фамилию:'),
              'patronymic': get_answer(f'Введите отчество:'),
              'email': get_answer(f'Введите email:'),
              'password': get_answer('Введите пароль:', getpass),
              'repeated_password': get_answer('Повторите пароль:', getpass)}
    if model_class is not Administrator:
        result['additional_field'] = get_additional_field(model_class)
    return result


def get_classes_to_select() -> list[tuple[str, str]]:
    classes = Class.manager.all(execution=True)
    return [(str(cls.number) + cls.letter, str(cls.pk)) for cls in classes]


def get_str_of_classes_for_msg(classes: list[tuple[str, str]]) -> str:
    return '\n'.join(f'[{cls[1]}] - {cls[0]}' for cls in classes)


def create_enum_of_classes(classes: list[tuple[str, str]]) -> Type[enum.Enum]:
    return EnumSchoolClassConstructor('SchoolClassEnum', classes)


def set_current_dates() -> None:
    current_period = Period.manager.get(is_current=True)
    State.current_dates = [current_period.start + datetime.timedelta(dt_dlt) for dt_dlt in
                           range((current_period.finish - current_period.start).days + 1)]


def get_subjects_for_table(subjects: list[Subject]) -> dict[Subject, list]:
    return {subject: [] for subject in subjects}


def get_empty_table_dict(subjects: list[Subject]) -> dict[datetime.date, dict[Subject, list]]:
    return {dt: get_subjects_for_table(subjects) for dt in State.current_dates}


def fill_raw_table_with_grades(table: dict[datetime.date, dict[Subject, list]], grades: list[Grade]) -> None:
    for grade in grades:
        if grade.date not in State.current_dates:
            continue
        table[grade.date][grade.subject].append(str(grade.value))


def get_pretty_table() -> PrettyTable:
    table = PrettyTable()
    table.hrules = 1
    return table


def prepare_pretty_table_for_grades(table: PrettyTable, subjects: list[Subject]) -> None:
    table.field_names = ['Дата'] + [subject.name for subject in subjects]


def prepare_pretty_table_for_tchs_list(table: PrettyTable) -> None:
    table.field_names = ('Предмет', 'Учитель')


def get_fio(user: UserTypes) -> str:
    return f'{user.first_name} {user.second_name} {user.patronymic}'


def fill_pretty_table_with_tchs(table: PrettyTable, teachers_subjects: list[SubjectClassTeacher]) -> None:
    """Заполняет пустую таблицу учителями и предметами"""
    for t_s in teachers_subjects:
        table.add_row([t_s.subject.name, get_fio(t_s.teacher)])


def get_str_grades_for_table(grades: dict[Subject, list]) -> list[str]:
    return ['/'.join(gr) for gr in grades.values()]


def get_str_date_for_table(date: datetime.date) -> str:
    return f'{date.day} {months_ru[date.month - 1]} {date.year}'


def fill_pretty_table_with_grades(raw_table: dict[datetime.date, dict[Subject, list]],
                                  pretty_table: PrettyTable) -> None:
    """Заполняет пустую таблицу оценками"""
    for grade_date, sbj_grades in raw_table.items():
        pretty_table.add_row([get_str_date_for_table(grade_date)] + get_str_grades_for_table(sbj_grades))


def print_class_students(students: list[Student]) -> None:
    for index, student in enumerate(students, 1):
        print(f'{index}. {get_fio(student)}')
