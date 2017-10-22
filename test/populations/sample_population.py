import json
from datetime import datetime

import test_utils

"""
sudo service mongod start
mongoimport --db lodeg --collection mockup_population --drop --maintainInsertionOrder --file ./population.json
mongoimport --db lodeg --collection mockup_lessons --drop --maintainInsertionOrder --file ./lessons.json
"""


def create_population():

    # Output formatting option (set None for no indentation)
    indent = 4
    # Lessons uploaded to the LODE platform (test)
    courses = ['course1', 'course2']
    lessons = ['lesson1', 'lesson2', 'lesson3']
    duration = 60.0 * 60.0 * 2.0  # seconds (2h)
    timestamp = datetime.utcnow().isoformat() + 'Z'

    ########################
    # ADD_LESSONS_DURATION #
    ########################
    with open('lessons.json', 'w+') as out:
        for course in courses:
            for lesson in lessons:
                record = {'course_id': course, 'lesson_id': lesson,
                          'duration': duration, 'timestamp': timestamp}
                json.dump(record, out, indent=indent)

    ###################
    # TEST_POPULATION #
    ###################

    with open('population.json', 'w+') as out:

        record = {}

        ###################
        # PLAY_PAUSE_TEST #
        ###################

        record['user_id'] = 'play_pause_test'
        record['session_id'] = 'play_pause_test'

        # Add play and pauses records (only time_abs)
        # Should add a test case that ends with a pause record (though it won't
        # change anything)
        play_pauses_records = [
            ['play', 0.0],
            ['pause', 15.0],
            ['play', 15.13],
            ['pause', 17.0],
            ['play', 19.0]]
        for item in play_pauses_records:
            record['type'] = item[0]
            record['value2'] = item[1]  # Time abs
            json.dump(record, out, indent=indent)

        #########################
        # SESSION_COVERAGE_TEST #
        #########################

        record = {}
        record['user_id'] = 'session_coverage_test'

        # Test1
        record['session_id'] = 'test1'
        session_coverage_records = [
            ['play', 0.0],
            ['pause', 30.0],
            ['play', 30.0],
            ['pause', 50.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            json.dump(record, out, indent=indent)

        # Test2
        record['session_id'] = 'test2'
        session_coverage_records = [
            ['play', 0.0],
            ['pause', 130.0],
            ['play', 130.0],
            ['alive', 180.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            json.dump(record, out, indent=indent)

        # Test3
        record['session_id'] = 'test3'
        session_coverage_records = [
            ['play', 0.0],
            ['jump', 30.0, 50.0],
            ['pause', 70.0],
            ['jump', 70.0, 90.0],
            ['play', 90.0],
            ['pause', 120.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        # Test4
        record['session_id'] = 'test4'
        session_coverage_records = [
            ['play', 100.0],
            ['jump', 120.0, 80.0],
            ['pause', 90.0],
            ['jump', 90.0, 40.0],
            ['play', 40.0],
            ['pause', 60.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        # Test5
        record['session_id'] = 'test5'
        session_coverage_records = [
            ['play', 100.0],
            ['jump', 120.0, 80.0],
            ['pause', 90.0],
            ['jump', 90.0, 10.0],
            ['play', 10.0],
            ['alive', 60.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        # Test6
        record['session_id'] = 'test6'
        session_coverage_records = [
            ['play', 0.0],
            ['jump', 10.0, 70.0],
            ['pause', 90.0],
            ['jump', 90.0, 130.0],
            ['play', 130.0],
            ['jump', 150.0, 80.0],
            ['pause', 100.0],
            ['jump', 100.0, 20.0],
            ['play', 20.0],
            ['pause', 40.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        # Test7
        record['session_id'] = 'test7'
        session_coverage_records = [
            ['play', 0.0],
            ['jump', 10.0, 70.0],
            ['pause', 90.0],
            ['jump', 90.0, 130.0],
            ['jump', 150.0, 80.0],
            ['pause', 100.0],
            ['jump', 100.0, 10.0],
            ['play', 10.0],
            ['alive', 60.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        # Test8
        record['session_id'] = 'test8'
        session_coverage_records = [
            ['play', 0.0],
            ['speed', 10.0, 2.0],
            ['jump', 20.0, 70.0],
            ['pause', 90.0],
            ['jump', 90.0, 130.0],
            ['jump', 150.0, 80.0],
            ['pause', 100.0],
            ['jump', 100.0, 10.0],
            ['play', 10.0],
            ['speed', 20.0, 1.5],
            ['alive', 60.0]]
        for item in session_coverage_records:
            record['type'] = item[0]
            record['value1'] = item[1]  # Time rel
            if(item[0] == 'jump'):
                record['value2'] = item[2]
            else:
                record.pop('value2', None)  # Time abs (not used)
            json.dump(record, out, indent=indent)

        ##############################
        # JUMPS_INFO_EXTRACTION_TEST #
        ##############################

        record = {}
        record['user_id'] = 'jumps_info_test'
        record['session_id'] = 'jumps_info_test'
        jump_info_test = [
            ['play', 0.0],
            ['jump', 10.0, 70.0, 'click_or_drag'],
            ['pause', 90.0],
            ['jump', 90.0, 130.0, 'click_or_drag'],
            ['jump', 150.0, 80.0, 'click_or_drag'],
            ['pause', 100.0],
            ['jump', 100.0, 10.0, 'keyframe'],
            ['play', 10.0],
            ['alive', 60.0]]
        for item in jump_info_test:
            record['type'] = item[0]
            record['value1'] = item[1]
            if(item[0] == 'jump'):
                record['value2'] = item[2]
                record['value3'] = item[3]
            else:
                record.pop('value2', None)
                record.pop('value3', None)
            json.dump(record, out, indent=indent)

        ##############
        # TEST_USERS #
        ##############

        record = {}
        test_users = ['user1', 'user2', 'user3']
        test_sessions = ['session1', 'session2', 'session3']

        for user in test_users:
            record['user_id'] = user
            for i in range(len(test_sessions)):
                session = test_sessions[i]
                record['session_id'] = user + "-" + session

                # Add title
                record['type'] = 'title'
                record['value1'] = 'lesson' + str(i + 1)
                record['value2'] = 'course1'
                json.dump(record, out, indent=indent)

                # Add records
                if (i == 1):
                    # Test6
                    session_coverage_records = [
                        ['play', 0.0],
                        ['jump', 10.0, 70.0],
                        ['pause', 90.0],
                        ['jump', 90.0, 130.0],
                        ['play', 130.0],
                        ['jump', 150.0, 80.0],
                        ['pause', 100.0],
                        ['jump', 100.0, 20.0],
                        ['play', 20.0],
                        ['pause', 40.0]]
                else:
                    # Test7
                    session_coverage_records = [
                        ['play', 0.0],
                        ['jump', 10.0, 70.0],
                        ['pause', 90.0],
                        ['jump', 90.0, 130.0],
                        ['jump', 150.0, 80.0],
                        ['pause', 100.0],
                        ['jump', 100.0, 10.0],
                        ['play', 10.0],
                        ['alive', 60.0]]
                for item in session_coverage_records:
                    record['type'] = item[0]
                    record['value1'] = item[1]  # Time rel
                    if(item[0] == 'jump'):
                        record['value2'] = item[2]
                    else:
                        record.pop('value2', None)  # Time abs (not used)
                    json.dump(record, out, indent=indent)

        session_coverage_records = [
            ['play', 0.0],
            ['jump', 10.0, 70.0],
            ['pause', 90.0],
            ['jump', 90.0, 130.0],
            ['play', 130.0],
            ['jump', 150.0, 80.0],
            ['pause', 100.0],
            ['jump', 100.0, 20.0],
            ['play', 20.0],
            ['pause', 40.0]]

        record = {}
        record['user_id'] = 'user2'
        for i in range(len(test_sessions)):
            session = test_sessions[i]
            record['session_id'] = user + "-" + session + "2"

            # Add title
            record['type'] = 'title'
            record['value1'] = 'lesson1'
            record['value2'] = 'course1'
            json.dump(record, out, indent=indent)

            for j in range(0, 7000, 300):
                for item in session_coverage_records:
                    record['type'] = item[0]
                    record['value1'] = item[1] + j
                    if(item[0] == 'jump'):
                        record['value2'] = item[2] + j
                    else:
                        record.pop('value2', None)
                    json.dump(record, out, indent=indent)

        # Add notes
        record = {}
        record['type'] = 'note'
        test_users = ['user4', 'user5']
        notes = [
            ['handwritten'],
            ['handwritten'],
            ['handwritten'],
            ['text'],
            ['text']]
        for user in test_users:
            record['user_id'] = user
            for i in range(len(test_sessions)):
                session = test_sessions[i]
                record['session_id'] = user + "-" + session
                for note in notes:
                    record['value1'] = note[0]
                    json.dump(record, out, indent=indent)

if __name__ == '__main__':
    create_population()
