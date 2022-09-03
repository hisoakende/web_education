import datetime
import unittest

from user_interaction.services import get_str_of_classes_for_msg, get_subjects_for_table, State, get_empty_table_dict, \
    fill_raw_table, get_str_grades_for_table, get_str_date_for_table
from working_with_models.models import Subject, Grade


class TestGetStrOfClassesForMsg(unittest.TestCase):

    def test_for_correct_result(self):
        data = [('11C', '1'), ('10A', '2')]
        result = get_str_of_classes_for_msg(data)
        expected_result = '[1] - 11C\n[2] - 10A'
        self.assertEqual(expected_result, result)


class TestGetSubjectsForTable(unittest.TestCase):

    def test_for_correct_result(self):
        data = [Subject('Английский язык'), Subject('Математика')]
        english, maths = data
        expected_result = {english: [], maths: []}
        self.assertEqual(expected_result, get_subjects_for_table(data))


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
        fill_raw_table(empty_table, grades)
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
