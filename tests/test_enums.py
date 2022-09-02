import unittest

from user_interaction.enums import get_base_main_menu_choices, base_main_menu_choice


class TestGetBaseMainMenuChoices(unittest.TestCase):

    def test_for_correct_result(self):
        """Ожидаемый результат зависит от перемаенной 'base_main_menu_choice'"""
        expected_result = [('exit', '0')]
        self.assertEqual(expected_result, get_base_main_menu_choices())
