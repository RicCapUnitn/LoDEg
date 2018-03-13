from bson.objectid import ObjectId


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
        collection, course: str, user: str, userInfo: dict):
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
