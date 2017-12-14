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
        cls._system = system.LodegSystem(debug=False)

    def test_system_initialization(self):
        if self._system == None:
            return self.fail()

    def test_system_complete_extraction(self):
        try:
            self._system.executeCompleteExtraction()
        except:
            return self.fail()

    def test_get_system_settings(self):
        try:
            settings = self._system.getSystemSettings()
            self.assertEqual(settings, self._system._config)
        except:
            return self.fail()

    def test_get_data_all(self):
        try:
            data = self._system.getData()
            self.assertNotEqual(data, None)
            self.assertNotEqual(data, {})
        except:
            return self.fail()

    def test_get_data_course(self):
        try:
            data = self._system.getData()
            self.assertNotEqual(data, None)
            self.assertNotEqual(data, {})
        except:
            return self.fail()

    # def test_json_export(self):
        #system.export_data(export_type='json', pretty_printing=True, course='course1',user='user1', selected_keys=['notes_per_type', 'number_of_notes'])


if __name__ == '__main__':
    unittest.main()
