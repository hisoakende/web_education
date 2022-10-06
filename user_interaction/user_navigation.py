from user_interaction.enums import WhatToDoWithLogin, teacher_main_menu_choice, \
    student_main_menu_choice, administrator_main_menu_choice, ManageClassPerformanceChoices, \
    ManageSchoolPerformanceChoices, WhatToDoWithObj
from user_interaction.messages import authenticate_user_msg, \
    choice_about_login_msg, registration_user_msg, hello_user_msg, teacher_main_menu_choices_msg, \
    student_main_menu_choices_msg, administrator_main_menu_choices_msg, main_menu_msg, separate_action, print_error, \
    manage_class_performance_choices_msg, manage_school_performance_choices_msg, what_to_do_with_obj_msg, \
    possible_actions_msg
from user_interaction.requesting_data_from_user import get_choice
from user_interaction.services import State, get_obj_from_user
from user_interaction.user_actions import authenticate_user, register_user, logout, show_grades, get_my_teachers, \
    rate_students_by_teacher, print_school_class_grades, print_grades_of_student, \
    rate_students_by_administrator, remove_obj_by_admin, change_obj_by_admin, create_obj_by_admin, \
    set_current_dates_by_admin, activate_users
from working_with_models.models import Class, Teacher, Subject, Student, Period, SubjectClassTeacher


def welcome() -> None:
    """Функция приветствия"""

    user = None
    while user is None:
        possible_actions_msg()
        user_choice = get_choice(WhatToDoWithLogin, choice_about_login_msg)
        if user_choice is WhatToDoWithLogin.authentication:
            authenticate_user_msg()
            user = authenticate_user()
        else:
            registration_user_msg()
            user = register_user()
        separate_action()
    State.user = user


def main_menu() -> None:
    """Функция для работы с главным меню"""

    hello_user_msg(State.user.first_name, State.user.patronymic, State.user.name_ru)
    separate_action()
    main_menu_msg()
    action_set, choices, main_menu_choices_msg = user_actions_and_choices[State.user.__class__.__name__]
    what_to_do_choice = get_choice(choices, main_menu_choices_msg)
    action_set[what_to_do_choice.name]()


def manage_class_performance() -> None:
    """Пункт меню 'Классное руководство'"""

    separate_action()
    school_classes = Class.manager.filter(classroom_teacher=State.user)
    if not school_classes:
        print_error('У вас нет ни одного класса!')
    school_class = get_obj_from_user(school_classes, 'класс')
    what_to_do_choice = get_choice(ManageClassPerformanceChoices, manage_class_performance_choices_msg)
    manage_class_performance_actions[what_to_do_choice](school_class)


def manage_school_performance() -> None:
    """Пункт меню 'Управлять успеваемостью' администратора"""

    what_to_do_choice = get_choice(ManageSchoolPerformanceChoices, manage_school_performance_choices_msg)
    if what_to_do_choice is ManageSchoolPerformanceChoices.rate_student:
        rate_students_by_administrator()
    else:
        school_classes = Class.manager.all()
        school_class = get_obj_from_user(school_classes, 'класс')
        print_grades_of_student(school_class)


def change_object() -> None:
    """Пункт меню 'Изменить объект' администратора"""

    what_to_do_with_obj_choice = get_choice(WhatToDoWithObj, what_to_do_with_obj_msg)
    if what_to_do_with_obj_choice is WhatToDoWithObj.change:
        model_classes = model_classes_to_change
    else:
        model_classes = model_classes_to_create_and_remove
    model_class_to_change = get_obj_from_user(list(model_classes.keys()), 'тип объекта')
    change_object_actions[what_to_do_with_obj_choice](model_classes[model_class_to_change])


base_actions = {'exit': logout}
student_actions = {'show_grades': show_grades, 'get_my_teachers': get_my_teachers}
teacher_actions = {'rate_students_by_teacher': rate_students_by_teacher,
                   'manage_class_performance': manage_class_performance}
administrator_actions = {'manage_school_performance': manage_school_performance, 'change_object': change_object,
                         'set_current_dates_by_admin': set_current_dates_by_admin, 'activate_users': activate_users}

manage_class_performance_actions = {ManageClassPerformanceChoices.print_school_class_grades: print_school_class_grades,
                                    ManageClassPerformanceChoices.print_grades_of_student: print_grades_of_student}
manage_school_performance_actions = {ManageSchoolPerformanceChoices.rate_student: rate_students_by_administrator,
                                     ManageSchoolPerformanceChoices.print_students_grades: print_grades_of_student}

change_object_actions = {WhatToDoWithObj.add: create_obj_by_admin, WhatToDoWithObj.remove: remove_obj_by_admin,
                         WhatToDoWithObj.change: change_obj_by_admin}

user_actions_and_choices = {
    'Teacher': (base_actions | teacher_actions, teacher_main_menu_choice, teacher_main_menu_choices_msg),
    'Student': (base_actions | student_actions, student_main_menu_choice, student_main_menu_choices_msg),
    'Administrator': (base_actions | administrator_actions, administrator_main_menu_choice,
                      administrator_main_menu_choices_msg)
}

model_classes_to_change = {Class.name_ru: Class, Subject.name_ru: Subject,
                           Period.name_ru: Period, SubjectClassTeacher.name_ru: SubjectClassTeacher}
model_classes_to_create_and_remove = model_classes_to_change | {Teacher.name_ru: Teacher, Student.name_ru: Student}
