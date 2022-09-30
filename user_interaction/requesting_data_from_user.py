import enum
from functools import wraps
from typing import Callable, Union, Any, Type, Optional

from user_interaction.enums import WhatToDoWithLogin
from user_interaction.messages import choose_exit_msg

input_sign = '\33[32m---> \033[0m'
invalid_input = 'Неккоректный ввод!'


def request_data(msg: Optional[str] = invalid_input) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> WhatToDoWithLogin:
            """
            Декоратор позволяет вызывать функцию до того момента,
            как она вернет значение, неравное 'None'
            """
            while True:
                data = func(*args, **kwargs)
                if data is not None:
                    return data
                if msg is not None:
                    print(f'\33[31m{msg}\33[0m')

        return wrapper

    return decorator


@request_data()
def _get_choice(choices: Type[enum.Enum]) -> Optional[enum.Enum]:
    choice = input(input_sign)
    if choice == '-1':
        raise SystemExit
    elif choice in choices:
        return choices(choice)


@request_data()
def _get_answer(func_input: Callable = input, func_check: Callable = lambda x: x) -> Optional[str]:
    answer = func_input(input_sign)
    if func_check(answer):
        return answer


def print_message(msg: Union[Callable, str, None] = None) -> None:
    if isinstance(msg, str):
        print(msg)
    elif isinstance(msg, Callable):
        msg()


def get_choice(choices: Type[enum.Enum], msg: Union[Callable, str, None] = None) -> Optional[enum.Enum]:
    print_message(msg)
    choose_exit_msg()
    return _get_choice(choices)


def get_answer(msg: Union[Callable, str, None] = None, func_input: Callable = input) -> Optional[str]:
    print_message(msg)
    return _get_answer(func_input)
