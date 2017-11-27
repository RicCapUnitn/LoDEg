from datetime import datetime, date
from dateutil import tz
import dateutil.parser
from bson.objectid import ObjectId
import json


class BetterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


def getTimeFromObjectId(oid: str):
    """Get the generation time from a MongoDB objcetId.

    Args:
        oid (str): the object id.
    """
    return ObjectId(oid).generation_time


def getDateTimeFromISO8601String(string):
    """Convert ISO8601 to datetime."""
    dt = dateutil.parser.parse(string)
    return dt


def utc_to_local_time(utc: datetime):  # <-------------Not working
    return utc.strftime('%Y-%m-%d %H:%M:%S %Z')


def get_lessons_durations_and_registration_dates(
        lessons_collection, course: str, courseInfo: dict):
    """Set for a course the course lessons and their durations.

    Args:
        lessons_collection : the MongoDB collection that contains the lessons records;
        course (str): the target course;
        courseInfo (dict): the dictionary to be populated.
    """
    cursor = lessons_collection.find({'course_id': course})
    lessons_durations = {}
    registration_dates = {}
    for lesson in cursor:
        lessons_durations[lesson['lesson_id']] = lesson['duration']
        registration_dates[lesson['lesson_id']] = ObjectId(
            lesson['_id']).generation_time
    courseInfo['lessons_durations'] = lessons_durations
    courseInfo['registration_dates'] = registration_dates


def add_interval(intervals: list, interval: list):
    """Add an interval to a list of disjoint intervals.

    It guarantees disjunction between intervals (substituting the intersections with a new interval),
    the order intervals[i][end] < intervals[i+1][start] and itervals[i][start] < intervals[i][end].

    Args:
        intervals (list): The list of intervals to whom we have to add the interval;
        interval  (list): the interval to add in the format [start,end].
    """

    start = interval[0]
    end = interval[1]
    if (start > end):
        start, end = end, start

    start_index = -1
    end_index = -1
    concatenating = False

    if (intervals is None or intervals == []):
        return [[start, end]]

    for i in range(0, len(intervals)):
        i_start = (intervals[i][0])
        i_end = (intervals[i][1])
        if (i_start <= start and i_end >= end):
            return intervals
        elif (start < i_start):
            if (end >= i_start):
                if(start_index == -1):
                    start_index = i
                    concatenating = True
                if (end < i_end):
                    end = i_end
            else:
                concatenating = False
            if (end < i_end):
                if(not concatenating):
                    if(end_index == -1):
                        concatenating = True
                        end_index = i
                if (concatenating):
                    end_index = i
        else:  # (start >= i_start)
            if (start <= i_end):
                if(start_index == -1):
                    start_index = i
                    start = i_start
                    concatenating = True
            else:
                pass  # disjoint

    # the interval is after the last item of intervals (disjoint)
    if (start_index == -1) and (end_index == -1):
        intervals.append([start, end])
        return intervals

    # disjoint_start and disjoint_middle
    elif (start_index == -1):
        intervals.insert(end_index, [start, end])
        return intervals

    # strict_end and boundary_end
    elif (end_index == -1):
        return intervals[:start_index] + [[start, end]]

    # the interval intersects some other intervals
    else:
        lst = []
        lst.append([start, end])
        return intervals[:start_index] + lst + intervals[(end_index):]


def purify_list(data: list, filter_types: list):
    """This function purifies a list of records, keeeping only the desired types of records.

    Args:
        data (list): the raw data to filter as a list of records
        filter_types (list): the types of records we want to keep from the list

    Returns:
        The filtered list.
    """
    return [record for record in data if record['type'] in filter_types]


###########################
# GENERAL_DATA_EXTRACTION #
###########################

def get_all_courses(lessons_collection):
    """Return all the course_ids that have been registered"""
    cursor = lessons_collection.aggregate([{'$group': {'_id': '$course_id'}}])
    return list(elem['_id'] for elem in cursor)


def get_all_users_for_course(collection, course: str):
    """ Returns the user_ids for the specified course.

    Args:
        collection: the collection of log records;
        course (str): the course_id.
    """
    cursor = collection.aggregate(
        [
            {'$match': {
                '$and': [
                    {'value2': course},
                    {'user_id': {'$ne': None}}
                ]
            }},
            {'$group': {'_id': '$user_id'}}
        ]
    )
    return list(elem['_id'] for elem in cursor)


def get_all_sessions_for_course(collection, course: str):
    """ Returns a list of the session_ids for the specified course

    Args:
        collection: the collection of log records
        course (str): the course_id
    """
    cursor = collection.aggregate(
        [
            {'$match': {
                '$and': [
                    {'value2': course},
                    {'user_id': {'$ne': None}}
                ]
            }},
            {'$group': {'_id': '$session_id'}}
        ]
    )
    return list(elem['_id'] for elem in cursor)


def get_all_sessions_for_user_and_course(collection, user: str, course: str):
    """ Returns the session_ids of the course for the specified user"""
    matching_sessions = get_all_sessions_for_course(collection, course)
    cursor = collection.aggregate(
        [
            {'$match': {'user_id': user}},
            {'$group': {'_id': '$session_id'}},
            {'$match': {'_id': {'$in': matching_sessions}}}
        ]
    )
    return list(elem['_id'] for elem in cursor)

######################
# RECORDS_EXTRACTION #
######################


def get_all_users_records(collection, course: str, courseInfo: dict):
    """ Retrieve courseInfo data

    Args:
        collection: the collection of log records
        course (str): the course_id we are interested in
        courseInfo (str): the dictionary that will be populated with the data
    """
    # Retrieve course sessions
    matching_sessions = get_all_sessions_for_course(collection, course)
    # Query for data
    cursor = collection.find({'session_id': {'$in': matching_sessions}})

    courseInfo['users'] = {}
    for elem in cursor:
        user_id = elem['user_id']
        session_id = elem['session_id']

        try:
            courseInfo['users'][user_id]
        except KeyError:
            # It is the first time we find this user -> initialize user
            courseInfo['users'][user_id] = {}

        try:
            courseInfo['users'][user_id]['sessions']
        except KeyError:
            # It is the first session we insert -> initialize sessions
            courseInfo['users'][user_id]['sessions'] = {}

        try:
            courseInfo['users'][user_id]['sessions'][session_id]
        except KeyError:
            # It is the first time we find this session -> initialize session
            courseInfo['users'][user_id]['sessions'][session_id] = {'data': []}

        courseInfo['users'][user_id]['sessions'][
            session_id]['data'].append(elem)

    # Probably we need to add the course_id to courseInfo here <--------------


def get_all_records_for_session(collection, session: str, sessionInfo: dict):
    """Populate the specified sessionInfo with data"""
    sessionInfo['data'] = list(collection.find({'session_id': session}))


def get_all_records_for_user_and_course(
        collection,
        course: str,
        user: str,
        userInfo: dict):
    """Populate the specified userInfo with data"""
    # Retrieve course sessions
    matching_sessions = get_all_sessions_for_course(collection, course)
    # Query for data
    cursor = collection.find(
        {'user_id': user, 'session_id': {'$in': matching_sessions}})

    userInfo['sessions'] = {}
    for record in cursor:
        session_id = record['session_id']
        if session_id in userInfo['sessions'].keys():
            pass
        else:
            userInfo['sessions'][session_id] = {}
        if 'data' in userInfo['sessions'][session_id].keys():
            userInfo['sessions'][session_id]['data'].append(record)
        else:
            userInfo['sessions'][session_id]['data'] = [record]
