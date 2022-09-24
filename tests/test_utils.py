import unittest

from other.utils import *
from tests.utils_for_tests import get_some_model, init_for_main_model, init_for_related_model
from working_with_models.models import BaseModel


class TestSingleton(unittest.TestCase):

    @classmethod
    def tearDownClass(cls):
        Singleton._Singleton__instance = None

    def test_for_singleton(self):
        self.assertEqual(Singleton(), Singleton._Singleton__instance)
        self.assertRaises(ManyInstanceOfClassError, Singleton)


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
    """
    Тестируются методы 'get_data_for_create_saving_request', 'add_data_to_lists',
    'process_pair_of_attr_and_value'
    """

    @classmethod
    def setUpClass(cls):
        cls.some_model_class = type('SomeClass', (BaseModel,), {'db_table': 'some_table'})
        cls.some_model = cls.some_model_class()

    def tearDown(self):
        self.some_model.__dict__ = {}
        self.some_model.__class__.related_data = ()

    def test_empty_result(self):
        self.assertEqual(([], []), get_data_to_write_to_db(self.some_model))

    def test_pk_attr(self):
        self.some_model.pk = 1
        self.assertEqual(([], []), get_data_to_write_to_db(self.some_model))

    def test_attr_in_related_data(self):
        self.some_model.__class__.related_data = ('some_attr',)
        self.some_model.some_attr = self.some_model_class()
        self.some_model.some_attr.pk = 2
        expected_result = [get_pk_related_entry(self.some_model.some_attr)]
        self.assertEqual(expected_result, get_data_to_write_to_db(self.some_model)[1])


class TestGetStringsForSql(unittest.TestCase):

    def test_for_correct_result(self):
        result = get_strings_for_sql(2)
        self.assertEqual(['{}, {}', '%s, %s'], result)


class TestGetIdentifiersForRequest(unittest.TestCase):

    def test_for_correct_result(self):
        result = get_identifiers('first_attr', 'second_attr')
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
        s = ' '.join('JOIN {} ON {}.{} = {}.{}' for _ in range(2))
        expected_result = (s, [
            Identifier('other_table1'), Identifier('main_table'),
            Identifier('attr1_id'), Identifier('other_table1'), Identifier('id'),
            Identifier('other_table2'), Identifier('main_table'),
            Identifier('attr2_id'), Identifier('other_table2'), Identifier('id')
        ])
        result = get_data_for_join_part_of_sql(main_model)
        self.assertEqual(expected_result, result)


class TestGetRawLineLikeDict(unittest.TestCase):

    def test_for_correct_result(self):
        raw_data = (0, 1, 2)
        generator = get_value_from_collection(raw_data)
        some_model = type('SomeModel', (BaseModel,),
                          {'db_table': 'some_table', 'attributes': [f'attr{x}' for x in range(3)]})
        expected_result = {'attr0': 0, 'attr1': 1, 'attr2': 2}
        result = get_raw_line_like_dict(generator, some_model)
        self.assertEqual(expected_result, result)


class TestGetAllOutputLikeDict(unittest.TestCase):

    def test_for_correct_result(self):
        raw_data = [(0, 1, 1, 2), (10, 11, 11, 12)]  # начиная со второго индекса, значения - атрибуты связанной модели
        model = get_some_model()
        expected_result = [{'pk': 0, 'related_model': {'pk': 1, 'some_attr': 2}},
                           {'pk': 10, 'related_model': {'pk': 11, 'some_attr': 12}}]
        result = get_all_output_like_dict(model, raw_data)
        self.assertEqual(expected_result, result)


class TestProcessRawLineOfOutput(unittest.TestCase):

    def test_for_correct_result(self):
        raw_line = (0, 1, 1, 2)
        model = get_some_model()
        expected_result = {'pk': 0, 'related_model': {'pk': 1, 'some_attr': 2}}
        result = process_raw_line_of_output(raw_line, model)
        self.assertEqual(expected_result, result)


class TestReplacePkWithDict(unittest.TestCase):

    def test_for_correct_result(self):
        raw_dict_line = {'pk': 1, 'related_model': 2}
        generator = get_value_from_collection((2, 3))
        model = get_some_model()
        expected_result = {'pk': 1, 'related_model': {'pk': 2, 'some_attr': 3}}
        replace_pk_with_dict(raw_dict_line, generator, model)
        self.assertEqual(expected_result, raw_dict_line)


class TestGetAllOutputLikeModel(unittest.TestCase):

    def test_for_correct_result(self):
        output = [{'pk': 0, 'related_model': {'pk': 1, 'some_attr': 2}},
                  {'pk': 10, 'related_model': {'pk': 11, 'some_attr': 12}}]
        model = get_some_model()
        model.__init__ = init_for_main_model
        model.related_data['related_model'].__init__ = init_for_related_model
        expected_result = '[' \
                          'MainModel(pk: 0, related_model: RelatedModel(pk: 1, some_attr: 2)), ' \
                          'MainModel(pk: 10, related_model: RelatedModel(pk: 11, some_attr: 12))' \
                          ']'
        result = get_all_output_like_model(model, output)
        self.assertEqual(expected_result, result.__str__())


class TestProcessDictLine(unittest.TestCase):

    def test_for_correct_result(self):
        output = {'pk': 0, 'related_model': {'pk': 1, 'some_attr': 2}}
        model = get_some_model()
        model.__init__ = init_for_main_model
        model.related_data['related_model'].__init__ = init_for_related_model
        expected_result = 'MainModel(pk: 0, related_model: RelatedModel(pk: 1, some_attr: 2))'
        result = process_dict_line(model, output)
        self.assertEqual(expected_result, result.__str__())


class TestGetDictLineLikeModel(unittest.TestCase):

    def test_for_correct_result(self):
        output = {'pk': 1, 'some_attr': 2}
        model = get_some_model().related_data['related_model']
        model.__init__ = init_for_related_model
        expected_result = 'RelatedModel(pk: 1, some_attr: 2)'
        result = get_dict_line_like_model(model, output)
        self.assertEqual(expected_result, result.__str__())


class TestGetTableAndColumnForWherePart(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.model = get_some_model()

    def test_for_condition_with_prefix(self):
        expected_result = ('related_table', 'some_condition')
        result = get_table_and_column_for_where_part(self.model, 'related_model__some_condition')
        self.assertEqual(expected_result, result)

    def test_for_condition_without_prefix(self):
        expected_result = ('main_table', 'some_condition')
        result = get_table_and_column_for_where_part(self.model, 'some_condition')
        self.assertEqual(expected_result, result)


class ProcessAttrAndValueForWherePart(unittest.TestCase):

    def test_for_pk_is_id(self):
        result = process_data_for_where_part(get_some_model(), 'pk', 123)[0]
        self.assertEqual('id', result)


class TestGetDataForWherePartOfSql(unittest.TestCase):

    def test_for_correct_result(self):
        s = 'WHERE {}.{} = %s AND {}.{} = %s'
        identifiers = [Identifier('main_table'), Identifier('id'),
                       Identifier('related_table'), Identifier('some_attr')]
        arguments = [1, datetime.date(2004, 8, 31)]
        expected_result = (s, identifiers, arguments)
        model = get_some_model()
        result = get_data_for_where_part_of_sql(model, pk=1, related_model__some_attr=datetime.date(2004, 8, 31))
        self.assertEqual(expected_result, result)


class TestGetDataForSetPartOfSql(unittest.TestCase):

    def test_for_correct_result(self):
        expected_result = ('SET {} = %s', [Identifier('related_model_id')], [1])
        model = get_some_model()()
        model.related_model = 1
        result = get_data_for_set_part_of_sql(model)
        self.assertEqual(expected_result, result)
