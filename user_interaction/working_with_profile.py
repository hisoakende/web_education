from getpass import getpass
from typing import Union, Type

from other.utils import get_password_hash
from user_interaction.messages import profile_type_msg, print_error, create_user_with_this_data_msg
from user_interaction.requesting_data_from_user import request_data, ProfileType, get_choice, get_answer, CreateUser
from working_with_models.models import Administrator, Teacher, Student, User

profiles = {ProfileType.student: Student,
            ProfileType.teacher: Teacher,
            ProfileType.administrator: Administrator}

UserTypes = Union[Teacher, Student, Administrator]


@request_data('Неправильный email или пароль')
def authenticate_user() -> Union[None, User]:
    """Аутентификация пользователя"""

    type_profile = get_choice(ProfileType, profile_type_msg)
    email = get_answer('Введите email:')
    password = get_answer('Введите пароль:', getpass)
    model_class = profiles[type_profile]
    user = model_class.manager.get(email=email)
    if user and user.password == get_password_hash(password):
        return user


def try_to_create_user(model_class: Type[UserTypes], first_name: str, second_name: str,
                       patronymic: str, email: str, password: str, additional_field: str) -> UserTypes:
    try:
        user = model_class(first_name, second_name, patronymic, email, password, additional_field)
    except ValueError as exception:
        print_error(f'{exception}')
    else:
        return user


def get_additional_field(model_class: Type[UserTypes]) -> Union[None, str]:
    if model_class is Teacher:
        return get_answer('Введите информацию об учителе (например: Учитель географии, стаж - 20 лет):')
    elif model_class is Student:
        return get_answer('Введите класс:')


def try_to_insert_user_to_db(user: UserTypes) -> bool:
    create_user = get_choice(CreateUser)
    if create_user == CreateUser.no:
        return False
    user.manager.create(execution=True)
    return True


def create_dict_with_user_data(model_class: Type[UserTypes]) -> dict[str, str]:
    return {'first_name': get_answer(f'Введите имя:'),
            'second_name': get_answer(f'Введите фамилию:'),
            'patronymic': get_answer(f'Введите отчество:'),
            'email': get_answer(f'Введите email:'),
            'password': get_answer('Введите пароль:', getpass),
            'repeated_password': get_answer('Повторите пароль:', getpass),
            'additional_fields': get_additional_field(model_class)}


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
    is_created_user = try_to_insert_user_to_db(user)
    if is_created_user:
        return user
    return register_user()
