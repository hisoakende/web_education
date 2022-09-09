import datetime
import unittest

from prettytable import PrettyTable

from tests.utils_for_tests import get_some_students
from user_interaction.services import get_str_of_choices, set_columns_in_table, State, get_empty_table_dict, \
    fill_raw_table_with_grades, get_str_grades_for_table, get_str_date_for_table, \
    get_prepared_students_field_names_view, prepare_pretty_table_for_grades
from working_with_models.models import Subject, Grade, Student


class TestGetStrOfClassesForMsg(unittest.TestCase):

    def test_for_correct_result(self):
        data = [('11C', '1'), ('10A', '2')]
        result = get_str_of_choices(data)
        expected_result = '[1] - 11C\n[2] - 10A'
        self.assertEqual(expected_result, result)


class TestGetSubjectsForTable(unittest.TestCase):

    def test_for_correct_result(self):
        data = [Subject('Английский язык'), Subject('Математика')]
        english, maths = data
        expected_result = {english: [], maths: []}
        self.assertEqual(expected_result, set_columns_in_table(data))


class TestEmptyTableDict(unittest.TestCase):

    def test_for_correct_result(self):
        data = [Subject('Английский язык'), Subject('Математика')]
        english, maths = data
        State.current_dates = [datetime.date(2000, 1, 1), datetime.date(2000, 1, 2)]
        expected_result = {datetime.date(2000, 1, 1): {english: [], maths: []},
                           datetime.date(2000, 1, 2): {english: [], maths: []}}
        self.assertEqual(expected_result, get_empty_table_dict(data))


class TestFillRawTable(unittest.TestCase):

    def test_for_correct_result(self):
        data = [Subject('Английский язык'), Subject('Математика')]
        english, maths = data
        expected_result = {datetime.date(2000, 1, 1): {english: ['5'], maths: []},
                           datetime.date(2000, 1, 2): {english: [], maths: ['2', '2']}}
        empty_table = get_empty_table_dict(data)
        grades = [Grade(5, 1, english, 1, datetime.date(2000, 1, 1)),
                  Grade(2, 1, maths, 1, datetime.date(2000, 1, 2)),
                  Grade(2, 1, maths, 1, datetime.date(2000, 1, 2))]
        fill_raw_table_with_grades(empty_table, grades, 'subject')
        self.assertEqual(expected_result, empty_table)


class TestGetStrGradesForTable(unittest.TestCase):

    def test_for_correct_result(self):
        grades = {Subject('Французский язык'): ['5'],
                  Subject('Английский язык'): ['2', '2']}
        expected_result = ['5', '2/2']
        self.assertEqual(expected_result, get_str_grades_for_table(grades))


class TestGetStrDateForTable(unittest.TestCase):

    def test_for_correct_result(self):
        expected_result = '1 Января 2000'
        self.assertEqual(expected_result, get_str_date_for_table(datetime.date(2000, 1, 1)))


class TestState(unittest.TestCase):

    def test_clear_cache(self):
        State.cache['some_key'] = 'some_value'
        State.clear_cache()
        self.assertEqual({'students_pks': {0: None}}, State.cache)


class TestGetPrepareDStudentsFieldNamesView(unittest.TestCase):

    def test_for_correct_result(self):
        raw_students = get_some_students()
        result = get_prepared_students_field_names_view(raw_students)
        expected_result = [f'{x}: Фамилия И. О.' for x in range(1, 8)]
        self.assertEqual(expected_result, result)


class TestPreparePrettyTableForGrades(unittest.TestCase):

    def test_objs_are_students(self):
        pretty_table = PrettyTable()
        students = get_some_students()
        expected_result = ['-'] + [f'{x}: Фамилия И. О.' for x in range(1, 8)]
        State.clear_cache()
        prepare_pretty_table_for_grades(pretty_table, students)
        self.assertEqual(expected_result, pretty_table.field_names)

    def test_obj_are_subjects(self):
        pretty_table = PrettyTable()
        subjects = [Subject('Математика'), Subject('Английский язык')]
        expected_result = ['-', Subject('Математика'), Subject('Английский язык')]
        prepare_pretty_table_for_grades(pretty_table, subjects)
        self.assertEqual(expected_result, pretty_table.field_names)
