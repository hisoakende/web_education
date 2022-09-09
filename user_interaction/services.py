import datetime
from getpass import getpass
from typing import Type, Union, Literal

from prettytable import PrettyTable

from other.exceptions import InstanceCantExist
from user_interaction.enums import CreateUser, EnumSchoolClassConstructor, ProfileType, EnumSubjectConstructor
from user_interaction.messages import print_error, separate_action
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
    """'
    Current_dates' - активные даты, с которыми можно работать
    (ставить и просматривать оценки). Например, четверть или полугодие
    Такая изначальная структура 'cache' нужна для корректной работы функции,
    соотносящий первичный ключ ученика и его порядковый номер в классе
    """

    user = None
    current_dates = None
    cache = {'students_pks': {0: None}}

    def __new__(cls, *args, **kwargs):
        raise InstanceCantExist

    @classmethod
    def clear_cache(cls):
        cls.cache = {'students_pks': {0: None}}


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
    classes_enum = EnumSchoolClassConstructor('SchoolClassEnum', classes)
    choices_msg = get_str_of_choices(classes)
    class_pk = get_choice(classes_enum, f'Введите класс:\n{choices_msg}').value
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


def get_str_of_choices(objs: list[tuple[str, str]]) -> str:
    return '\n'.join(f'[{obj[1]}] - {obj[0]}' for obj in objs)


def set_current_dates() -> None:
    current_period = Period.manager.get(is_current=True)
    State.current_dates = [current_period.start + datetime.timedelta(dt_dlt) for dt_dlt in
                           range((current_period.finish - current_period.start).days + 1)]


def set_columns_in_table(objs: list[Union[Subject, Student]]) -> dict[Union[Subject, Student], list]:
    return {obj: [] for obj in objs}


def get_empty_table_dict(objs: list[Union[Subject, Student]]) \
        -> dict[datetime.date, dict[Union[Subject, Student], list]]:
    """
    Получить представление пустой таблицы (без оценок; таблица либо для учителя
    со строками в виде дат и столбцами в виде учеников, либо для ученика со строками
    в виде дат и столбацми в виде учебных предметов) в виде словаря
    """
    return {dt: set_columns_in_table(objs) for dt in State.current_dates}


def fill_raw_table_with_grades(table: dict[datetime.date, dict[Subject, list]],
                               grades: list[Grade], attr: Literal['subject', 'student']) -> None:
    for grade in grades:
        if grade.date not in State.current_dates:
            continue
        table[grade.date][getattr(grade, attr)].append(str(grade.value))


def get_pretty_table() -> PrettyTable:
    table = PrettyTable()
    table.hrules = 1
    return table


def get_prepared_students_field_names_view(raw_students: list[Student]) -> list[str]:
    """
    Сохраняет соотношение порядкового номера ученика в классе (1, 2, 3, ...) и первичного ключа.
    Обрабтывает представление ученика в названии столбца.
    """
    prepared_students = []
    last_index = max(State.cache['students_pks'].keys())
    for index in range(len(raw_students)):
        prepared_students.append(f'{last_index + index + 1}: {str(raw_students[index])}')
        State.cache['students_pks'][last_index + index + 1] = raw_students[index].pk
    return prepared_students


def prepare_pretty_table_for_grades(table: PrettyTable, objs: list[Union[Subject, Student]]) -> None:
    if isinstance(objs[0], Student):
        objs = get_prepared_students_field_names_view(objs)
    table.field_names = ['-'] + objs


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


def get_subjects_to_select(subjects: list[Subject]) -> list[tuple[str, str]]:
    return [(subject.name, str(subject.pk)) for subject in subjects]


def get_subject_from_user(subjects: list[Subject]) -> Subject:
    """Позволяет получить школьный предмет, который выбрал пользователь"""

    subjects_to_select = get_subjects_to_select(subjects)
    subjects_enum = EnumSubjectConstructor('SubjectEnum', subjects_to_select)
    choices_msg = get_str_of_choices(subjects_to_select)
    subject_pk = get_choice(subjects_enum, f'Выберете класс:\n{choices_msg}').value
    return Subject.manager.get(pk=subject_pk)


def get_table_with_students_grades_for_print(students: list[Student], subject: Subject) -> PrettyTable:
    """Возвращает таблицу (или часть таблицы) с оценками учеников для вывода в консоль"""

    pretty_table = get_pretty_table()
    prepare_pretty_table_for_grades(pretty_table, students)
    raw_table = get_empty_table_dict(students)
    grades = Grade.manager.filter(teacher=State.user, subject=subject)
    grades = list(filter(lambda grade: grade.student in students, grades))
    fill_raw_table_with_grades(raw_table, grades, 'student')
    fill_pretty_table_with_grades(raw_table, pretty_table)
    return pretty_table


def print_class_grades() -> None:
    """Печатает все оценки, полученные учениками определеннего класса по определенному предмету"""

    school_class = get_school_class_from_user()
    students = sorted(Student.manager.filter(school_class=school_class), key=lambda st: st.second_name)
    subjects = list(map(lambda x: x.subject, SubjectClassTeacher.manager.filter(teacher=State.user)))
    subject = get_subject_from_user(subjects)
    for index in range(0, len(students), 7):
        students_part = students[index: index + 7]
        table = get_table_with_students_grades_for_print(students_part, subject)
        separate_action()
        print(table)
