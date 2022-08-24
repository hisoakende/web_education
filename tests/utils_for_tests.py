from typing import Any

import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.sql import Identifier, SQL

from config import *
from working_with_models.models import BaseModel

data_for_conn = {'database': DATABASE_NAME, 'user': DATABASE_USER, 'password': DATABASE_PASSWORD,
                 'host': DATABASE_HOST, 'port': DATABASE_PORT}


def prepare_db() -> tuple[connection, cursor]:
    conn = psycopg2.connect(**data_for_conn)
    cur = conn.cursor()
    cur.execute(
        SQL('CREATE TABLE {} ({} int, {} varchar)').format(Identifier('table_for_tests'), Identifier('first_attr'),
                                                           Identifier('second_attr')))
    cur.execute(
        SQL('INSERT INTO {} ({}, {}) VALUES (%s, %s)').format(Identifier('table_for_tests'),
                                                              Identifier('first_attr'),
                                                              Identifier('second_attr')), (1, 'text1'))
    conn.commit()
    return conn, cur


def clean_db(conn: connection, cur: cursor) -> None:
    cur.execute(SQL('DROP TABLE {}').format(Identifier('table_for_tests')))
    conn.commit()
    cur.close()
    conn.close()


def get_some_instance() -> 'SomeClass':
    return type('SomeClass', (), {})()


def get_some_model() -> type:
    related_model = type('RelatedModel', (BaseModel,),
                         {'db_table': 'related_table', 'attributes': ['pk', 'some_attr']})
    main_model = type('MainModel', (BaseModel,),
                      {'db_table': 'main_table', 'attributes': ['pk', 'related_model'],
                       'related_data': {'related_model': related_model}})
    return main_model


def init_for_main_model(self: BaseModel, related_model: BaseModel) -> None:
    """Метод __init__ для главного класса, созданного в функции 'get_some_model'"""
    super(self.__class__, self).__init__()
    self.related_model = related_model


def init_for_related_model(self: BaseModel, some_attr: Any) -> None:
    """Метод __init__ для связанного класса, созданного в функции 'get_some_model'"""
    super(self.__class__, self).__init__()
    self.some_attr = some_attr
