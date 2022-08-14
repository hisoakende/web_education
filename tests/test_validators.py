import unittest

from working_with_models.validators import BaseValidator, PersonalDataValidator, EmailValidator, PasswordValidator


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
        self.assertRaises(ValueError, self.validator.check_for_length, 'a' * 21, 0, 20)
        self.assertRaises(ValueError, self.validator.check_for_length, '', 5, 20)

        self.assertIsNone(self.validator.check_for_length('a', 1, 20))

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

    def test_set(self):
        class_ = type('SomeClass', (), {})
        instance = class_()
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
        class_ = type('SomeClass', (), {})
        instance = class_()
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
        class_ = type('SomeClass', (), {})
        instance = class_()
        self.validator.__set__(instance, 'PASSword1234!!!!')
        self.assertEqual('PASSword1234!!!!', instance.attr)
