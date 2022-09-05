from getpass import getpass
from typing import Union

import psycopg2.errors

from other.utils import get_password_hash
from user_interaction.enums import ProfileType
from user_interaction.messages import profile_type_msg, print_error, create_user_with_this_data_msg
from user_interaction.requesting_data_from_user import request_data, get_choice, get_answer
from user_interaction.services import State, get_empty_table_dict, fill_raw_table_with_grades, \
    prepare_pretty_table_for_grades, \
    fill_pretty_table_with_grades, get_pretty_table, prepare_pretty_table_for_tchs_list, fill_pretty_table_with_tchs
from user_interaction.services import create_dict_with_user_data, try_to_create_user, profiles, UserTypes, \
    try_to_insert_user_to_db
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


def finish_registration(user: UserTypes) -> Union[None, UserTypes]:
    try:
        is_created_user = try_to_insert_user_to_db(user)
    except psycopg2.errors.UniqueViolation:
        print_error('Аккаунт такого типа с данным email уже существует')
        return
    if is_created_user:
        return user
    return register_user()


@request_data('Повторите процедуру регистрации еще раз\n')
def register_user() -> Union[None, UserTypes]:
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


def show_grades() -> None:
    """Показывает все оценки ученика за текущий период (атрибут 'current_dates' класса State)"""

    subjects = list(map(lambda x: x.subject,
                        SubjectClassTeacher.manager.filter(school_class=State.user.school_class)))
    raw_table = get_empty_table_dict(subjects)
    grades = Grade.manager.filter(student=State.user)
    fill_raw_table_with_grades(raw_table, grades)
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
