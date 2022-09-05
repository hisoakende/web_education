from user_interaction.enums import WhatToDoWithLogin, teacher_main_menu_choice, \
    student_main_menu_choice, administrator_main_menu_choice
from user_interaction.messages import welcome_msg, authenticate_user_msg, \
    choice_about_login_msg, registration_user_msg, hello_user_msg, \
    teacher_main_menu_choices_msg, student_main_menu_choices_msg, administrator_main_menu_choices_msg, main_menu_msg
from user_interaction.requesting_data_from_user import get_choice
from user_interaction.services import State
from user_interaction.user_actions import authenticate_user, register_user, logout, show_grades, get_my_teachers, \
    show_my_students


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


base_actions = {'exit': logout}
student_actions = {'show_grades': show_grades, 'get_my_teachers': get_my_teachers}
teacher_action = {'show_my_students': show_my_students}

user_actions_and_choices = {
    'Teacher': (base_actions | teacher_action, teacher_main_menu_choice, teacher_main_menu_choices_msg),
    'Student': (base_actions | student_actions, student_main_menu_choice, student_main_menu_choices_msg),
    'Administrator': (base_actions | {}, administrator_main_menu_choice, administrator_main_menu_choices_msg)
}


def main_menu() -> None:
    """Функция для работы с главным меню"""

    main_menu_msg()
    action_set, choices, main_menu_choices_msg = user_actions_and_choices[State.user.__class__.__name__]
    what_to_do_choice = get_choice(choices, main_menu_choices_msg)
    action_set[what_to_do_choice.name]()
