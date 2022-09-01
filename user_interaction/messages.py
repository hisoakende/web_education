from typing import Type, Union

from working_with_models.models import Teacher, Student, Class, Administrator


def separate_action() -> None:
    print(f'\33[34m{"-" * 50}\33[0m')


def title(msg: str) -> None:
    print(f'\33[1m{msg}\33[0m')


def exit_msg() -> None:
    print('\33[35m[-1] - выйти из программы\33[0m')


def welcome_msg() -> None:
    separate_action()
    title('Добро пожаловать в систему web-образования!')


def choice_about_login_msg() -> None:
    print('[1] - войти в аккаунт')
    print('[2] - зарегистироваться')
    exit_msg()


def profile_type_msg() -> None:
    print('Выберите тип аккаунта:')
    print('[1] - ученик')
    print('[2] - учитель')
    print('[3] - администратор')
    exit_msg()


def authenticate_user_msg() -> None:
    separate_action()
    title('Аутентификация')


def registration_user_msg() -> None:
    separate_action()
    title('Регистрация')


def print_error(msg: str) -> None:
    print(f'\33[31m{msg}\33[0m')


def print_full_name(first_name: str, second_name: str, patronymic: str) -> None:
    print(f'Имя: {first_name}')
    print(f'Фамилия: {second_name}')
    print(f'Отчество: {patronymic}')


def whether_to_save_account() -> None:
    print('\nСохранить профиль с такими данными?')
    print('[1] - сохранить')
    print('[2] - не сохранять, повторить регистрацию')


def create_user_with_this_data_msg(model_class: Type[Union[Teacher, Student, Administrator]], first_name: str,
                                   second_name: str, patronymic: str,
                                   email: str, additional_field: Union[None, Class, str] = None) -> None:
    print_full_name(first_name, second_name, patronymic)
    print(f'Email: {email}')
    if model_class is Teacher:
        print(f'Информация об учителе: {additional_field}')
    elif model_class is Student:
        print(f'Класс: {str(additional_field.number) + additional_field.letter}')
    whether_to_save_account()
    exit_msg()
