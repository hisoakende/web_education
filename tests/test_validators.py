import unittest

from working_with_models.validators import BaseValidator, PersonalDataValidator, EmailValidator


class TestBaseValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = BaseValidator()
        cls.validator.name = 'attr'

    def test_check_for_characters(self):
        func = self.validator.check_for_characters
        self.assertRaises(ValueError, func, {'a', 'b', 'c'}, 'ab')
        self.assertRaises(ValueError, func, {'a', 'c'}, {'a', 'b'})
        self.assertIsNone(func({'1', '2', '3'}, ['1', '2', '3', '4']))
        self.assertIsNone(func({'1', '2'}, ('1', '2')))

    def test_check_for_string(self):
        func = self.validator.check_for_string
        for type_ in (set, int, list, dict, tuple, bool):
            self.assertRaises(TypeError, func, type_())
        self.assertIsNone(func('123'))


class TestPersonalDataValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = PersonalDataValidator()
        cls.validator.name = 'attr'

    def test_check_for_length(self):
        self.assertRaises(ValueError, self.validator.check_for_length, 'a' * 20)
        self.assertIsNone(self.validator.check_for_length('a'))

    def test_set(self):
        class_ = type('SomeClass', (), {})
        instance = class_()
        self.validator.__set__(instance, 'ДМИТРИЙ')
        self.assertEqual('Дмитрий', instance.__dict__['attr'])


class TestEmailValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = EmailValidator()
        cls.validator.name = 'attr'

    def test_check_for_special_characters(self):
        self.assertRaises(ValueError, self.validator.check_for_special_characters, 'some_email')
        self.assertIsNone(self.validator.check_for_special_characters('some_mail@mail.com'))

    def test_set(self):
        class_ = type('SomeClass', (), {})
        instance = class_()
        self.validator.__set__(instance, 'some_email@mail.com')
        self.assertEqual('some_email@mail.com', instance.__dict__['attr'])
