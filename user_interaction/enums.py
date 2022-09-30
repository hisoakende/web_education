import enum
from typing import Any

base_main_menu_choice = [('exit', '1')]


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


class SaveChanges(enum.Enum, metaclass=ExtendedEnumMeta):
    yes = '1'
    no = '2'


class WhatToDoWithGrades(enum.Enum, metaclass=ExtendedEnumMeta):
    add = '1'
    remove = '2'
    nothing = '3'


class ManageClassPerformanceChoices(enum.Enum, metaclass=ExtendedEnumMeta):
    print_school_class_grades = '1'
    print_grades_of_student = '2'


class ManageSchoolPerformanceChoices(enum.Enum, metaclass=ExtendedEnumMeta):
    rate_student = '1'
    print_students_grades = '2'


class WhatToDoWithObj(enum.Enum, metaclass=ExtendedEnumMeta):
    add = '1'
    remove = '2'
    change = '3'


class EnumConstructor(enum.Enum, metaclass=ExtendedEnumMeta):

    def __str__(self) -> str:
        return self.name


teacher_main_menu_choice = EnumConstructor(
    'TeacherMainMenuChoice',
    base_main_menu_choice + [('rate_students_by_teacher', '2'), ('manage_class_performance', '3')]
)

student_main_menu_choice = EnumConstructor(
    'StudentMainMenuChoice',
    base_main_menu_choice + [('show_grades', '2'), ('get_my_teachers', '3')]
)

administrator_main_menu_choice = EnumConstructor(
    'AdministratorMainMenuChoice',
    base_main_menu_choice + [('manage_school_performance', '2'), ('change_object', '3')]
)
