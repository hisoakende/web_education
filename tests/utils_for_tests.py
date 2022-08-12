import psycopg2
from psycopg2.extensions import connection, cursor
from psycopg2.sql import Identifier, SQL

from config import *

data_for_conn = {'database': DATABASE_NAME, 'user': DATABASE_USER, 'password': DATABASE_PASSWORD,
                 'host': DATABASE_HOST, 'port': DATABASE_PORT}


def prepare_db() -> tuple[connection, cursor]:
    conn = psycopg2.connect(**data_for_conn)
    cur = conn.cursor()
    cur.execute(
        SQL('CREATE TABLE {} ({} int, {} varchar)').format(Identifier('table_for_tests'), Identifier('first_attr'),
                                                           Identifier('second_attr')))
    cur.execute(SQL('INSERT INTO {} ({}, {}) '
                    'VALUES (%s, %s)').format(Identifier('table_for_tests'),
                                              Identifier('first_attr'),
                                              Identifier('second_attr')), (1, 'text1'))
    conn.commit()
    return conn, cur


def clean_db(conn, cur) -> None:
    cur.execute(SQL('DROP TABLE {}').format(Identifier('table_for_tests')))
    conn.commit()
    cur.close()
    conn.close()
