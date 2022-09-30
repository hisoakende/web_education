from typing import Iterable

from working_with_models.models import Student, Grade


def separate_action() -> None:
    print(f'\33[34m{"-" * 50}\33[0m')


def strong_font(msg: str) -> None:
    print(f'\33[1m{msg}\33[0m')


def goodbye_msg() -> None:
    separate_action()
    strong_font('Спасибо за работу в нашем приложении. Всего хорошего!')


def choose_exit_msg() -> None:
    print('\33[35m[-1] - выйти из программы\33[0m')


def welcome_msg() -> None:
    separate_action()
    strong_font('Добро пожаловать в систему web-образования!')


def choice_about_login_msg() -> None:
    print('[1] - войти в аккаунт')
    print('[2] - зарегистироваться')


def profile_type_msg() -> None:
    print('Выберите тип аккаунта:')
    print('[1] - ученик')
    print('[2] - учитель')
    print('[3] - администратор')


def authenticate_user_msg() -> None:
    separate_action()
    strong_font('Аутентификация')


def registration_user_msg() -> None:
    separate_action()
    strong_font('Регистрация')


def print_error(msg: str) -> None:
    print(f'\33[31m{msg}\33[0m')


def print_full_name(first_name: str, second_name: str, patronymic: str) -> None:
    print(f'Имя: {first_name}')
    print(f'Фамилия: {second_name}')
    print(f'Отчество: {patronymic}')


def save_account_msg() -> None:
    print('\nСохранить аккаунт?')
    yes_or_no_msg()


def save_obj_msg() -> None:
    print('\nСохранить объект?')
    yes_or_no_msg()


def yes_or_no_msg() -> None:
    print('[1] - да')
    print('[2] - нет')


def create_obj_with_this_data_msg(obj):
    for attr_index in range(len(obj.attributes) - 1):
        if obj.attributes[attr_index + 1] not in ('password', 'is_current'):
            print(f'{obj.attributes_ru[attr_index].lower().capitalize()}: '
                  f'{getattr(obj, obj.attributes[attr_index + 1])}')


def teacher_main_menu_choices_msg() -> None:
    base_main_menu_choices_msg()
    print('[2] - управлять успеваемостью')
    print('[3] - классное руководство')


def manage_class_performance_choices_msg() -> None:
    separate_action()
    print('Возможные действия:')
    print('[1] - показать успеваемость класса')
    print('[2] - показать успеваемость одного ученика')


def student_main_menu_choices_msg() -> None:
    base_main_menu_choices_msg()
    print('[2] - посмотреть оценки')
    print('[3] - показать моих учителей')


def administrator_main_menu_choices_msg() -> None:
    base_main_menu_choices_msg()
    print('[2] - управлять успеваемостью')
    print('[3] - управлять объектами')


def base_main_menu_choices_msg() -> None:
    print('[1] - выйти из аккаунта')


def hello_user_msg(name: str, patronymic: str, user_type: str) -> None:
    separate_action()
    strong_font(f'Вы вошли как {name} {patronymic} ({user_type})')


def main_menu_msg() -> None:
    strong_font('Главное меню')
    print('Возможные действия:')


def error_msg() -> None:
    separate_action()
    print_error('Произошла ошибка. Пожайлуста, запустите приложение снова. '
                'Если ошибка не исчезла, напишите об этом сюда: hisoakende@gmail.com')


def print_grading_instruction() -> None:
    print('Оценка добавляется/удаляется в формате: <идентификатор ученика>: оценка\n'
          'Оценки разным ученикам разделяются точкой с запятой \';\'\n'
          'Сразу за оценкой в скобках указывается дата\n'
          'Чтобы добавить/удалить несколько оценок одного ученика, соответствующие команды нужно писать через запятую\n'
          'Например, 15: 1(1/1/2000), 2(15/1/2000); 32: 3(2/1/2000)\n'
          '\n'
          'Введите команды для добавления/удаления оценок, или [-2] для выхода:')


def preliminary_grades_msg(preliminary_grades: list[tuple[Student, list[Grade]]], action: str) -> None:
    print(f'Подтверждаете {action} следующих оценок?')
    for preliminary_grade in sorted(preliminary_grades, key=lambda x: x[0].second_name):
        print(f'{preliminary_grade[0]}: {", ".join(f"{grade.value}({grade.date})" for grade in preliminary_grade[1])}')
    yes_or_no_msg()


def print_objs_for_the_user_to_select(obj_name: str, objs: Iterable) -> None:
    print(f'Выберете {obj_name}:')
    print('\n'.join(f'[{i}] - {schl_cls}' for i, schl_cls in enumerate(objs, 1)))


def what_to_do_with_grades_msg() -> None:
    print('Действия с оценками:')
    print('[1] - добавить')
    print('[2] - удалить')
    print('[3] - ничего')


def manage_school_performance_choices_msg() -> None:
    separate_action()
    print('Возможные действия:')
    print('[1] - управлять успеваемостью')
    print('[2] - показать успеваемость одного ученика')


def what_to_do_with_obj_msg() -> None:
    print('Действия с объектом:')
    print('[1] - добавить')
    print('[2] - удалить')
    print('[3] - изменить')
