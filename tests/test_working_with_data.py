import unittest

from db_interaction.manage_db import Database
from db_interaction.working_with_data import TablesManager
from tests.utils_for_tests import data_for_conn, get_some_model, init_for_main_model, init_for_related_model
from working_with_models.models import BaseModel


class TestTablesManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database(**data_for_conn)
        cls.tb_manager = TablesManager(cls.db)

    def tearDown(self):
        self.tb_manager._model = None
        self.tb_manager.arguments_for_request = {}
        self.tb_manager._TablesManager__method = None
        self.db._Database__unexecuted_requests = []
        self.tb_manager.execution = False

    @classmethod
    def tearDownClass(cls):
        Database._Singleton__instance = None
        TablesManager._Singleton__instance = None

    def test_get_request_result_if_necessary(self):
        self.tb_manager._TablesManager__method = 'get'
        self.tb_manager._TablesManager__db._output = [(0, 1, 1, 2)]
        self.tb_manager._model = get_some_model()
        self.tb_manager._model.__init__ = init_for_main_model
        self.tb_manager._model.related_data['related_model'].__init__ = init_for_related_model
        expected_result1 = 'MainModel(pk: 0, related_model: RelatedModel(pk: 1, some_attr: 2))'
        result1 = self.tb_manager._TablesManager__get_request_result_if_necessary().__str__()
        self.assertEqual(expected_result1, result1)

        self.tb_manager._TablesManager__method = 'get'
        self.tb_manager._TablesManager__db._output = [(0, 1, 1, 2), (1, 1, 1, 2)]
        self.assertRaises(ValueError, self.tb_manager._TablesManager__get_request_result_if_necessary)

        self.tb_manager._TablesManager__method = 'filter'
        self.tb_manager._TablesManager__db._output = [(0, 1, 1, 2)]
        expected_result2 = '[MainModel(pk: 0, related_model: RelatedModel(pk: 1, some_attr: 2))]'
        result2 = self.tb_manager._TablesManager__get_request_result_if_necessary().__str__()
        self.assertEqual(expected_result2, result2)

    def test_check_for_kwargs_dont_exist(self):
        self.tb_manager.arguments_for_request = {'key': 'value'}
        self.assertRaises(TypeError, self.tb_manager._TablesManager__check_for_kwargs_dont_exist)
        self.tb_manager.arguments_for_request = {}
        self.assertIsNone(self.tb_manager._TablesManager__check_for_kwargs_dont_exist())

    def test_register_request(self):
        self.tb_manager._model = type('SomeModel', (BaseModel,), {'db_table': 'some_table'})
        self.tb_manager._TablesManager__method = 'all'
        self.tb_manager._TablesManager__register_request()
        self.assertNotEqual([], self.db._Database__unexecuted_requests)

    def test_is_method_with_result(self):
        self.tb_manager._TablesManager__method = 'get'
        self.assertTrue(self.tb_manager._TablesManager__is_method_with_result())
        self.tb_manager._TablesManager__method = 'create'
        self.assertFalse(self.tb_manager._TablesManager__is_method_with_result())

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
