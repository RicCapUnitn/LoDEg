import unittest

# Add path in order to be able to do imports
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import system

class TestSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._system = system.LodegSystem()

    def test_system_initialzation(self):
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

    def test_modify_class_settings(self):
        try:
            self._system.modify_class_settings(**self._system._config_console)
            self.assertEqual(self._system._config_console, self._system._config)
            # Restore system settings
            self._system._config = self._system._config_default.copy()
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



if __name__ == '__main__':
    unittest.main()
