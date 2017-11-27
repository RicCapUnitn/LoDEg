from collections import Counter
import datetime
import random
import pytz


def get_lessons(collection):
    cursor = collection.find({}, {'_id': 0})
    return list(cursor)


def get_play_and_pauses_test(collection, sessionInfo: dict):
    cursor = collection.aggregate(
        [
            {'$match': {'user_id': 'play_pause_test'}},
            {'$project': {'_id': 0, 'type': 1, 'value2': 1}}
        ]
    )
    sessionInfo['data'] = list(cursor)


def session_coverage_extraction_test(collection, test_session_id, sessionInfo):
    cursor = collection.aggregate(
        [
            {'$match': {'$and': [{'user_id': 'session_coverage_test'}, {
                'session_id': test_session_id}]}},
            {'$project': {'_id': 0, 'type': 1, 'value1': 1, 'value2': 1}}
        ]
    )
    sessionInfo['data'] = list(cursor)


def jumps_info_test(collection, test_session_id, sessionInfo):
    cursor = collection.aggregate(
        [
            {'$match': {'$and': [
                {'user_id': 'jumps_info_test'},
                {'session_id': test_session_id},
                {'type': 'jump'}]}},
            {'$project': {'_id': 0, 'type': 1, 'value1': 1, 'value2': 1, 'value3': 1}}
        ]
    )
    sessionInfo['data'] = list(cursor)


def correlation_graph_lessons_test():
    lessons_visualization = {}
    lessons = ['lesson' + str(i) for i in range(5)]
    dates = [
        datetime.datetime.now(
            pytz.utc) +
        datetime.timedelta(
            days=-
            i) for i in range(20)]
    for lesson in lessons:
        counter = Counter()
        for date in dates:
            counter[date] += random.randint(1, 100)
        lessons_visualization[lesson] = counter
    return lessons_visualization
