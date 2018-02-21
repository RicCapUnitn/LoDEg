import unittest

# Add path in order to be able to do imports
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import system


class TestSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._system = system.LodegSystem()
        cls._test_course = 'course1'
        cls._test_valid_user = 'user0'
        cls._test_valid_session = 'user0-session0'

        cls._test_invalid_course = 'invalidCourse'
        cls._test_invalid_user = 'invalidUser'
        cls._test_invalid_session = 'invalidSession'

    def test_complete_extraction_query_mem_opt_no_ml(self):
        kwargs = {
            'keep_session_data': False,
            'keep_user_info': True,
            'query_mem_opt': True,
            'ml_autorun': False
        }
        self._system.executeCompleteExtraction(**kwargs)

    def test_complete_extraction_no_query_mem_opt_no_ml(self):
        kwargs = {
            'keep_session_data': False,
            'keep_user_info': True,
            'query_mem_opt': False,
            'ml_autorun': False
        }
        self._system.executeCompleteExtraction(**kwargs)

    def test_complete_extraction_query_mem_opt_ml(self):
        kwargs = {
            'keep_session_data': False,
            'keep_user_info': True,
            'query_mem_opt': True,
            'ml_autorun': True
        }
        self._system.executeCompleteExtraction(**kwargs)
