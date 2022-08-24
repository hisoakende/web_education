def separate_action() -> None:
    print(f'\33[34m{"-" * 50}\33[0m')


def title(msg: str) -> None:
    print(f'\33[1m{msg}\33[0m')


def exit_msg() -> None:
    print('\n\33[35m[-1] - выйти\33[0m')


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
