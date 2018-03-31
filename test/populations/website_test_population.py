import json
from datetime import datetime
import numpy as np


"""
sudo service mongod start
mongoimport --db lodeg --collection web_mockup_population --drop --maintainInsertionOrder --file ./web_population.json
mongoimport --db lodeg --collection web_mockup_lessons --drop --maintainInsertionOrder --file ./web_lessons.json
"""


def create_population():

    # Output formatting option (set None for no indentation)
    indent = 0
    # Lessons uploaded to the LODE platform (test)
    courses = ['course1', 'course2']
    lessons = ['lesson1', 'lesson2', 'lesson3']
    duration = 60.0 * 60.0 * 2.0  # seconds (2h)
    timestamp = datetime.utcnow().isoformat() + 'Z'

    ########################
    # ADD_LESSONS_DURATION #
    ########################
    with open('web_lessons.json', 'w+') as out:
        for course in courses:
            for lesson in lessons:
                record = {'course_id': course, 'lesson_id': lesson,
                          'duration': duration, 'timestamp': timestamp}
                json.dump(record, out, indent=indent)

    ###################
    # TEST_POPULATION #
    ###################

    with open('web_population.json', 'w+') as out:

        record = {}

        test_users = ['user' + str(i) for i in range(3)]
        test_sessions = ['session' + str(i) for i in range(3)]
        test_records = [
            ['play', 0.0, 0.0],
            ['jump', 10.0, 70.0, 'click_or_drag'],
            ['pause', 90.0, 90.0],
            ['jump', 90.0, 130.0, 'click_or_drag'],
            ['jump', 150.0, 80.0, 'click_or_drag'],
            ['pause', 100.0, 170.0],
            ['jump', 100.0, 10.0, 'keyframe'],
            ['play', 10.0, 190.0],
            ['alive', 60.0, 250.0]]

        for user in test_users:
            record['user_id'] = user
            for i in range(len(test_sessions)):
                session = test_sessions[i]
                record['session_id'] = user + "-" + session

                # Add title
                record['type'] = 'title'
                record['value1'] = 'lesson1'
                record['value2'] = 'course1'
                json.dump(record, out, indent=indent)

                for j in range(0, 7000, 300):
                    for item in test_records:
                        noise = np.random.normal(0, 20)
                        record['type'] = item[0]
                        record['value1'] = item[1] + j + noise
                        record['value2'] = item[2] + j + noise
                        if(item[0] == 'jump'):
                            record['value3'] = item[3]
                        else:
                            record.pop('value3', None)
                        json.dump(record, out, indent=indent)

        # Add notes
        record = {}
        notes = [
            ['handwritten'],
            ['handwritten'],
            ['handwritten'],
            ['text'],
            ['text']]
        record['type'] = 'note'
        for user in test_users:
            record['user_id'] = user
            for i in range(len(test_sessions)):
                session = test_sessions[i]
                record['session_id'] = user + "-" + session
                for note in notes:
                    record['value1'] = note[0]
                    json.dump(record, out, indent=indent)

        # Add missing_lesson_duration_test
        record = {}
        record['course_id'] = 'missing_lesson_duration_test'
        record['user_id'] = 'missing_lesson_duration_test'
        record['session_id'] = 'missing_lesson_duration_test'

        json.dump({
            'type': 'title',
            'course_id': record['course_id'],
            'user_id': 'missing_lesson_duration_test',
            'session_id': 'missing_lesson_duration_test',
            'value1': 'missing_lesson_duration_test',
            'value2': record['course_id']
        }, out, indent=indent)

        for j in range(0, 7000, 1500):
            for item in test_records:
                noise = np.random.normal(0, 20)
                record['type'] = item[0]
                record['value1'] = item[1] + j + noise
                record['value2'] = item[2] + j + noise
                if(item[0] == 'jump'):
                    record['value3'] = item[3]
                else:
                    record.pop('value3', None)
                json.dump(record, out, indent=indent)


if __name__ == '__main__':
    create_population()
