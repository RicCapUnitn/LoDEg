import unittest

# Add path in order to be able to do imports
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import system
import copy
from exceptions import ImportException, ExportException
import import_export

test_system = system.LodegSystem()

systemInfo_mockup = {
    'courses': {
        'test_course': {
            'users': {
                'test_user': {
                    'sessions': {
                        'test_session': {
                            "notes_per_type": {
                                "handwritten": 0,
                                "text": 0
                            }
                        }
                    },
                    "notes_per_type": {
                        "handwritten": 0,
                        "text": 0
                    }
                }
            },
            "notes_per_type": {
                "handwritten": 0,
                "text": 0
            },
            "last_update": "2018-02-26T17:16:57.692736"
        }
    },
    "last_update": "2018-02-26T17:16:57.740225"
}


class TestLibJSONImport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._base_systemInfo = {
            'courses': {}, 'last_update': '2018-02-26T17:16:57.740225'}

    def setUp(self):
        self.test_systemInfo = copy.deepcopy(self._base_systemInfo)

    def test_import_file_not_found(self):
        expected_error_message = 'File not found: unknown.json'
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(
                self.test_systemInfo, 'unknown.json')

    def test_import_file_format_not_supported(self):
        expected_error_message = 'File format not supported'
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(
                self.test_systemInfo, 'not_supported.xml')

    def test_json_import_corrupted_metadata(self):
        expected_error_message = 'The file is corrupted and does not contain the appropriate metadata'
        test_file = './test/unit/test_data/corrupted_metadata.json'
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(self.test_systemInfo, test_file)

    def test_json_import_system_valid(self):
        test_file = './test/unit/test_data/system_valid.json'
        result = import_export.import_data(self.test_systemInfo, test_file)
        self.assertDictEqual(result, systemInfo_mockup)

    def test_json_import_course_valid(self):
        test_file = './test/unit/test_data/course_valid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        systemInfo_populated['courses'] = {}
        result = import_export.import_data(self.test_systemInfo, test_file)
        self.assertDictEqual(result, systemInfo_mockup)

    def test_json_import_course_invalid(self):
        expected_error_message = 'Metadata are corrupted; the file cannot be imported'
        test_file = './test/unit/test_data/course_invalid.json'
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(self.test_systemInfo, test_file)

    def test_json_import_course_malformed(self):
        expected_error_message = 'Some layers above the level you are inserting are not present in the system'
        test_file = './test/unit/test_data/course_valid.json'
        malformed_systemInfo = {
        }
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(malformed_systemInfo, test_file)

    def test_json_import_user_valid(self):
        test_file = './test/unit/test_data/user_valid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        systemInfo_populated['courses']['test_course']['users'] = {}
        result = import_export.import_data(systemInfo_populated, test_file)
        self.assertDictEqual(result, systemInfo_mockup)

    def test_json_import_user_invalid(self):
        expected_error_message = 'Metadata are corrupted; the file cannot be imported'
        test_file = './test/unit/test_data/user_invalid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        systemInfo_populated['courses']['test_course']['users'] = {}
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(systemInfo_populated, test_file)

    def test_json_import_user_malformed(self):
        expected_error_message = 'Some layers above the level you are inserting are not present in the system'
        test_file = './test/unit/test_data/user_valid.json'
        malformed_systemInfo = {
            'courses': {
                'test_course': {
                }
            }
        }
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(malformed_systemInfo, test_file)

    def test_json_import_session_valid(self):
        test_file = './test/unit/test_data/session_valid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        systemInfo_populated['courses']['test_course']['users']['test_user']['sessions'] = {
        }
        result = import_export.import_data(systemInfo_populated, test_file)
        self.assertDictEqual(result, systemInfo_mockup)

    def test_json_import_session_invalid(self):
        expected_error_message = 'Metadata are corrupted; the file cannot be imported'
        test_file = './test/unit/test_data/session_invalid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        systemInfo_populated['courses']['test_course']['users']['test_user']['sessions'] = {
        }
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(systemInfo_populated, test_file)

    def test_json_import_session_malformed(self):
        expected_error_message = 'Some layers above the level you are inserting are not present in the system'
        test_file = './test/unit/test_data/session_valid.json'
        malformed_systemInfo = {
            'courses': {
                'test_course': {
                }
            }
        }
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(malformed_systemInfo, test_file)

    def test_json_import_system_with_overwrite_issue(self):
        expected_error_message = 'Trying to overwrite the whole system without permissions; try overwrite = True'
        test_file = './test/unit/test_data/system_valid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(systemInfo_populated, test_file)

    def test_json_import_lower_level_with_overwrite_issue(self):
        expected_error_message = 'Import has overwrite conflict; try to launch with overwrite = True'
        test_file = './test/unit/test_data/course_valid.json'
        systemInfo_populated = copy.deepcopy(systemInfo_mockup)
        with self.assertRaisesRegex(ImportException, expected_error_message):
            import_export.import_data(systemInfo_populated, test_file)


if __name__ == '__main__':
    unittest.main()
