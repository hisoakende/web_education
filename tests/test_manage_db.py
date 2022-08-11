import unittest

from psycopg2.sql import SQL, Identifier

from config import *
from interaction_with_db.manage_db import *
from other.exceptions import ManyInstanceOfClassError


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_for_conn = {'database': DATABASE_NAME, 'user': DATABASE_USER, 'password': DATABASE_PASSWORD,
                         'host': DATABASE_HOST, 'port': DATABASE_PORT}
        cls.conn = psycopg2.connect(**data_for_conn)
        cls.cur = cls.conn.cursor()
        cls.cur.execute(
            SQL('CREATE TABLE {} ({} int, {} varchar)').format(Identifier('table_for_tests'), Identifier('first_attr'),
                                                               Identifier('second_attr')))
        cls.cur.execute(SQL('INSERT INTO {} ({}, {}) '
                            'VALUES (%s, %s)').format(Identifier('table_for_tests'),
                                                      Identifier('first_attr'),
                                                      Identifier('second_attr')), (1, 'text1'))
        cls.conn.commit()

        cls.db = Database(**data_for_conn)

        cls.r_select = Request(SQL('SELECT * FROM {}').format(Identifier('table_for_tests')), (), 'with_output')
        cls.r_insert = Request(SQL('INSERT INTO {} ({}, {}) VALUES (%s, %s)').format(
            Identifier('table_for_tests'), Identifier('first_attr'),
            Identifier('second_attr')), (2, 'text2'), 'without_output')

    def tearDown(self):
        self.conn.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.cur.execute(SQL('DROP TABLE {}').format(Identifier('table_for_tests')))
        cls.conn.commit()
        cls.cur.close()
        cls.conn.close()

    def test_for_singleton(self):
        self.assertEqual(self.db, Database._Singleton__instance)
        self.assertRaises(ManyInstanceOfClassError, Database)

    def test_check_to_requests_exist(self):
        self.assertRaises(DontExistUnexecutedRequests,
                          self.db.check_to_requests_exist)
        self.db._Database__unexecuted_requests.append(self.r_select)
        self.assertIsNone(self.db.check_to_requests_exist())

    def test_execute_one_request(self):
        self.db._Database__execute_one_request(self.cur, self.r_select)
        self.assertEqual([(1, 'text1')], self.db.output)
        result = self.db._Database__execute_one_request(self.cur, self.r_insert)
        self.assertIsNone(result)

    def test_execute_requests(self):
        self.db._Database__unexecuted_requests += [self.r_select for _ in range(3)]
        self.db._Database__execute_requests(self.cur)
        self.assertEqual([], self.db._Database__unexecuted_requests)
