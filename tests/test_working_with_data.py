import unittest
from typing import Callable

from config import *
from interaction_with_db.manage_db import Database
from interaction_with_db.working_with_data import TablesManager, register_tables_manager
from other.exceptions import DontExistUnexecutedRequests
from work_with_models.models import SuperUser


class TestTablesManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_for_conn = {'database': DATABASE_NAME, 'user': DATABASE_USER, 'password': DATABASE_PASSWORD,
                         'host': DATABASE_HOST, 'port': DATABASE_PORT}
        cls.db = Database(**data_for_conn)
        cls.tb_manager = TablesManager(cls.db)
        cls.tb_manager._model = SuperUser('username', 'email', 'password')
        register_tables_manager(cls.tb_manager)

    def tearDown(self):
        self.db._Database__unexecuted_requests = []
        self.db._output = None

    def test_register_request(self):
        self.tb_manager._TablesManager__register_request('all')
        try:
            self.db._Database__unexecuted_requests[0]
        except IndexError:
            self.fail()

    def test_get_request_result(self):
        try:
            self.tb_manager._TablesManager__get_request_result('all')
        except DontExistUnexecutedRequests:
            pass
        except Exception:
            self.fail()

        case2 = self.tb_manager._TablesManager__get_request_result('some_method')
        self.assertIsNone(case2)

    def test_process_method(self):
        func = self.tb_manager._TablesManager__wrapper_process_method('all')
        self.assertIsInstance(func, Callable)

        func()
        self.assertIsNone(self.tb_manager._work_table)

    def test_getattr(self):
        self.assertRaises(AttributeError, self.tb_manager.__getattr__, 'some_method')
