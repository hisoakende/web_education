import unittest

from interaction_with_db.manage_db import Database
from interaction_with_db.working_with_data import TablesManager
from tests.utils_for_tests import data_for_conn
from working_with_models.models import BaseModel


class TestTablesManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database(**data_for_conn)
        cls.tb_manager = TablesManager(cls.db)

    def tearDown(self):
        self.tb_manager._model = None
        self.tb_manager.arguments_for_request = {}
        self.tb_manager.method = None
        self.db._Database__unexecuted_requests = []
        self.tb_manager.execution = False

    @classmethod
    def tearDownClass(cls):
        Database._Singleton__instance = None
        TablesManager._Singleton__instance = None

    def test_check_for_kwargs_dont_exist(self):
        self.tb_manager.arguments_for_request = {'key': 'value'}
        self.assertRaises(TypeError, self.tb_manager._TablesManager__check_for_kwargs_dont_exist)
        self.tb_manager.arguments_for_request = {}
        self.assertIsNone(self.tb_manager._TablesManager__check_for_kwargs_dont_exist())

    def test_register_request(self):
        self.tb_manager._model = type('SomeModel', (BaseModel,), {'db_table': 'some_table'})
        self.tb_manager.method = 'all'
        self.tb_manager._TablesManager__register_request()
        self.assertNotEqual([], self.db._Database__unexecuted_requests)

    def test_check_execution_type(self):
        self.tb_manager.execution = '123'
        self.assertRaises(TypeError, self.tb_manager._TablesManager__check_execution_type)
        self.tb_manager.execution = True
        self.assertIsNone(self.tb_manager._TablesManager__check_execution_type())

    def test_set_execution_value(self):
        self.tb_manager._TablesManager__set_execution_value({'execution': True})
        self.assertTrue(self.tb_manager.execution)
        self.tb_manager._TablesManager__set_execution_value({})
        self.assertFalse(self.tb_manager.execution)

    def test_process_kwargs(self):
        self.tb_manager._TablesManager__process_kwargs(**{'execution': True})
        self.assertEqual({}, self.tb_manager.arguments_for_request)

    def test_getattr(self):
        self.assertRaises(AttributeError, self.tb_manager.__getattr__, 'some_method')
