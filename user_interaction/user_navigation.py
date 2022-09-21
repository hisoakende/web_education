from user_interaction.enums import WhatToDoWithLogin, teacher_main_menu_choice, \
    student_main_menu_choice, administrator_main_menu_choice, ManageClassChoices
from user_interaction.messages import welcome_msg, authenticate_user_msg, \
    choice_about_login_msg, registration_user_msg, hello_user_msg, teacher_main_menu_choices_msg, \
    student_main_menu_choices_msg, administrator_main_menu_choices_msg, main_menu_msg, separate_action, print_error, \
    manage_user_choices_msg
from user_interaction.requesting_data_from_user import get_choice
from user_interaction.services import State, get_obj_from_user, get_objs_from_sct
from user_interaction.user_actions import authenticate_user, register_user, logout, show_grades, get_my_teachers, \
    rate_students, SubjectClassTeacher, print_school_class_grades, print_grades_for_one_student


def welcome() -> None:
    """Функция приветствия"""

    welcome_msg()
    user_choice = get_choice(WhatToDoWithLogin, choice_about_login_msg)
    if user_choice is WhatToDoWithLogin.authentication:
        authenticate_user_msg()
        user = authenticate_user()
    else:
        registration_user_msg()
        user = register_user()
    hello_user_msg(user.first_name, user.patronymic, user.name_ru)
    State.user = user


def main_menu() -> None:
    """Функция для работы с главным меню"""

    separate_action()
    main_menu_msg()
    action_set, choices, main_menu_choices_msg = user_actions_and_choices[State.user.__class__.__name__]
    what_to_do_choice = get_choice(choices, main_menu_choices_msg)
    action_set[what_to_do_choice.name]()


def manage_class() -> None:
    """Пункт меню 'Классное руководство'"""

    separate_action()
    classes_of_teachers = get_objs_from_sct(SubjectClassTeacher.manager.filter(teacher=State.user), 'school_class')
    if not classes_of_teachers:
        print_error('Вы не ведете ни одного предмета!')
    school_class = get_obj_from_user(classes_of_teachers, 'класс')
    what_to_do_choice = get_choice(ManageClassChoices, manage_user_choices_msg)
    manage_class_actions[what_to_do_choice](school_class)


base_actions = {'exit': logout}
student_actions = {'show_grades': show_grades, 'get_my_teachers': get_my_teachers}
teacher_actions = {'rate_students': rate_students, 'manage_class': manage_class}
manage_class_actions = {ManageClassChoices.print_school_class_grades: print_school_class_grades,
                        ManageClassChoices.print_grades_for_one_student: print_grades_for_one_student}

user_actions_and_choices = {
    'Teacher': (base_actions | teacher_actions, teacher_main_menu_choice, teacher_main_menu_choices_msg),
    'Student': (base_actions | student_actions, student_main_menu_choice, student_main_menu_choices_msg),
    'Administrator': (base_actions, administrator_main_menu_choice, administrator_main_menu_choices_msg)
}
