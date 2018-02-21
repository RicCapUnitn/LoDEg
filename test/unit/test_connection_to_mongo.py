import unittest

# Add path in order to be able to do imports
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import connection_to_mongo


class TestDbConnection(unittest.TestCase):

    def test_default_connection(self):
        connection_to_mongo.connect_to_mongo()

    def test_connection_with_authentication(self):
        connection_to_mongo.connect_to_mongo(username='test', password='test')
