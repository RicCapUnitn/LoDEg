import unittest

# Add path in order to be able to do imports
import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import system

class TestSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._system = system.LodegSystem(modality='console')

    def test_system_initialzation(self):
        if self._system == None:
            return self.fail()

    def test_system_complete_extraction(self):
        try:
            self._system.executeCompleteExtraction()
        except:
            return self.fail()

if __name__ == '__main__':
    unittest.main()
