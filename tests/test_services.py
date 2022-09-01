import unittest

from user_interaction.services import get_str_of_classes_for_msg


class TestGetStrOfClassesForMsg(unittest.TestCase):

    def test_for_correct_result(self):
        data = [('11C', '1'), ('10A', '2')]
        result = get_str_of_classes_for_msg(data)
        expected_result = '[1] - 11C\n[2] - 10A'
        self.assertEqual(expected_result, result)
