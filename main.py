#!/usr/bin/env python3

"""Исполняемый файл всего приложения"""

from config import *
from db_interaction.manage_db import Database
from db_interaction.working_with_data import TablesManager
from user_interaction.user_navigation import welcome


def main():
    db = Database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT)
    TablesManager(db)
    welcome()


if __name__ == '__main__':
    main()
