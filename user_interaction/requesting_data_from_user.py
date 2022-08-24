import enum
from functools import wraps
from getpass import getpass
from typing import Callable, Union, Any

from user_interaction.messages import choice_about_login_msg, profile_type_msg

input_sign = '\33[32m---> \033[0m'
invalid_input = 'Неккоректный ввод!'


class ExtendedEnumMeta(enum.EnumMeta):

    def __contains__(cls, item):
        return item in sum([[val, val.value, val.name] for val in cls], [])


class WhatToDoWithLogin(enum.Enum, metaclass=ExtendedEnumMeta):
    authentication = '1'
    registration = '2'


class ProfileType(enum.Enum, metaclass=ExtendedEnumMeta):
    student = '1'
    teacher = '2'
    administrator = '3'


def request_data(msg: str = invalid_input) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> WhatToDoWithLogin:
            while True:
                data = func(*args, **kwargs)
                if data is not None:
                    return data
                print(f'\33[31m{msg}\33[0m')

        return wrapper

    return decorator


@request_data()
def get_choice(choices: ExtendedEnumMeta) -> Union[None, enum.Enum]:
    choice = input(input_sign)
    if choice in choices:
        return choices(choice)


@request_data()
def get_answer(func: Callable = input) -> Union[None, str]:
    answer = func(input_sign)
    if answer:
        return answer


def get_choice_about_login() -> Union[None, WhatToDoWithLogin]:
    choice_about_login_msg()
    return get_choice(WhatToDoWithLogin)


def get_profile_type() -> Union[None, ProfileType]:
    profile_type_msg()
    return get_choice(ProfileType)


def get_email() -> Union[None, str]:
    print('Введите email:')
    return get_answer()


def get_password() -> Union[None, str]:
    print('Введите пароль:')
    return get_answer(getpass)
