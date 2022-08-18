import unittest

from other.utils import *
from working_with_models.models import BaseModel


class TestSingleton(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        Singleton._Singleton__instance = None

    def test_for_singleton(self):
        self.assertEqual(Singleton(), Singleton._Singleton__instance)
        self.assertRaises(ManyInstanceOfClassError, Singleton)


class TestProcessDateForRequest(unittest.TestCase):

    def test_function_result(self):
        result = process_date_for_request(datetime.date(year=2004, month=8, day=31))
        self.assertEqual('2004/8/31', result)


class TestGetPkRelatedEntry(unittest.TestCase):

    def test_int_value(self):
        case1 = get_pk_related_entry(1)
        self.assertEqual(1, case1)

    def test_base_model_value(self):
        some_model = type('SomeModel', (BaseModel,), {'db_table': 'some_table'})()
        some_model.pk = 2
        case2 = get_pk_related_entry(some_model)
        self.assertEqual(2, case2)


class TestGetDataForCreateSavingRequest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.some_model_class = type('SomeClass', (BaseModel,), {'db_table': 'some_table'})
        cls.some_model = cls.some_model_class()

    def tearDown(self):
        self.some_model.__dict__ = {}
        self.some_model.__class__.related_data = ()

    def test_empty_result(self):
        self.assertEqual(([], []), get_data_for_create_saving_request(self.some_model))

    def test_pk_attr(self):
        self.some_model.pk = 1
        self.assertEqual(([], []), get_data_for_create_saving_request(self.some_model))

    def test_attr_in_related_data(self):
        self.some_model.__class__.related_data = ('some_attr',)
        self.some_model.some_attr = self.some_model_class()
        self.some_model.some_attr.pk = 2
        expected_result = [get_pk_related_entry(self.some_model.some_attr)]
        self.assertEqual(expected_result, get_data_for_create_saving_request(self.some_model)[1])

    def test_value_is_date(self):
        some_attr = datetime.date(year=2004, month=8, day=31)
        self.some_model.some_attr = some_attr
        expected_result = [process_date_for_request(some_attr)]
        self.assertEqual(expected_result, get_data_for_create_saving_request(self.some_model)[1])


class TestGetStringsForSql(unittest.TestCase):

    def test_for_correct_result(self):
        result = get_strings_for_sql(2)
        self.assertEqual(['{}, {}', '%s, %s'], result)


class TestGetIdentifiersForRequest(unittest.TestCase):

    def test_for_correct_result(self):
        result = get_identifiers_for_request(['first_attr', 'second_attr'])
        expected_result = [Identifier('first_attr'), Identifier('second_attr')]
        self.assertEqual(expected_result, result)


class TestGetDataForJoinPartOfSql(unittest.TestCase):

    def test_for_correct_result(self):
        main_model = type('MainModel', (BaseModel,), {'db_table': 'main_table'})()
        other_model1_class = type('OtherModel1', (BaseModel,), {'db_table': 'other_table1'})
        other_model2_class = type('OtherModel2', (BaseModel,), {'db_table': 'other_table2'})
        main_model.attr1 = other_model1_class()
        main_model.attr2 = other_model2_class()
        main_model.related_data = {'attr1': other_model1_class, 'attr2': other_model2_class}
        expected_result = ('JOIN {} ON {}.{} = {}.id ' * 2, [
            Identifier('other_table1'), Identifier('main_table'),
            Identifier('attr1_id'), Identifier('other_table1'),
            Identifier('other_table2'), Identifier('main_table'),
            Identifier('attr2_id'), Identifier('other_table2')
        ])
        result = get_data_for_join_part_of_sql(main_model)
        self.assertEqual(expected_result, result)
