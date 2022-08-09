import unittest

from config import *
from manage_db import *


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_for_conn = {'database': DATABASE_NAME, 'user': DATABASE_USER, 'password': DATABASE_PASSWORD,
                         'host': DATABASE_HOST, 'port': DATABASE_PORT}
        cls.conn = psycopg2.connect(**data_for_conn)
        cls.cur = cls.conn.cursor()
        cls.cur.execute('CREATE TABLE table_for_tests (first_attr int, second_attr varchar)')
        cls.cur.execute('INSERT INTO table_for_tests (first_attr, second_attr) VALUES (%s, %s)', (1, 'text1'))
        cls.conn.commit()

        cls.db = Database(**data_for_conn)

        cls.r_select = Request('SELECT * FROM table_for_tests', (), 'with_output')
        cls.r_insert = Request('INSERT INTO table_for_tests (first_attr, second_attr) '
                               'VALUES (%s, %s)', (2, 'text2'), 'without_output')

    def tearDown(self):
        self.conn.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.cur.execute('DROP TABLE table_for_tests')
        cls.conn.commit()
        cls.cur.close()
        cls.conn.close()

    def test_for_singleton(self):
        self.assertEqual(self.db, Database._Database__instance)
        self.assertRaises(ManyInstanceOfDatabaseError, Database)

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
