from typing import Optional

import psycopg2.errors

from other.utils import get_password_hash
from user_interaction.messages import profile_type_msg, create_user_with_this_data_msg
from user_interaction.services import *
from user_interaction.services import create_dict_with_user_data, try_to_create_user, profiles, try_to_insert_user_to_db
from working_with_models.models import User, SubjectClassTeacher, Grade


@request_data('Неправильный email или пароль\nПовторите процедуру аутентификации еще раз\n')
def authenticate_user() -> Union[None, User]:
    """Аутентификация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    email = get_answer('Введите email:')
    password = get_answer('Введите пароль:', getpass)
    model_class = profiles[type_profile]
    user = model_class.manager.get(email=email)
    if user and user.password == get_password_hash(user.second_name + password + user.email):
        return user


def finish_registration(user: User) -> Union[None, User]:
    try:
        is_created_user = try_to_insert_user_to_db(user)
    except psycopg2.errors.UniqueViolation:
        print_error('Аккаунт такого типа с данным email уже существует')
        return
    if is_created_user:
        return user
    return register_user()


@request_data('Повторите процедуру регистрации еще раз\n')
def register_user() -> Union[None, User]:
    """Регистрация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    model_class = profiles[type_profile]
    data = create_dict_with_user_data(model_class)
    if data['password'] != data['repeated_password']:
        print_error('Введенные пароли не совпадают')
        return
    data.pop('repeated_password')
    user = try_to_create_user(model_class, *data.values())
    if user is None:
        return
    data.pop('password')
    create_user_with_this_data_msg(model_class, *data.values())
    return finish_registration(user)


def logout() -> None:
    """Выход из аккаунта"""
    State.user = None


def show_grades(student: Optional[User] = None) -> None:
    """Показывает все оценки ученика за текущий период (атрибут 'current_dates' класса State)"""

    if student is None:
        student = State.user
    subjects = get_objs_from_sct(SubjectClassTeacher.manager.filter(school_class=student.school_class), 'subject')
    raw_table = get_empty_table_dict(subjects)
    grades = Grade.manager.filter(student=student)
    fill_raw_table_with_grades(raw_table, grades, 'subject')
    pretty_table = get_pretty_table()
    prepare_pretty_table_for_grades(pretty_table, subjects)
    fill_pretty_table_with_grades(raw_table, pretty_table)
    print(pretty_table)


def get_my_teachers() -> None:
    """Показывает всех учителей, которые ведут предметы у конкректного ученика"""

    pretty_table = get_pretty_table()
    prepare_pretty_table_for_tchs_list(pretty_table)
    user_class = State.user.school_class
    teachers_subjects = SubjectClassTeacher.manager.filter(school_class=user_class)
    fill_pretty_table_with_tchs(pretty_table, teachers_subjects)
    print(pretty_table)


def rate_students() -> None:
    """Позволяет выставить оценки ученикам"""

    try:
        school_class, subject = get_date_to_rate_students()
    except NoSubjectsTaughtByTheTeacher:
        print_error('Вы не ведете ни одного предмета!')
    else:
        process_student_grading(school_class, subject)


def print_school_class_grades(school_class: Class) -> None:
    subjects = get_objs_from_sct(SubjectClassTeacher.manager.filter(school_class=school_class), 'subject')
    subject = get_obj_from_user(subjects, 'предмет')
    print_class_grades_table(school_class, subject)


def print_grades_for_one_student(school_class: Class) -> None:
    students = sorted(Student.manager.filter(school_class=school_class), key=lambda x: x.second_name)
    student = get_obj_from_user(students, 'ученика')
    print(f'Успеваемость {student}:')
    show_grades(student)
