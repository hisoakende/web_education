import unittest

from config import *
from exceptions import ManyInstanceOfDatabaseError
from manage_db import Database


class TestDatabase(unittest.TestCase):

    def test_for_singleton(self):
        db = Database(DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD,
                      DATABASE_HOST, DATABASE_PORT)
        self.assertEqual(db, Database._Database__instance)
        self.assertRaises(ManyInstanceOfDatabaseError, Database)
