import enum
from typing import Any

base_main_menu_choice = {'exit': '1'}


class ExtendedEnumMeta(enum.EnumMeta):

    def __contains__(cls, item: Any) -> bool:
        return item in sum([[val, val.value, val.name] for val in cls], [])


class WhatToDoWithLogin(enum.Enum, metaclass=ExtendedEnumMeta):
    authentication = '1'
    registration = '2'


class ProfileType(enum.Enum, metaclass=ExtendedEnumMeta):
    student = '1'
    teacher = '2'
    administrator = '3'


class CreateUser(enum.Enum, metaclass=ExtendedEnumMeta):
    yes = '1'
    no = '2'


class EnumSchoolClassConstructor(enum.Enum, metaclass=ExtendedEnumMeta):

    def __str__(self) -> str:
        return self.name


class BaseMainMenuChoiceConstructor(enum.Enum, metaclass=ExtendedEnumMeta):
    pass


def get_base_main_menu_choices() -> list[tuple[str, str]]:
    return [(choice, number) for choice, number in base_main_menu_choice.items()]


teacher_main_menu_choice = BaseMainMenuChoiceConstructor(
    'TeacherMainMenuChoice',
    get_base_main_menu_choices() + [('show_my_students', '2')]
)

student_main_menu_choice = BaseMainMenuChoiceConstructor(
    'StudentMainMenuChoice',
    get_base_main_menu_choices() + [('show_grades', '2'), ('get_my_teachers', '3')]
)

administrator_main_menu_choice = BaseMainMenuChoiceConstructor(
    'AdministratorMainMenuChoice',
    get_base_main_menu_choices() + []
)
