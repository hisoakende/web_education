from user_interaction.messages import welcome_msg, authenticate_user_msg, choice_about_login_msg, registration_user_msg
from user_interaction.requesting_data_from_user import WhatToDoWithLogin, get_choice
from user_interaction.working_with_profile import authenticate_user, register_user


class State:
    user = None


def welcome() -> None:
    """Функция приветствия"""

    welcome_msg()
    user_choice = get_choice(WhatToDoWithLogin, choice_about_login_msg)
    if user_choice == WhatToDoWithLogin.authentication:
        authenticate_user_msg()
        user = authenticate_user()
    else:
        registration_user_msg()
        user = register_user()
    State.user = user
