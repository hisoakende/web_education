import unittest

from tests.utils_for_tests import get_some_instance
from working_with_models.validators import *


class TestBaseValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = BaseValidator()
        cls.validator.name = 'attr'

    def test_check_for_characters(self):
        func = self.validator.check_for_characters
        self.assertRaises(ValueError, func, 'abc', 'ab')
        self.assertRaises(ValueError, func, 'ac', {'a', 'b'})
        self.assertIsNone(func('123', ['1', '2', '3', '4']))
        self.assertIsNone(func('12', ('1', '2')))

    def test_check_for_length(self):
        self.assertRaises(ValueError, self.validator.check_for_range, 21, 0, 20)
        self.assertRaises(ValueError, self.validator.check_for_range, 1, 5, 20)

        self.assertIsNone(self.validator.check_for_range(1, 1, 20))

    def test_check_for_string(self):
        func = self.validator.check_for_string
        for type_ in (set, int, list, dict, tuple, bool):
            self.assertRaises(TypeError, func, type_())
        self.assertIsNone(func('123'))


class TestPersonalDataValidator(unittest.TestCase):

    def setUp(self):
        self.validator = PersonalDataValidator()
        self.validator.name = 'attr'

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 'ДМИТРИЙ')
        self.assertEqual('Дмитрий', instance.attr)


class TestEmailValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = EmailValidator()
        cls.validator.name = 'attr'

    def test_check_for_at(self):
        self.assertRaises(ValueError, self.validator.check_for_at, 'some_email')
        self.assertIsNone(self.validator.check_for_at('some_email@mail.com'))

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 'some_email@mail.com')
        self.assertEqual('some_email@mail.com', instance.attr)


class TestPasswordValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = PasswordValidator()
        cls.validator.name = 'attr'

    def test_check_for_certain_characters(self):
        self.assertRaises(ValueError, self.validator.check_for_certain_characters, 'some_password', '0123456789')
        self.assertIsNone(self.validator.check_for_certain_characters('password1', '0123456789'))

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 'PASSword1234!!!!')
        self.assertEqual('PASSword1234!!!!', instance.attr)


class TestClassNumberValidator(unittest.TestCase):

    def setUp(self):
        self.validator = ClassNumberValidator()
        self.validator.name = 'attr'

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 4)
        self.assertEqual(4, instance.attr)


class TestClassLetterValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = ClassLetterValidator()
        cls.validator.name = 'attr'

    def test_check_for_correct_letter(self):
        self.assertRaises(ValueError, self.validator.check_for_correct_letter, 'abcd')
        self.assertIsNone(self.validator.check_for_correct_letter('г'))

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 'а')
        self.assertEqual('А', instance.attr)


class TestSubjectNameValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = SubjectNameValidator()
        cls.validator.name = 'attr'

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 'математИКА')
        self.assertEqual('Математика', instance.attr)


class TestGradeValueValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = GradeValueValidator()
        cls.validator.name = 'attr'

    def test_set(self):
        instance = get_some_instance()
        self.validator.__set__(instance, 3)
        self.assertEqual(3, instance.attr)
