import enum
from getpass import getpass
from typing import Type, Union

from user_interaction.enums import CreateUser, EnumSchoolClassConstructor, ProfileType
from user_interaction.messages import print_error
from user_interaction.requesting_data_from_user import get_answer, get_choice
from working_with_models.models import Teacher, Student, Class, Administrator

profiles = {ProfileType.student: Student,
            ProfileType.teacher: Teacher,
            ProfileType.administrator: Administrator}

UserTypes = Union[Teacher, Student, Administrator]


def try_to_create_user(model_class: Type[UserTypes], first_name: str, second_name: str,
                       patronymic: str, email: str, password: str, *additional_field: str) -> UserTypes:
    try:
        user = model_class(first_name, second_name, patronymic, email, password, *additional_field)
    except ValueError as exception:
        print_error(f'{exception}')
    else:
        return user


def get_school_class_from_user() -> Class:
    classes = get_classes_for_registration()
    classes_enum = create_enum_of_classes(classes)
    classes_msg = get_str_of_classes_for_msg(classes)
    class_pk = get_choice(classes_enum, f'Введите класс:\n{classes_msg}').value
    return Class.manager.get(pk=class_pk, execution=True)


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


def get_classes_for_registration() -> list[tuple[str, str]]:
    classes = Class.manager.all(execution=True)
    return [(str(cls.number) + cls.letter, str(cls.pk)) for cls in classes]


def get_str_of_classes_for_msg(classes: list[tuple[str, str]]) -> str:
    return '\n'.join(f'[{cls[1]}] - {cls[0]}' for cls in classes)


def create_enum_of_classes(classes: list[tuple[str, str]]) -> Type[enum.Enum]:
    return EnumSchoolClassConstructor('SchoolClassEnum', classes)
