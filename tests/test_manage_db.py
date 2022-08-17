import unittest

from interaction_with_db.manage_db import *
from .utils_for_tests import *


class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn, cls.cur = prepare_db()
        cls.db = Database(**data_for_conn)
        cls.r_select = Request(SQL('SELECT * FROM {}').format(Identifier('table_for_tests')), [], 'with_output')
        cls.r_insert = Request(SQL('INSERT INTO {} ({}, {}) VALUES (%s, %s)').format(
            Identifier('table_for_tests'), Identifier('first_attr'),
            Identifier('second_attr')), [2, 'text2'], 'without_output')

    def tearDown(self):
        self.db._Database__unexecuted_requests = []
        self.conn.rollback()

    @classmethod
    def tearDownClass(cls):
        clean_db(cls.conn, cls.cur)
        Database._Singleton__instance = None

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

    def test_add_unexecuted_request(self):
        self.assertRaises(TypeError, self.db.add_unexecuted_request, 123)
        self.db.add_unexecuted_request(Request(SQL('').format(Identifier('')), [], 'with_output'))
        self.assertTrue(bool(self.db._Database__unexecuted_requests))
