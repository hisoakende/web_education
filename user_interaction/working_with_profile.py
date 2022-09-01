from getpass import getpass
from typing import Union

import psycopg2.errors

from other.utils import get_password_hash
from user_interaction.enums import ProfileType
from user_interaction.messages import profile_type_msg, print_error, create_user_with_this_data_msg
from user_interaction.requesting_data_from_user import request_data, get_choice, get_answer
from user_interaction.services import create_dict_with_user_data, try_to_create_user, try_to_insert_user_to_db, \
    profiles, UserTypes
from working_with_models.models import User


@request_data('Неправильный email или пароль\nПовторите процедуру аутентификации еще раз\n')
def authenticate_user() -> Union[None, User]:
    """Аутентификация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    email = get_answer('Введите email:')
    password = get_answer('Введите пароль:', getpass)
    model_class = profiles[type_profile]
    user = model_class.manager.get(email=email)
    if user and user.password == get_password_hash(password):
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
