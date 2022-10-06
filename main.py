#!/usr/bin/env python3

"""Исполняемый файл всего приложения"""

from config import *
from db_interaction.manage_db import Database
from db_interaction.working_with_data import TablesManager
from user_interaction.messages import goodbye_msg, error_msg, print_error, welcome_msg, separate_action
from user_interaction.services import State, set_current_dates_to_state
from user_interaction.user_navigation import welcome, main_menu
from working_with_models.models import Period, Administrator


def main():
    db = Database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    State.db = db
    TablesManager(db)
    set_current_dates_to_state(Period.manager.get(is_current=True))
    welcome_msg()
    while True:
        if State.user is None:
            welcome()
        if isinstance(State.user, Administrator) or State.user.is_active:
            main_menu()
        else:
            print_error('Ваш аккаунт не активирован. Пожайлуста, дождитесь, пока администратор активирует его')
            separate_action()
            State.user = None


if __name__ == '__main__':
    try:
        main()
    except (SystemExit, KeyboardInterrupt) as e:
        if isinstance(e, KeyboardInterrupt):
            print()
        goodbye_msg()
    except:
        error_msg()
