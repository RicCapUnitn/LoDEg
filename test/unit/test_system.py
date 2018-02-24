import unittest

# Add path in order to be able to do imports
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

from configure.configurations import DefaultConfigurationsHolder
import system


class TestSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._system = system.LodegSystem()
        cls._test_valid_course = 'course1'
        cls._test_invalid_course = 'CourseNotPresent'
        cls._test_user = 'user0'
        cls._system.executeCompleteExtraction()
        cls._default_configurations_holder = DefaultConfigurationsHolder()

    def test_get_system_settings(self):
        settings = self._system.getSystemSettings()
        default_settings = self._default_configurations_holder.get('default')
        self.assertEqual(settings, default_settings)

    def test_modify_class_settings(self):
        self._system.modify_class_settings(
            **self._default_configurations_holder.get('console'))
        self.assertEqual(self._default_configurations_holder.get(
            'console'), self._system._config.getSettings())
        # Restore system settings
        self._system._config = self._default_configurations_holder.get(
            'default')

    def test_getLastUpdate(self):
        last_update = self._system.getLastUpdate()
        self.assertRegex(last_update, r"\d+-\d+-\d+ \d+:\d+:\d+.*")

    def test_get_data_all(self):
        data = self._system.getData()
        self.assertNotEqual(data, None)
        self.assertNotEqual(data, {})

    def test_get_data_course(self):
        data = self._system.getData(course=self._test_valid_course)
        self.assertNotEqual(data, None)
        self.assertNotEqual(data, {})

###############################################################################
#                                  HEADERS                                    #
###############################################################################

    # getUsers
    def test_getUsers_with_course_param_not_set(self):
        """Get the number of users of the system"""
        users = self._system.getUsers()
        self.assertEqual(users, 3)

    def test_getUsers_with_valid_course_param_set(self):
        users = self._system.getUsers(self._test_valid_course)
        self.assertEqual(sorted(users), ['user0', 'user1', 'user2'])

    def test_getUsers_with_invalid_course_param_set(self):
        users = self._system.getUsers(self._test_invalid_course)
        self.assertEqual(users, [])

    # getUserSessionsHeaders
    def test_getUserSessionsHeaders_with_valid_course_and_valid_user(self):
        session_headers = self._system.getUserSessionsHeaders(
            self._test_valid_course, self._test_user)
        self.assertEqual(len(session_headers), 3)

    def test_getUserSessionsHeaders_with_invalid_course_and_valid_user(self):
        sessions_headers = self._system.getUserSessionsHeaders(
            self._test_invalid_course, self._test_user)
        self.assertEqual(sessions_headers, [])

    # getLessonsHeaders
    def test_getLessonsHeaders_with_valid_course(self):
        lessons_headers = self._system.getLessonsHeaders(
            self._test_valid_course)
        self.assertEqual(sorted(lessons_headers), [
                         'lesson1', 'lesson2', 'lesson3'])

    def test_getLessonsHeaders_with_invalid_course(self):
        lessons_headers = self._system.getLessonsHeaders(
            self._test_invalid_course)
        self.assertEqual(lessons_headers, [])

    # getCourses
    def test_getCourses(self):
        courses = self._system.getCourses()
        self.assertEqual(sorted(courses), ['course1', 'course2'])


if __name__ == '__main__':
    unittest.main()
