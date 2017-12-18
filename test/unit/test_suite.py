import unittest

# Add path in order to be able to do imports
import sys
import os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../../src/lodegML')

import connection_to_mongo as connect
import data_extraction
import test_utils
import utility_queries as utils

# Connect to the instance of MongoDB where the mockup_population
# collection is located
db = connect.connect_to_mongo()
logs_collection = db.get_collection('mockup_population')
lessons_collection = db.get_collection('mockup_lessons')


class TestPausesExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._sessionInfo = {}
        test_utils.get_play_and_pauses_test(logs_collection, cls._sessionInfo)
        data_extraction.play_pause_extraction(cls._sessionInfo)

    def test_pauses(self):
        self.assertEqual(self._sessionInfo['pauses'], [
                         (15.13 - 15.0) / 1000, (19.0 - 17.0) / 1000])

    def test_plays(self):
        self.assertEqual(self._sessionInfo['plays'], [
                         (15.0 - 0.0) / 1000, (17.0 - 15.13) / 1000])

    def test_pauses_ratio(self):
        self.assertEqual(self._sessionInfo['pauses_ratio'], [
                         (15.0 - 0.0) / (15.13 - 15.0),
                         (17.0 - 15.13) / (19.0 - 17.0)])


class TestAddInterval(unittest.TestCase):

    def setUp(self):
        self._intervals = [[10.0, 20.0], [30.0, 40.0],
                           [50.0, 60.0], [70.0, 80.0], [90.0, 100.0]]

    def test_intervals_1_disjoint_start(self):
        test_interval = [0.0, 5.0]
        expected_output = [test_interval] + self._intervals
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_2_disjoint_middle(self):
        test_interval = [23.0, 27.0]
        expected_output = self._intervals[
            :1] + [test_interval] + self._intervals[1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_3_disjoint_end(self):
        test_interval = [110.0, 120.0]
        expected_output = self._intervals + [test_interval]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_4_iternal_strict_smaller(self):
        test_interval = [12.0, 15.0]
        expected_output = self._intervals
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_5_external_strict_larger(self):
        test_interval = [9.0, 23.0]
        expected_output = [test_interval] + self._intervals[1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_6_external_strict_smaller_right(self):
        test_interval = [10.0, 15.0]
        expected_output = self._intervals
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_7_external_strict_smaller_left(self):
        test_interval = [15.0, 20.0]
        expected_output = self._intervals
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_8_equals(self):
        test_interval = [10.0, 20.0]
        expected_output = self._intervals
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_9_single_intersection_strict_start(self):
        test_interval = [5.0, 15.0]
        expected_output = [[5.0, 20.0]] + self._intervals[1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_10_single_intersection_strict_end(self):
        test_interval = [95.0, 105.0]
        expected_output = self._intervals[:-1] + [[90.0, 105.0]]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_11_single_intersection_boundary_start(self):
        test_interval = [5.0, 10.0]
        expected_output = [[5.0, 20.0]] + self._intervals[1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_12_single_intersection_boundary_end(self):
        test_interval = [100.0, 105.0]
        expected_output = self._intervals[:-1] + [[90.0, 105.0]]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_13_single_intersection_strict_middle_left(self):
        test_interval = [55.0, 65.0]
        expected_output = self._intervals[
            :2] + [[50.0, 65.0]] + self._intervals[3:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_14_single_intersection_strict_middle_right(self):
        test_interval = [25.0, 35.0]
        expected_output = self._intervals[
            :1] + [[25.0, 40.0]] + self._intervals[2:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_15_single_intersection_boundary_middle_left(self):
        test_interval = [60.0, 65.0]
        expected_output = self._intervals[
            :2] + [[50.0, 65.0]] + self._intervals[3:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_16_single_intersection_boundary_middle_right(self):
        test_interval = [25.0, 30.0]
        expected_output = self._intervals[
            :1] + [[25.0, 40.0]] + self._intervals[2:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_17_multiple_intersection_strict_internal(self):
        test_interval = [35.0, 75.0]
        expected_output = self._intervals[
            :1] + [[30.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_18_multiple_intersection_strict_external(self):
        test_interval = [25.0, 85.0]
        expected_output = self._intervals[
            :1] + [[25.0, 85.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_19_multiple_intersection_boundary_internal_left(self):
        test_interval = [30.0, 75.0]
        expected_output = self._intervals[
            :1] + [[30.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_20_multiple_intersection_boundary_external_left(self):
        test_interval = [30.0, 85.0]
        expected_output = self._intervals[
            :1] + [[30.0, 85.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_21_multiple_intersection_boundary_both(self):
        test_interval = [30.0, 80.0]
        expected_output = self._intervals[
            :1] + [[30.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_22_multiple_intersection_boundary_internal_right(self):
        test_interval = [35.0, 80.0]
        expected_output = self._intervals[
            :1] + [[30.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_23_multiple_intersection_boundary_external_right(self):
        test_interval = [25.0, 80.0]
        expected_output = self._intervals[
            :1] + [[25.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)

    def test_intervals_24_multiple_intersection_boundary_internal_both(self):
        test_interval = [40.0, 70.0]
        expected_output = self._intervals[
            :1] + [[30.0, 80.0]] + self._intervals[-1:]
        self.assertEqual(utils.add_interval(
            self._intervals, test_interval), expected_output)


class TestSessionCoverageExtracion(unittest.TestCase):

    def setUp(self):
        self._sessionInfo = {}

    def test_session_coverage_1_play_pause(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test1', self._sessionInfo)
        expected_output = [[0.0, 50.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_2_play_pause_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test2', self._sessionInfo)
        expected_output = [[0.0, 180.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_3_play_pause_jump_forwards(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test3', self._sessionInfo)
        expected_output = [[0.0, 30.0], [50.0, 70.0], [90.0, 120.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_4_play_pause_jump_backwards(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test4', self._sessionInfo)
        expected_output = [[40.0, 60.0], [80.0, 90.0], [100.0, 120.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_5_play_pause_jump_backwards_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test5', self._sessionInfo)
        expected_output = [[10.0, 60.0], [80.0, 90.0], [100.0, 120.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_6_play_pause_jump_both(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test6', self._sessionInfo)
        expected_output = [[0.0, 10.0], [20.0, 40.0],
                           [70.0, 100.0], [130.0, 150.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_7_play_pause_jump_both_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test7', self._sessionInfo)
        expected_output = [[0.0, 60.0], [70.0, 100.0], [130.0, 150.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_8_play_pause_jump_both_alive_speed(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test8', self._sessionInfo)
        expected_output = [[0.0, 60.0], [70.0, 100.0], [130.0, 150.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'session_coverage'], expected_output)

    def test_session_coverage_mute_1_play_pause(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test1', self._sessionInfo)
        expected_output = [[35.0, 50.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_2_play_pause_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test2', self._sessionInfo)
        expected_output = [[35.0, 150.0], [160.0, 180.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_3_play_pause_jump_forwards(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test3', self._sessionInfo)
        expected_output = [[60.0, 70.0], [90.0, 100]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_4_play_pause_jump_backwards(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test4', self._sessionInfo)
        expected_output = [[40.0, 50.0], [80.0, 90.0], [110.0, 120.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_5_play_pause_jump_backwards_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test5', self._sessionInfo)
        expected_output = [[10.0, 20.0], [30.0, 60.0], [80.0, 90.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_6_play_pause_jump_both(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test6', self._sessionInfo)
        expected_output = []
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_7_play_pause_jump_both_alive(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test7', self._sessionInfo)
        expected_output = []
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)

    def test_session_coverage_mute_8_play_pause_jump_both_alive_speed(self):
        test_utils.session_coverage_extraction_test(
            logs_collection, 'test8', self._sessionInfo)
        expected_output = [[0.0, 60.0], [70.0, 90.0]]
        data_extraction.session_coverage_extraction(self._sessionInfo)
        self.assertEqual(self._sessionInfo[
                         'muted_intervals'], expected_output)


class TestQueries(unittest.TestCase):

    def test_queries_1_get_all_courses(self):
        self.assertEqual(
            set(utils.get_all_courses(lessons_collection)), set(['course1', 'course2']))

    def test_queries_2_get_all_users_for_course(self):
        self.assertEqual(
            set(utils.get_all_users_for_course(logs_collection, 'course1')), set(['user1', 'user2', 'user3', 'play_pause_test', 'session_coverage_test', 'jumps_info_test']))

    def test_queries_3_get_all_sessions_for_user_and_course(self):
        self.assertEqual(
            set(utils.get_all_sessions_for_user_and_course(logs_collection, 'user1', 'course1')), set(['user1-session1', 'user1-session2', 'user1-session3']))

    def test_queries_4_get_all_users_records(self):
        courseInfo = {}
        utils.get_all_users_records(logs_collection, 'course1', courseInfo)
        self.assertNotEqual(courseInfo, {})

    def test_queries_5_get_all_records_for_session(self):
        sessionInfo = {}
        utils.get_all_records_for_session(
            logs_collection, 'user1-session1', sessionInfo)
        self.assertNotEqual(sessionInfo, {})

    def test_queries_6_get_all_records_for_user_and_course(self):
        userInfo = {}
        utils.get_all_records_for_user_and_course(
            logs_collection, 'course1', 'user1', userInfo)
        self.assertNotEqual(userInfo, {})


class TestJumpsInfoExtraction(unittest.TestCase):

    def setUp(self):
        self._sessionInfo = {}

    def test_jumps(self):
        input_list = [{
            "type": "jump",
            "value1": 10.0,
            "value2": 70.0,
            "value3": "click_or_drag"
        }, {
            "type": "jump",
            "value1": 90.0,
            "value2": 130.0,
            "value3": "click_or_drag"
        }, {
            "type": "jump",
            "value1": 150.0,
            "value2": 80.0,
            "value3": "click_or_drag"
        }, {
            "type": "jump",
            "value1": 100.0,
            "value2": 10.0,
            "value3": "keyframe"
        }]

        number_of_jumps = 4
        total_jumps_length = 60.0 + 40.0 + 70.0 + 90.0
        average_jumps_length = total_jumps_length / 4.0
        jumps_per_type = jumps_per_type = {
            'click_or_drag': 3, 'keyframe': 1, 'note': 0}
        expected_output = {'number_of_jumps': number_of_jumps, 'average_jumps_length':
                           average_jumps_length, 'jumps_per_type': jumps_per_type,
                           'total_jumps_length': total_jumps_length}

        test_utils.jumps_info_test(
            logs_collection, 'jumps_info_test', self._sessionInfo)
        data_extraction.jumps_info_extraction(self._sessionInfo)
        del self._sessionInfo['data']
        self.assertEqual(self._sessionInfo, expected_output)


@unittest.expectedFailure  # Need to update everything (structure has changed)
class TestDataExtraction(unittest.TestCase):

    def setUp(self):
        self._courseInfo = {}
        self._test_course = 'course1'

    def test_data_extraction_1_purify_list_play_pause_extraction(self):
        computed_output = {}
        expected_output = {}
        # Get the records
        utils.get_all_users_records(
            logs_collection, self._test_course, self._courseInfo)

        # Purify the records
        extracted_purified_records = utils.purify_list(
            self._courseInfo['users']['play_pause_test']['sessions']['play_pause_test']['data'], ['play', 'pause'])
        # Run the play_pause_extraction on the extracted data
        data_extraction.play_pause_extraction(
            computed_output, extracted_purified_records)
        # Run the play_pause_extraction on the test data
        data_extraction.play_pause_extraction(
            expected_output, test_utils.get_play_and_pauses_test(logs_collection))
        self.assertEqual(computed_output, expected_output)

    def test_data_extraction_2_purify_list_session_coverage_extraction(self):
        computed_output = {}
        expected_output = {}
        # Get the records
        utils.get_all_users_records(
            logs_collection, self._test_course, self._courseInfo)
        # Purify the records
        extracted_purified_records = utils.purify_list(
            self._courseInfo['users']['session_coverage_test']['sessions']['test7']['data'], ['play', 'pause', 'alive', 'jump'])
        # Run the session_coverage_extraction on the extracted data
        data_extraction.session_coverage_extraction(
            computed_output, extracted_purified_records)
        # Run the session_coverage_extraction on the test data
        data_extraction.session_coverage_extraction(
            expected_output, test_utils.session_coverage_extraction_test(logs_collection, 'test7'))
        self.assertEqual(computed_output, expected_output)

    def test_data_extraction_3_purify_list_jumps_info_extraction(self):
        computed_output = {}
        expected_output = {}
        # Get the records
        utils.get_all_users_records(
            logs_collection, 'course1', self._courseInfo)
        # Purify the records
        extracted_purified_records = utils.purify_list(
            self._systemInfo['users']['jumps_info_test']['sessions']['jumps_info_test']['data'], ['jump'])
        # Run the session_coverage_extraction on the extracted data
        data_extraction.jumps_info_extraction(
            computed_output, extracted_purified_records)
        # Run the jumps_info_extraction on the test data
        data_extraction.jumps_info_extraction(
            expected_output, test_utils.jumps_info_test(logs_collection, 'jumps_info_test'))
        self.assertEqual(computed_output, expected_output)

    def test_data_extraction_4_compute_sessons_coverage_single_user(self):
        raw_lessons_data_list = test_utils.get_lessons(
            db.get_collection('lessons'))
        lessons_durations = utils.create_lessons_durations_dict(
            raw_lessons_data_list)
        utils.get_all_users_records(logs_collection, self._systemInfo)
        test_users = ['user1']
        # Compute session coverage
        for user in self._systemInfo['users'].keys():
            if (user in test_users):
                for session in self._systemInfo['users'][user]['sessions'].keys():
                    data_extraction.add_lesson_id_to_session(
                        self._systemInfo['users'][user]['sessions'][session])
                    extracted_purified_records = utils.purify_list(
                        self._systemInfo['users'][user]['sessions'][session]['data'], ['play', 'pause', 'alive', 'jump'])
                    data_extraction.session_coverage_extraction(
                        self._systemInfo['users'][user]['sessions'][session], extracted_purified_records)

        # Compute lesson coverage
        for user in self._systemInfo['users'].keys():
            if(user in test_users):
                data_extraction.compute_lessons_coverage_for_single_user(
                    self._systemInfo['users'][user], lessons_durations)
        # The expected ouput depends on the inteval_gap set in data_extraction
        expected_output = [1, 1, 1, 0, 1] + ([0] * 235)
        self.assertEqual(self._systemInfo['users']['user1']['lessons_coverage'][
                         'lesson1'], expected_output)

    def test_data_extraction_5_compute_global_coverage(self):
        raw_lessons_data_list = test_utils.get_lessons(
            db.get_collection('lessons'))
        lessons_durations = test_utils.create_lessons_durations_dict(
            raw_lessons_data_list)
        utils.get_all_users_records(logs_collection, self._systemInfo)
        test_users = ['user1', 'user2', 'user3']
        # Compute session coverage
        for user in self._systemInfo['users'].keys():
            if (user in test_users):
                for session in self._systemInfo['users'][user]['sessions'].keys():
                    data_extraction.add_lesson_id_to_session(
                        self._systemInfo['users'][user]['sessions'][session])
                    extracted_purified_records = utils.purify_list(
                        self._systemInfo['users'][user]['sessions'][session]['data'], ['play', 'pause', 'alive', 'jump'])
                    data_extraction.session_coverage_extraction(
                        self._systemInfo['users'][user]['sessions'][session], extracted_purified_records)

        # Compute lesson coverage
        for user in self._systemInfo['users'].keys():
            if(user in test_users):
                data_extraction.compute_lessons_coverage_for_single_user(
                    self._systemInfo['users'][user], lessons_durations)
        # Compute global coverage
        data_extraction.compute_global_lesson_coverage(
            self._systemInfo, lessons_durations)
        # The expected ouput depends on the inteval_gap set in data_extraction
        expected_output = [3, 0, 3, 0, 3] + ([0] * 235)
        self.assertEqual(self._systemInfo['global_coverage'][
                         'lesson2'], expected_output)

    def test_data_extracion_6_notes_info_extraction(self):
        raw_lessons_data_list = test_utils.get_lessons(
            db.get_collection('lessons'))
        lessons_durations = utils.create_lessons_durations_dict(
            raw_lessons_data_list)
        utils.get_all_users_records(logs_collection, self._systemInfo)
        userInfo = self._systemInfo['users']['user4']
        for sessionInfo in userInfo['sessions'].values():
            data_extraction.compute_session_duration(sessionInfo)
            notes = utils.purify_list(
                sessionInfo['data'], ['note'])
            data_extraction.notes_info_extraction(sessionInfo, notes)
            self.assertEqual(sessionInfo['notes_per_type'], {
                             'handwritten': 3, 'text': 2})
            self.assertEqual(sessionInfo['number_of_notes'], 5)

    def test_data_extracion_7_user_notes_info_extraction(self):
        raw_lessons_data_list = test_utils.get_lessons(
            db.get_collection('lessons'))
        lessons_durations = utils.create_lessons_durations_dict(
            raw_lessons_data_list)
        utils.get_all_users_records(logs_collection, self._systemInfo)
        test_users = ['user4', 'user5']
        for user in test_users:
            userInfo = self._systemInfo['users'][user]
            for sessionInfo in userInfo['sessions'].values():
                data_extraction.compute_session_duration(sessionInfo)
                notes = utils.purify_list(
                    sessionInfo['data'], ['note'])
                data_extraction.notes_info_extraction(sessionInfo, notes)
            data_extraction.user_notes_info_extraction(userInfo)
            self.assertEqual(userInfo['notes_per_type'], {
                             'handwritten': 9, 'text': 6})
            self.assertEqual(userInfo['number_of_notes'], 15)

    def test_data_extraction_7_complete_extraction(self):
        self._systemInfo = data_extraction.execute_complete_extraction(
            logs_collection, self._systemInfo)
        # To be refined


if __name__ == '__main__':
    unittest.main()
