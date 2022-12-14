import datetime
from getpass import getpass
from string import digits
from typing import Type, Union, Literal, Callable, Optional, Any

import psycopg2.errors
from prettytable import PrettyTable

from other.exceptions import InstanceCantExist, InvalidData, ValidationError, \
    NoSubjectsTaughtByTheTeacher, SemanticCommandError, ExitGradingCommand, InvalidDate, NoObjsToChooseFrom
from other.utils import ModelValuesTypes
from user_interaction.enums import EnumConstructor, ProfileType, SaveChanges, WhatToDoWithGrades
from user_interaction.messages import print_error, separate_action, print_grading_instruction, preliminary_grades_msg, \
    print_objs_for_the_user_to_select, what_to_do_with_grades_msg, delete_obj_msg, warning_before_deletion_msg
from user_interaction.requesting_data_from_user import get_answer, get_choice, request_data
from working_with_models.models import Teacher, Student, Class, Administrator, Grade, Period, SubjectClassTeacher, \
    Subject, User, BaseModel

profiles = {ProfileType.student: Student,
            ProfileType.teacher: Teacher,
            ProfileType.administrator: Administrator}

models_for_admin_work = Union[Teacher, Student, Class, Subject, Period, SubjectClassTeacher]
model_classes_for_admin_work = Type[models_for_admin_work]

UserTypes = Union[Teacher, Student, Administrator]

months_ru = ('Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня',
             'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря')

dependent_models = {Teacher: (Class, SubjectClassTeacher, Grade), Class: (SubjectClassTeacher, Student),
                    Subject: (SubjectClassTeacher, Grade), Student: (Grade,)}


class State:
    """
    'Current_dates' - активные даты, с которыми можно работать
    (ставить и просматривать оценки). Например, четверть или полугодие
    Такая изначальная структура 'cache' нужна для корректной работы функции,
    которая соотносит ученика и его порядковый номер в классе (1, 2, 3 и т.д.)
    """

    db = None
    cache = {'students': [None]}
    user = None
    current_dates = None

    def __new__(cls, *args, **kwargs):
        raise InstanceCantExist

    @classmethod
    def clear_cache(cls):
        cls.cache = {'students': [None]}


def try_to_create_obj(model_class: Type[BaseModel], *args: ModelValuesTypes) -> Optional[BaseModel]:
    try:
        user = model_class(*args)
    except ValidationError as exception:
        print_error(f'{exception}')
    else:
        return user


def get_obj_from_user(objs: list, obj_name_str: str) -> Any:
    if not objs:
        raise NoObjsToChooseFrom('Нет объектов для выбора')
    objs_enum = EnumConstructor('ObjsEnum', [(repr(c), str(i)) for i, c in enumerate(objs, 1)])
    print_objs_for_the_user_to_select(obj_name_str, objs)
    obj_number = get_choice(objs_enum).value
    return objs[int(obj_number) - 1]


def get_additional_field(model_class: Type[User]) -> Union[None, str, Class]:
    if model_class is Teacher:
        return get_answer('Введите информацию об учителе (например: Учитель географии, стаж - 20 лет):')
    elif model_class is Student:
        classes = Class.manager.all()
        return get_obj_from_user(classes, 'класс')


def try_to_insert_obj_to_db(obj: BaseModel, method: Literal['save', 'create']) -> bool:
    if get_choice(SaveChanges) is SaveChanges.no:
        return False
    getattr(getattr(obj, 'manager'), method)(execution=True)
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


def set_current_dates_to_state(current_period: Period) -> None:
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
    Сохраняет соотношение порядкового номера ученика в классе (1, 2, 3, ...) и самого ученика.
    Обрабтывает представление ученика в названии столбца.
    """
    prepared_students = []
    last_index = len(State.cache['students']) - 1
    for index in range(len(raw_students)):
        prepared_students.append(f'{last_index + index + 1}: {str(raw_students[index])}')
        State.cache['students'].append(raw_students[index])
    return prepared_students


def prepare_pretty_table_for_grades(table: PrettyTable, objs: list[Union[Subject, Student]]) -> None:
    if isinstance(objs[0], Student):
        objs = get_prepared_students_field_names_view(objs)
    table.field_names = ['-'] + objs


def prepare_pretty_table_for_tchs_list(table: PrettyTable) -> None:
    table.field_names = ('Предмет', 'Учитель')


def get_fio(user: User) -> str:
    return f'{user.second_name} {user.first_name} {user.patronymic}'


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


def get_table_with_students_grades_for_print(students: list[Student], subject: Subject) -> PrettyTable:
    """Возвращает таблицу (или часть таблицы) с оценками учеников для вывода в консоль"""

    pretty_table = get_pretty_table()
    prepare_pretty_table_for_grades(pretty_table, students)
    raw_table = get_empty_table_dict(students)
    grades = Grade.manager.filter(subject=subject)
    grades = list(filter(lambda grade: grade.student in students, grades))
    fill_raw_table_with_grades(raw_table, grades, 'student')
    fill_pretty_table_with_grades(raw_table, pretty_table)
    return pretty_table


def print_class_grades_table(school_class: Class, subject: Subject) -> None:
    """Печатает все оценки, полученные учениками определеннего класса по определенному предмету"""

    students = sorted(Student.manager.filter(school_class=school_class, is_active=True), key=lambda st: st.second_name)
    for index in range(0, len(students), 7):
        students_part = students[index: index + 7]
        table = get_table_with_students_grades_for_print(students_part, subject)
        separate_action()
        print(table)


def validate_command_chars(command: str) -> None:
    for character in command:
        if character not in ':(/),; ' + digits:
            raise InvalidData('Содержатся недопустимые символы')


def validate_command_parts(command: list[str]) -> None:
    if not all(command):
        raise InvalidData('Недопустимая форма')


def validate_command_form(cmd: str) -> None:
    if cmd.count(':') + cmd.count('(') + cmd.count('/') + cmd.count(')') < 5:
        raise InvalidData('Недопустимая форма')


def get_student_from_grading_command(user_number: int) -> Student:
    """Возвращает ученика, которому ставится оценка"""
    if len(State.cache['students']) > user_number > 0:
        return State.cache['students'][user_number]
    raise InvalidData('Неверный номер студента')


def validate_grade_and_date(grade_and_date: list[str]) -> None:
    if len(grade_and_date) != 4:
        raise InvalidData('Недопустимый формат оценки или даты')


def check_location_of_special_chars_in_date(date: str) -> None:
    if date.index(')') > date.index('/') > date.index('('):
        return
    raise InvalidDate('Недопустимый формат даты')


def check_number_of_special_chars_in_date(date: str) -> None:
    if date.count('/') != 2 or date.count('(') != 1 or date.count(')') != 1:
        raise InvalidDate('Недопустимый формат даты')


def check_date_in_current_period(date: datetime.date) -> None:
    if date not in State.current_dates:
        raise InvalidDate('Недопустимая дата')


def split_grade_and_date(grade_and_date: str) -> tuple[int, list[int]]:
    check_number_of_special_chars_in_date(grade_and_date)
    check_location_of_special_chars_in_date(grade_and_date)
    grade_and_date = grade_and_date.replace('(', ' ').replace('/', ' ').replace(')', ' ').split()
    validate_grade_and_date(grade_and_date)
    grade_value = int(grade_and_date[0])
    date = list(map(int, grade_and_date[1:][::-1]))
    return grade_value, date


def process_part_of_one_student_command(part: str) -> tuple[Student, list[str]]:
    user_number_and_grades = part.split(':')
    validate_command_parts(user_number_and_grades)
    student = get_student_from_grading_command(int(user_number_and_grades[0]))
    grades_and_dates = user_number_and_grades[1].split(',')
    validate_command_parts(grades_and_dates)
    return student, grades_and_dates


def create_date_from_command_values(date: list[int]) -> datetime.date:
    try:
        return datetime.date(*date)
    except ValueError:
        raise InvalidDate


def create_grade_from_grading_command(grade_and_date: str, student: Student, subject: Subject) -> Grade:
    grade_value, date = split_grade_and_date(grade_and_date)
    date = create_date_from_command_values(date)
    check_date_in_current_period(date)
    return Grade(grade_value, student, subject, date)


def get_user_and_his_grades_from_command(part: str, subject: Subject) -> tuple[Student, list[Grade]]:
    student, grades_and_dates = process_part_of_one_student_command(part)
    parsed_grades = [create_grade_from_grading_command(gr_and_dt, student, subject) for gr_and_dt in grades_and_dates]
    return student, parsed_grades


def grading_command_preprocessing(command: str) -> list[str]:
    validate_command_chars(command)
    validate_command_form(command)
    command = command.replace(' ', '')
    parts_by_users = command.split(';')
    validate_command_parts(parts_by_users)
    return parts_by_users


def parse_student_grading_command(command: str, subject: Subject) -> list[tuple[Student, list[Grade]]]:
    """Функция, обрабатывающая команду выставления оценки"""
    parts_by_users = grading_command_preprocessing(command)
    parsed_data = [get_user_and_his_grades_from_command(part, subject) for part in parts_by_users]
    return parsed_data


def process_grading_command(command: str, subject: Subject) -> Union[None, list[tuple[Student, list[Grade]]]]:
    try:
        st_and_gr = parse_student_grading_command(command, subject)
    except (InvalidData, InvalidDate, ValidationError) as e:
        if isinstance(e, ValidationError):
            e = 'Недопустимое значение оценки'
        print_error(f'Неккоректная команда! {e}')
        return
    return st_and_gr


@request_data(None)
def get_preliminary_grades(subject: Subject) -> Union[None, list[tuple[Student, list[Grade]]]]:
    """Запрашивает команду выставления оценок и возвращает предварительные оценки"""
    student_grading_command = get_answer()
    if student_grading_command == '-2':
        raise ExitGradingCommand
    return process_grading_command(student_grading_command, subject)


def get_data_to_rate_students(teacher: Optional[Teacher] = None) -> tuple[Class, Subject]:
    if teacher is None:
        s_c_t = SubjectClassTeacher.manager.all()
    else:
        s_c_t = SubjectClassTeacher.manager.filter(teacher=teacher)
    if not s_c_t:
        raise NoSubjectsTaughtByTheTeacher
    classes = get_unique_elements(get_objs_from_sct(s_c_t, 'school_class'))
    school_class = get_obj_from_user(classes, 'класс')
    subjects = [el.subject for el in s_c_t if el.school_class.pk is school_class.pk]
    subjects = get_unique_elements(subjects)
    subject = get_obj_from_user(subjects, 'предмет')
    return school_class, subject


def get_unique_elements(objs: list[BaseModel]) -> list[BaseModel]:
    pks, result = [], []
    for obj in objs:
        if obj.pk in pks:
            continue
        result.append(obj)
        pks.append(obj.pk)
    return result


def save_grades_from_grading_command(preliminary_grades: list[tuple[Student, list[Grade]]]) -> None:
    iterate_over_preliminary_grades(preliminary_grades, lambda gr: gr.manager.create())


def iterate_over_preliminary_grades(preliminary_grades: list[tuple[Student, list[Grade]]], func: Callable) -> None:
    for user_and_his_grades in preliminary_grades:
        for grade in user_and_his_grades[1]:
            func(grade)


def remove_one_grade_from_grading_command(grade: Grade) -> None:
    grades = Grade.manager.filter(value=grade.value, student=grade.student, subject=grade.subject, date=grade.date)
    if not grades:
        raise SemanticCommandError
    grades[0].manager.delete()


def remove_grades_from_grading_command(preliminary_grades: list[tuple[Student, list[Grade]]]) -> None:
    iterate_over_preliminary_grades(preliminary_grades, remove_one_grade_from_grading_command)


what_to_do_with_grades_choices = {WhatToDoWithGrades.add: (save_grades_from_grading_command, 'добавление'),
                                  WhatToDoWithGrades.remove: (remove_grades_from_grading_command, 'удаление')}


def get_what_to_do_with_grades_choice() -> WhatToDoWithGrades:
    what_to_do_with_grades_choice = get_choice(WhatToDoWithGrades, what_to_do_with_grades_msg)
    if what_to_do_with_grades_choice is WhatToDoWithGrades.nothing:
        raise ExitGradingCommand
    return what_to_do_with_grades_choice


def get_save_change_choice() -> bool:
    save_changes_choice = get_choice(SaveChanges)
    if save_changes_choice == SaveChanges.no:
        return False
    return True


def process_student_grading(school_class: Class, subject: Subject) -> None:
    """Оценивание студента"""
    while True:
        State.clear_cache()
        print_class_grades_table(school_class, subject)
        while True:
            try:
                what_to_do_with_grades_choice = get_what_to_do_with_grades_choice()
                print_grading_instruction()
                preliminary_grades = get_preliminary_grades(subject)
            except ExitGradingCommand:
                return
            try:
                what_to_do_with_grades_choices[what_to_do_with_grades_choice][0](preliminary_grades)
            except SemanticCommandError:
                print_error('Неверный смысл команды!\n')
                continue
            preliminary_grades_msg(preliminary_grades, what_to_do_with_grades_choices[what_to_do_with_grades_choice][1])
            if not get_save_change_choice():
                continue
            State.db.execute_transaction()
            break


def get_objs_from_sct(raw_objs: list[SubjectClassTeacher], model: str) -> list[Union[Subject, Class, Teacher]]:
    """Возвращает конкректные объекты ('Subject', 'Class', 'Teacher'). sct - subject_class_teacher"""
    return [getattr(obj, model) for obj in raw_objs]


def get_noun_form(attr: str) -> str:
    if attr == 'учитель':
        return 'учителя'
    elif attr == 'классный руководитель':
        return 'классного руководителя'
    return attr


def process_value_from_admin_to_change_obj(value: Union[str, BaseModel], attr: str,
                                           model_class: Type[BaseModel]) -> Union[BaseModel, int, datetime.date, str]:
    if not isinstance(value, str):
        return value
    elif value.isdigit() and attr == 'number':
        return int(value)
    elif attr in ('start', 'finish') and model_class is Period:
        check_number_of_special_chars_in_date(value)
        check_location_of_special_chars_in_date(value)
        date = list(map(int, value.replace('(', ' ').replace('/', ' ').replace(')', ' ').split()[::-1]))
        return create_date_from_command_values(date)
    return value


def request_value_to_create_obj_by_admin(model_class: Type[BaseModel], attr_en: str,
                                         attr_ru: str) -> Union[BaseModel, str, None]:
    if attr_en in model_class.related_data:
        related_model = model_class.related_data[attr_en]
        related_objs = get_all_objects_for_any_model(related_model)
        if not related_objs:
            raise NoObjsToChooseFrom('Нет зависимых объектов для выбора')
        related_model_str_ru = get_noun_form(attr_ru)
        return get_obj_from_user(related_objs, related_model_str_ru)
    elif attr_en == 'password':
        return get_answer(f'Введите поле \'{attr_ru}\':', getpass)
    elif attr_en == 'is_current':
        return
    return get_answer(f'Введите поле \'{attr_ru}\':')


def try_to_add_value_to_list_to_create_obj_by_admin(data: list[Union[BaseModel, int, datetime.date, str]],
                                                    value: Union[str, BaseModel],
                                                    attr_en: str,
                                                    model_class: Type[BaseModel]) -> None:
    try:
        data.append(process_value_from_admin_to_change_obj(value, attr_en, model_class))
    except InvalidDate as e:
        raise InvalidData(str(e))


def get_values_to_create_obj_by_admin(model_class: Type[BaseModel]) -> list[Union[BaseModel, int, datetime.date, str]]:
    data = []
    for attr_en, attr_ru in zip(model_class.attributes[1:], model_class.attributes_ru):
        value = request_value_to_create_obj_by_admin(model_class, attr_en, attr_ru)
        if value is None:
            continue
        try_to_add_value_to_list_to_create_obj_by_admin(data, value, attr_en, model_class)
    return data


def finish_registration(user: User) -> Optional[User]:
    try:
        is_created_user = try_to_insert_obj_to_db(user, 'create')
    except psycopg2.errors.UniqueViolation:
        print_error('Аккаунт такого типа с данным email уже существует')
        return
    if is_created_user:
        return user


def finish_deleting_object(obj: models_for_admin_work) -> None:
    delete_obj_choice = get_choice(SaveChanges, delete_obj_msg)
    if delete_obj_choice is SaveChanges.yes:
        obj.manager.delete(execution=True)
        print('Объект удален')
    else:
        print('Объект не удален')


def warn_user_about_dependent_models(model_class: Union[Teacher, Class, Subject, Student]) -> None:
    warning_before_deletion_msg()
    for i, dependent_obj in enumerate(dependent_models[model_class], 1):
        print(f'{i}) \'{dependent_obj.name_ru}\'')
    print()


def get_obj_from_user_for_admin_work(model_class: model_classes_for_admin_work,
                                     msg: str) -> Union[models_for_admin_work, None]:
    objs = get_all_objects_for_any_model(model_class)
    if not objs:
        print(msg)
        return
    return get_obj_from_user(objs, 'объект')


def get_attrs_to_change(obj: BaseModel) -> dict[str, str]:
    attrs_to_change = {}
    for attr_en, attr_ru in zip(obj.attributes[1:], obj.attributes_ru):
        if attr_en in ('pk', 'is_current'):
            continue
        attrs_to_change[f'{attr_ru} (текущее значение - \'{getattr(obj, attr_en)})\''] = attr_en
    return attrs_to_change


def get_all_objects_for_any_model(model_class: Type[BaseModel]) -> list[BaseModel]:
    if model_class in (Student, Teacher):
        return model_class.manager.filter(is_active=True)
    return model_class.manager.all()
