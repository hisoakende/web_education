import unittest
from typing import Callable

from interaction_with_db.manage_db import Database
from interaction_with_db.working_with_data import TablesManager, register_tables_manager
from other.data_structures import Request
from tests.utils_for_tests import *
from working_with_models.models import BaseModel


class TestTablesManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn, cls.cur = prepare_db()
        cls.db = Database(**data_for_conn)
        cls.tb_manager = TablesManager(cls.db)
        register_tables_manager(cls.tb_manager)

    def tearDown(self):
        self.db._Database__unexecuted_requests = []
        self.db._output = None

    def setUp(self):
        self.tb_manager._model = type('SomeModel', (BaseModel,), {'db_table': 'table_for_tests'})

    @classmethod
    def tearDownClass(cls):
        clean_db(cls.conn, cls.cur)
        Database._Singleton__instance = None
        TablesManager._Singleton__instance = None
        BaseModel._manager = None

    def test_register_request(self):
        self.tb_manager._TablesManager__register_request('all')
        try:
            self.db._Database__unexecuted_requests[0]
        except IndexError:
            self.fail()

    def test_get_request_result(self):
        self.db.add_unexecuted_request(
            Request(SQL('SELECT * FROM {}').format(Identifier('table_for_tests')), (), 'with_output'))
        case1 = self.tb_manager._TablesManager__get_request_result('all')
        self.assertIsNotNone(case1)
        case2 = self.tb_manager._TablesManager__get_request_result('some_method')
        self.assertIsNone(case2)

    def test_process_method(self):
        func = self.tb_manager._TablesManager__wrapper_process_method('all')
        self.assertIsInstance(func, Callable)
        TablesManager._TablesManager__methods_with_result = ()
        func()
        self.assertIsNone(self.tb_manager._model)

    def test_getattr(self):
        self.assertRaises(AttributeError, self.tb_manager.__getattr__, 'some_method')
