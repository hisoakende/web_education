import unittest

from tests.utils_for_tests import get_some_students, hash_func_for_model
from user_interaction.services import *
from working_with_models.models import Subject, Grade, Student


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
        grades = [Grade(5, 1, english, datetime.date(2000, 1, 1)),
                  Grade(2, 1, maths, datetime.date(2000, 1, 2)),
                  Grade(2, 1, maths, datetime.date(2000, 1, 2))]
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
        self.assertEqual({'students': [None]}, State.cache)


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


class TestGetStudentFromGradingCommand(unittest.TestCase):

    def test_incorrect_student_number(self):
        State.clear_cache()
        self.assertRaises(InvalidData, get_student_from_grading_command, 0)
        self.assertRaises(InvalidData, get_student_from_grading_command, 1)

    def test_correct_student_number(self):
        some_student = Student('Владимир', 'Владимиров', 'Владимирович', 'some_email@email.com', 'a' * 64, 1)
        State.cache['students'][1] = some_student
        self.assertEqual(some_student, get_student_from_grading_command(1))


class TestValidateCommandChars(unittest.TestCase):

    def test_incorrect_command_chars(self):
        self.assertRaises(InvalidData, validate_command_chars, '5: 5(1!1!2022)')

    def test_correct_command_chars(self):
        self.assertIsNone(validate_command_chars('32: 5(10/10/2022), 3(5/9/2022); 20: 5(10/10/2022)'))


class TestValidateCommandParts(unittest.TestCase):

    def test_incorrect_command_parts(self):
        self.assertRaises(InvalidData, validate_command_parts, ['1234', '1234', ''])

    def test_correct_command_parts(self):
        self.assertIsNone(validate_command_parts(['1234', '1234', '1234']))


class TestValidateCommandForm(unittest.TestCase):

    def test_incorrect_command_form(self):
        self.assertRaises(InvalidData, validate_command_form, '5: 4(10/12/2022')

    def test_correct_command_form(self):
        self.assertIsNone(validate_command_form('10: 2(10/10/2022)'))


class TestValidateGradeAndDate(unittest.TestCase):

    def test_incorrect_grade_and_date(self):
        self.assertRaises(InvalidData, validate_grade_and_date, ['5', '20', '20'])

    def test_correct_grade_and_date(self):
        self.assertIsNone(validate_grade_and_date(['5', '1', '1', '2022']))


class TestValidateLocationOfSpecialCharsInDate(unittest.TestCase):

    def test_incorrect_location(self):
        self.assertRaises(InvalidDate, check_location_of_special_chars_in_date, '5/10)10/(')

    def test_correct_location(self):
        self.assertIsNone(check_location_of_special_chars_in_date('5(10/10/2022)'))


class TestCheckNumberOfSpecialCharsInDate(unittest.TestCase):

    def test_incorrect_number(self):
        self.assertRaises(InvalidDate, check_number_of_special_chars_in_date, '5((/10/10/2022))')

    def test_correct_number(self):
        self.assertIsNone(check_number_of_special_chars_in_date('5(10/10/2022)'))


class TestCheckDateInCurrentPeriod(unittest.TestCase):

    def test_date_not_in_current_dates(self):
        State.current_dates = [datetime.date(2022, 9, 1), datetime.date(2022, 9, 2)]
        self.assertRaises(InvalidDate, check_date_in_current_period, datetime.date(2022, 9, 3))

    def test_date_in_current_dates(self):
        State.current_dates = State.current_dates = [datetime.date(2022, 9, 1), datetime.date(2022, 9, 2)]
        self.assertIsNone(check_date_in_current_period(datetime.date(2022, 9, 1)))


class TestSplitGradeAndDate(unittest.TestCase):

    def test_for_correct_result(self):
        self.assertEqual((5, [2022, 10, 29]), split_grade_and_date('5(29/10/2022)'))


class TestProcessPartOfOneStudentCommand(unittest.TestCase):

    def test_for_correct_result(self):
        some_student = Student('Ученик', 'Некоторый', 'Некоторович', 'some@email', 'a' * 64, 1)
        State.cache['students'][1] = some_student
        expected_result = (some_student, ['5(28/10/2022)', '3(29/10/2022)'])
        self.assertEqual(expected_result, process_part_of_one_student_command('1:5(28/10/2022),3(29/10/2022)'))
        State.clear_cache()


class TestCreateDateFromCommandValues(unittest.TestCase):

    def test_incorrect_command_values(self):
        self.assertRaises(InvalidDate, create_date_from_command_values, [2022, 10, 32])

    def test_correct_command_values(self):
        expected_result = datetime.date(2022, 12, 31)
        self.assertEqual(expected_result, create_date_from_command_values([2022, 12, 31]))


class TestGetUserAndHisGradesFromCommand(unittest.TestCase):

    def test_for_correct_result(self):
        State.user = 1
        State.current_dates = [datetime.date(2022, 1, 1), datetime.date(2022, 1, 2)]
        student = Student('Ученик', 'Некоторый', 'Некоторович', 'some@email', 'a' * 64, 1)
        State.cache['students'].append(student)
        subject = Subject('Математика')
        grade1 = Grade(5, student, subject, datetime.date(2022, 1, 1))
        grade2 = Grade(3, student, subject, datetime.date(2022, 1, 2))
        expected_result = (student, [grade1, grade2])
        command = '1:5(1/1/2022),3(2/1/2022)'
        self.assertEqual(str(expected_result), str(get_user_and_his_grades_from_command(command, subject)))
        State.clear_cache()


class TestGradingCommandPreprocessing(unittest.TestCase):

    def test_for_correct_result(self):
        command = '10: 5(13/9/2022), 3(12/9/2022); 9: 3(13/9/2022), 2(12/9/2022)'
        expected_result = ['10:5(13/9/2022),3(12/9/2022)', '9:3(13/9/2022),2(12/9/2022)']
        self.assertEqual(expected_result, grading_command_preprocessing(command))


class TestParseStudentGradingCommand(unittest.TestCase):

    def test_for_correct_result(self):
        State.user = 1
        State.current_dates = [datetime.date(2022, 9, 13), datetime.date(2022, 9, 12)]
        student1 = Student('УченикОдин', 'НекоторыйОдин', 'НекоторовичОдин', 'some1@email', 'a' * 64, 1)
        student2 = Student('УченикДва', 'НекоторыйДва', 'НекоторовичДва', 'some2@email', 'b' * 64, 1)
        State.cache['students'].append(student1)
        State.cache['students'].append(student2)
        subject = Subject('Математика')
        grade1_1 = Grade(5, student1, subject, datetime.date(2022, 9, 13))
        grade1_2 = Grade(3, student1, subject, datetime.date(2022, 9, 12))
        grade2_1 = Grade(3, student2, subject, datetime.date(2022, 9, 13))
        grade2_2 = Grade(2, student2, subject, datetime.date(2022, 9, 12))
        expected_result = [(student1, [grade1_1, grade1_2]), (student2, [grade2_1, grade2_2])]
        command = '1: 5(13/9/2022), 3(12/9/2022); 2: 3(13/9/2022), 2(12/9/2022)'
        self.assertEqual(str(expected_result), str(parse_student_grading_command(command, subject)))
        State.clear_cache()


class TestRelatedModelStrRuToChoice(unittest.TestCase):

    def test_attr_is_teacher(self):
        result = get_related_model_str_ru_to_choice('teacher')
        expected_result = 'учителя'
        self.assertEqual(expected_result, result)

    def test_attr_is_classroom_teacher(self):
        result = get_related_model_str_ru_to_choice('classroom_teacher')
        expected_result = 'классного руководителя'
        self.assertEqual(expected_result, result)


class TestProcessValueFromAdminToChangeObj(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.some_model_class = type('SomeClass', (BaseModel,), {'db_table': 'some_table'})
        cls.some_model_class.__hash__ = hash_func_for_model

    def test_value_is_not_str(self):
        some_instance = self.some_model_class()
        result = process_value_from_admin_to_change_obj(some_instance, 'some_attr', self.some_model_class)
        expected_result = some_instance
        self.assertEqual(expected_result, result)

    def test_value_is_digit_and_attr_is_number(self):
        result = process_value_from_admin_to_change_obj('1234', 'number', self.some_model_class)
        expected_result = 1234
        self.assertEqual(expected_result, result)

    def test_value_is_incorrect_date(self):
        self.assertRaises(InvalidDate, process_value_from_admin_to_change_obj,
                          'ffd2v2v', 'start', Period)

    def test_value_is_correct_date(self):
        result = process_value_from_admin_to_change_obj('(31/8/2004)', 'start', Period)
        expected_result = datetime.date(2004, 8, 31)
        self.assertEqual(expected_result, result)
