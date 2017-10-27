import utility_queries as utils  # migrate
import auto_plot  # migrate
import data_extraction  # migrate
import connection_to_mongo  # migrate
import ml  # migrate

from django.http import HttpResponse
import pandas as pd
import csv
import json
import pickle


class LodegSystem:
    """The class that represents the system."""

    ##################
    # CONFIGURATIONS #
    ##################

    # Default configuration (command line, python script, ...)
    _config_default = {
        'query_mem_opt': True,  # Might be false (need to benchmark)
        'keep_user_info': True,
        'keep_session_data': False,
        'ml_mem_opt': False,  # Keep data both in dataframes and dictionaries
        'ml_autorun': True,  # Autorun the clustering algorith
        # Initialization only
        'cache': None  # Default should be set to None or be always available
    }

    # Low memory configuration
    _config_low_mem = {
        'query_mem_opt': True,
        'keep_user_info': False,  # Discard user statistics after computation
        'keep_session_data': False,
        'ml_mem_opt': True,
        'ml_autorun': False,
        'cache': None  # Default should be set to None or be always available
    }

    # Web default configuration
    _config_web = {
        'query_mem_opt': True,
        'keep_user_info': True,
        'keep_session_data': False,
        'ml_mem_opt': True,
        'ml_autorun': False,
        'cache': 'sqlite'  # Default should be set to None or be always available
    }

    _config = _config_default.copy()

    ##############
    # DECORATORS #
    ##############

    def _cache_needed(func):
        def func_wrapper(self, *args, **kwargs):
            if self._config['cache']:
                func(self, *args, **kwargs)
            else:
                return 'You need to initialize a cache to run this method.'
        return func_wrapper

    def _takes_config(pos_params: int, params: list):
        """
        Args:
            pos_params (int): the number of position parameters (self included)
        """
        def func_decorator(func):
            def func_wrapper(self, *args, **kwargs):
                if len(args) > pos_params:
                    return ('Wrong params call; config params should be set explicitly: param = value')
                config_params = {}

                # No config param has been provided
                if kwargs is None:
                    return func(self, *args, **{param: self._config[param] for param in params})

                # There is at least one config param in the function call
                for param in params:
                    if param not in kwargs:
                        config_params[param] = self._config[param]
                    else:
                        if kwargs[param] is None:
                            config_params[param] = self._config[param]
                        else:
                            config_params[param] = kwargs[param]
                return func(self, *args, **config_params)
            return func_wrapper
        return func_decorator

    #################
    # CLASS METHODS #
    #################

    def __init__(self, modality: str = None, **kwargs):
        """ Object constructur, accepts config dictionary.

        Args:
            modality (str): Select a predefined configuration between [default, low_mem, web]
        """
        self._systemInfo = {'courses': {}, 'last_update': 'never'}

        # Set base settings
        if modality:
            if modality == 'low_mem':
                self._config = self._config_low_mem.copy()
            elif modality == 'web':
                self._config = self._config_web.copy()
            else:
                self._config = self._config_default.copy()
        else:
            self._config = self._config_default.copy()

        # Update class settings if required during instantiation
        if (kwargs is not None):
            self.modify_class_settings(**kwargs)

        # Get default collections
        self._db = connection_to_mongo.connect_to_mongo()
        self._logs = self._db.get_collection('web_mockup_population')
        self._lessons = self._db.get_collection('web_mockup_lessons')

        # Get appropriate cache (or set default one if available)
        requested_cache = self._config['cache']
        if requested_cache is not None:
            import cache  # migrate
            # self.check_available_caches()
            # if requested_cache in available_caches:
            # pass # get the appropriate cache somehow
            if requested_cache == 'sqlite':
                self._cache = cache.CacheSQLite()
            else:
                self._cache = cache.CacheMongoDb(
                    self._db.get_collection('system_cache'))

    def modify_class_settings(self, **kwargs):
        """Tweak class params

        Note: default values for all parameters has already been provided before this function can be called;
            Only params that already exist can be modified (type checking is implemented to avoid inappropriate use).

        Args:
            kwargs:
                keep_session_data (bool): Keep the raw session data in the system. Defaults to False.
                keep_user_info (bool): Keep the statistics computed at the userInfo level. Defaults to True.
                query_mem_opt (bool): Do only partial queries to keep memory usage low. Defaults to True.
        """
        for param, param_value in kwargs.items():
            if param in self._config:
                if type(self._config[param]) == type(param_value):
                    self._config[param] = param_value

    def getData(self, course: str = None, user: str = None, session: str = None, get_copy: bool = False):
        """Get a reference of a part of the system (default is SystemInfo)

        Args:
            course (str): if set a CourseInfo is returned 
            user (str): if both course and user are set then a UserInfo is returned
            session (str): if course, user and session are set then a SessionInfo is returned

        Returns:
            the target system part if present; otherwise, an empty dict
        """
        try:
            if course:
                if user:
                    data = self._systemInfo['courses'][course]['users'][user] 
                else:
                    data = self._systemInfo['courses'][course]
            else:
                data = self._systemInfo
            
            return data.copy() if get_copy else data

        except KeyError:
            # The information of the target course or user is not present in
            # the system
            return {}

    def getLastUpdate(self):
        """Get the local time representation of the last data extraction"""
        if (self._systemInfo['last_update'] != 'never'):
            return utils.utc_to_local_time(self._systemInfo['last_update'])
        else:
            return 'never'

    @_takes_config(3, ['keep_session_data'])
    def extractUserData(self, course: str, user: str, keep_session_data: bool = None):
        """Extracts the statistics for the target user.

        Args:
            course (str): The id of the course we are interested in.
            user (str): The id of the user whose userInfo we are extracting.
            keep_session_data (bool): Keep the raw session data in the system. Defaults to config.
        """
        # Check if the course is already known by the system
        if course not in self._systemInfo['courses'].keys():
            self._systemInfo['courses'][course] = {'users': {}}
        courseInfo = self._systemInfo['courses'][course]
        # Check if the lessons_durations have already been computed
        if ('lessons_durations' not in courseInfo.keys()):
            utils.get_lessons_durations_and_registration_dates(
                self._lessons, course, courseInfo)
        lessons_durations = courseInfo['lessons_durations']
        # Extract user data
        userInfo = {}
        data_extraction.execute_userInfo_extraction(
            self._logs, lessons_durations, course, user, userInfo, keep_session_data)
        # Save the user in the system
        courseInfo['users'][user] = userInfo

    @_takes_config(1, ['keep_session_data', 'keep_user_info', 'query_mem_opt', 'ml_autorun'])
    def executeCompleteExtraction(self,
                                  keep_session_data: bool = None,
                                  keep_user_info: bool = None,
                                  query_mem_opt: bool = None,
                                  ml_autorun: bool = None):
        """Extract the data and compute all the statistics.

        Args:
            keep_session_data (bool): Keep the raw session data in the system. Defaults to False. 
            keep_user_info (bool): Keep all computed userInfos in the system. Defaults to False. 
        """
        systemInfo = {'courses': {}}
        data_extraction.execute_complete_extraction(
            self._logs, self._lessons, systemInfo, keep_session_data, keep_user_info, query_mem_opt)
        self._systemInfo = systemInfo
        # If ml_autorun is run the ml algorithms
        if ml_autorun: 
            self.runMl()

    @_cache_needed
    def collectDataFromDb(self, user: str = None):
        """Queries the db for already computed information.

        Note:
            If the user is defined we query only the userInfo. Otherwise, it means
            that the user is an administrator of the system: in this case we query
            the cache for the whole systemInfo.

        Args:
            user (str): The id of the user whose userInfo we are quering the db.
        """
        self._systemInfo = self._cache.collectDataFromDb(
            self._systemInfo, user)

    @_cache_needed
    def saveDataToDb(self, user: str = None):
        """Saves the current information into the database.

        Note:
            If the user is defined we save only the userInfo. Otherwise, it means
            that the user is an administrator of the system: in this case we save
            the whole systemInfo in the cache.

        Args:
             user (str): The id of the user whose userInfo we are saving. Defaults to None.
        """
        self._cache.saveDataToDb(self._systemInfo, user)

    def getCSV(self, course: str) -> HttpResponse:
        """ Get an HttpResponse containing the courseInfo information formatted as CSV.

        Args:
            course (str): the course whose statistics we are exporting.

        Returns:
            An HttpResponse with content MIME text/csv
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename= "' + \
            course + 'Export.csv"'
        courseInfo = self._systemInfo['courses'][course]

        if 'stats_dframe' not in courseInfo:
            # Create the DataFrame
            ml.migrateStatsToDataFrames(courseInfo, ml_mem_opt=False)

        csv_export = courseInfo['stats_dframe'].to_csv()
        response.write(csv_export)

        return response

    def export_data(self, export_type: str, course: str = None, user: str = None, session: str = None,
                    selected_keys: list = None, pretty_printing: bool = False):
        """Export the whole system or a part of it.
        
        The json and the binary .p formats are supported.
        
        Args:
            export_type (str): 'json' or 'bytes' export types are supported;
            course (str): if set the target CourseInfo is exported;
            user (str): if both course and user are set, the target UserInfo is exported;
            session (str): if all course, user and session are set, the target SessionInfo is exported;
            selected_keys (list of str): the keys (stats) that you want to export. Defaults to all;
            pretty_printing (bool): if True json will be formatted with 4-spaces indentation. Defaults to False.        
        """

        data = None
        title = None
        insertion_level = 'system'
        insertion_key = ''

        # Localize the target data
        try:
            if course:
                if user:
                    if session:
                        # SessionInfo
                        title = '{}-{}-{}'.format(course, user, session)
                        data = self._systemInfo['courses'][course][
                            'users'][user]['sessions'][session]
                        insertion_position = 'session'
                        insertion_key = '{} {} {}'.format(
                            course, user, session)
                    else:
                        # UserInfo
                        title = '{}-{}'.format(course, user)
                        data = self._systemInfo['courses'][
                            course]['users'][user]
                        insertion_position = 'user'
                        insertion_key = '{} {}'.format(course, user)
                else:
                    # CourseInfo
                    title = course
                    data = self._systemInfo['courses'][course]
                    insertion_position = 'course'
                    insertion_key = course
            else:
                # SystemInfo
                title = 'system'
                data = self._systemInfo
                insertion_position = 'system'
                insertion_key = ''

            # Select only requested keys
            if selected_keys:
                dict_keys = set(data.keys())
                target_keys = set(selected_keys)
                for unwanted_key in dict_keys - target_keys:
                    del data[unwanted_key]

        except KeyError:
            title = 'damaged'
            data = {'objective': 'not found'}

        # Json file
        if export_type == 'json':
            with open(title + '-export.json', 'w') as fp:
                if pretty_printing:
                    json.dump({
                        'insertion_position': insertion_position,
                        'insertion_key': insertion_key,
                        'data': data}, fp, indent=4, skipkeys=True, cls = utils.BetterEncoder)
                else:
                    json.dump({
                        'insertion_position': insertion_position,
                        'insertion_key': insertion_key,
                        'data': data}, fp, skipkeys=True, cls = utils.BetterEncoder)

        # Binary file
        elif export_type == 'bytes':
            with open(title + '-export.p', 'wb') as fp:
                pickle.dump({
                    'insertion_position': insertion_position,
                    'insertion_key': insertion_key,
                    'data': data}, fp)

    def import_data(self, filename: str, overwrite: bool = False) -> str:
        """Import the whole system or a part of it
        
        Args:
            filename (str): the filename (filepath) that we are importing;
            overwrite (bool): if the imported information is already present in the system and overwrite = False then a message is returned and the file is not imported. Defaults to False.
        Returns:
            True if the import worked nominally; otherwise, False.
        """

        # Get the data to be imported
        data = None

        try:
            # Json file
            if filename.endswith('.json'):
                with open(filename, 'r') as fp:
                    data = json.load(fp)
            # Binary file
            elif filename.endswith('.p'):
                with open(filename, 'rb') as fp:
                    data = pickle.load(fp)
            else:
                return 'File format not supported'

            try:
                insertion_position = data['insertion_position']
                insertion_key = data['insertion_key']
                data = data['data']
            except KeyError:
                return 'The file is corrupted and does not contain the appropriate metadata'

        except FileNotFoundError:
            return 'File not found: {}'.format(filename)

        # Try to see if the system can accept the data; if a key error is
        # rised, do nothing.
        system_flag = False
        tokens = insertion_key.split()

        try:
            if insertion_position == 'session':
                insertion_position = self._systemInfo['courses'][
                    tokens[0]]['users'][tokens[1]]['sessions']
                insertion_key = tokens[2]
            elif insertion_position == 'user':
                insertion_position = self._systemInfo[
                    'courses'][tokens[0]]['users']
                insertion_key = tokens[1]
            elif insertion_position == 'course':
                insertion_position = self._systemInfo['courses']
                insertion_key = tokens[0]
            elif insertion_position == 'system':
                insertion_position = self._systemInfo
                system_flag = True
        except KeyError:
            return 'Some layers above the {} you are inserting are not present in the system'.format(location)
        except IndexError:
            return 'Metadata are corrupted; the file cannot be imported'

        if system_flag:
            if overwrite == False:
                if len(self._systemInfo['courses']) != 0:
                    return 'Trying to overwrite the whole system without permissions; try overwrite = True'
            self._systemInfo = data
        else:
            if overwrite == False:
                if insertion_key in inserting_position.keys():
                    return 'Import has overwrite conflict; try to launch with overwrite = True'
            insertion_position[insertion_key] = data

        # Everything worked nominally
        return 'Done'

    def getNumberOfUsers(self, course: str = None):
        """Get the number of users saved in the system.

        Args:
            course(str): if specified, we are asking for course level info; otherwise, system level.

        Returns:
            The total number of users if the information is known by the system.
        """
        number_of_users = 0
        try:
            if (course is not None):
                number_of_users = len(
                    self._systemInfo['courses'][course]['users'])
            else:
                for course in self._systemInfo['courses'].keys():
                    number_of_users += len(
                        self._systemInfo['courses'][course]['users'])
        except KeyError:
            number_of_users = 'Unknown'
        return number_of_users

    def getNumberOfSessions(self, course: str = None, user: str = None):
        """Get the number of sessions.

        Args:
            course (str): If set we are asking for courseLevel or userLevel info; otherwise, systemLevel info will be provided.
            user (str): If both course and user are set we are asking for userLevel info; otherwise, courseLevel or systemLevel.

        Returns:
            The appropriate number of sessions if the information is known by the system; otherwise, the string 'Unknown'.

        """
        try:
            if (course is not None):
                if (user is not None):
                    # User level info
                    numberOfSessions = len(self._systemInfo['courses'][
                                           course]['users'][user]['sessions'])
                else:
                    # Course level info
                    numberOfSessions = self._systemInfo[
                        'courses'][course]['number_of_sessions']
            else:
                # System level info
                # <------------ Not implemented yet
                numberOfSessions = self._systemInfo['number_of_sessions']
        except KeyError:
            # We don't have the information in the system
            numberOfSessions = "Unknown"
        return numberOfSessions

    def getNumberOfLessons(self, course: str):
        """Get the number of lessons for a specific course.

        Args:
            course (str): the id of the course whose information we are interested in.

        Returns:
            The total number of lessons if the information is known by the system; otherwise, the string 'Unknown'.

        """
        try:
            return len(self._systemInfo['courses'][course]['lessons_durations'])
        except KeyError:
            return 'Unknown'

    def getUserCoveragePercentage(self, course: str, user: str):
        """Get the coverage percentage of lessons that the user have watched over the lessons of the course.

        Args:
            course (Str): The id of the course we are inspecting.
            user (str): The id of the user whose coverage percentage we are asking for.

        Returns:
            str: the coverage percentage if the information is known by the system; otherwise, the string 'Unknown'.

        """
        try:
            coverage_percentage = str(self._systemInfo['courses'][course]['users'][user][
                                      'coverage_percentage']) + '%'
        except KeyError:
            # We don't have this information in the system
            coverage_percentage = "Unknown"
        return coverage_percentage

###############################################################################
#                                  HEADERS                                    #
###############################################################################

    def getUsers(self, course: str = None):
        """Get the list of users

        Args:
            course (str): The id of the course we are interested in. If none we get all the users.

        Returns:
            list of str: the users ids if the course is present in the system; otherwise, the empty list
        """
        try:
            if course is not None:
                users = self._systemInfo['courses'][course]['users'].keys()
            else:
                users = 0
                for courseInfo in self._systemInfo['courses'].items():
                    users += len(courseInfo['users'])
        except KeyError:
            users = []
        return users

    def getUserSessionsHeaders(self, course: str, user: str):
        """Get a list of string headers (lesson_title:date) of the user sessions

        Args:
            course (str): The id of the course we are interested in.
            user (str): The id of the user whose sessions dates we are asking for.

        Returns:
            list of str: the headers of the session if known by the system; otherwise, the empty list

        """
        sessions_dates = []
        try:
            for session, sessionInfo in self._systemInfo['courses'][course]['users'][user]['sessions'].items():
                sessions_dates.append({'session_id': session, 'header': (
                    sessionInfo['lesson_id'] + "-> " + str(sessionInfo['date']))})
        except KeyError:
            # We don't have this information in the system or the user has no
            # session
            sessions_dates = []
        return sessions_dates

    def getLessonsHeaders(self, course: str):
        """Get the lessons headers of all uploaded lessons.

         Args:
            course (str): The id of the course we are interested in.

        Returns:
            list of str: the headers of the session if known by the system; otherwise, the empty list
        """
        try:
            return self._systemInfo['courses'][course]['lessons_durations'].keys()
        except KeyError:
            # We don't have this information in the system
            return []

    def getCourses(self):
        """Get the courses present in the system.

        Returns:
            list of str: the courses.
        """
        return self._systemInfo['courses'].keys()


###############################################################################
#                                  CHARTS                                     #
###############################################################################

    def printSessionCoverage(self, course: str, user: str, session: str):
        """Returns an image of the session coverage as html string 

        Note:
            This method requires the user (_systemInfo['users'][user]['sessions']) to be already initialized.

        Args:
            course (str): The id of the course whose user session coverage we are asking for.
            user (str): The id of the user whose session coverage we are asking for.
            session (str): The demanded session.

        Returns:
            str: the image representation of the session coverage
        """
        if (course not in self._systemInfo['courses'].keys()):
            self._systemInfo['courses'][course] = {
                'users': {user: {'sessions': {}}}}
        else:
            if (user not in self._systemInfo['courses'][course]['users'].keys()):
                self._systemInfo['courses'][course][
                    'users'][user] = {'sessions': {}}
        # Check if it is the first time we encounter this session
        try:
            sessionInfo = self._systemInfo['courses'][
                course]['users'][user]['sessions'][session]
        except KeyError:
            # We have never computed the sessionInfo for this user -> execute a
            # complete extraction for this session
            sessionInfo = {}
            data_extraction.execute_sessionInfo_extraction(sessionInfo,
                                                           logs_collection=self._logs, session=session, keep_session_data=self._config['keep_session_data'])
            self._systemInfo['courses'][course]['users'][
                user]['sessions'][session] = sessionInfo

        # Get the lesson duration for this session
        try:
            lesson_duration = self._systemInfo['courses'][course][
                'lessons_durations'][sessionInfo['lesson_id']]
        except KeyError:
            # THIS MUST NOT HAPPEN -> it implies that the lesson has not been
            # registered when uploaded
            lesson_duration = 7200.0

        # Check if the session_coverage has already been calculated
        try:
            image = auto_plot.printSessionCoverage(
                sessionInfo, lesson_duration)
        except KeyError:
            # We don't have this information in the system -> extract it
            data_extraction.session_coverage_extraction(
                sessionInfo, lesson_duration)
            image = auto_plot.printSessionCoverage(sessionInfo)

        return image

    def printLessonCoverage(self, lesson: str, course: str, user: str = None):
        """Returns an image of the session coverage as html string.

        Note:
            This method requires the coverage to be already computed.

        Args:
            lesson (str): The id of the lesson whose coverage we are asking for.
            course (str): The course we are considering.
            user (str): If set, we are asking for the lesson coverage of a specific user; 
                otherwise, courseLevel lesson coverage will be plotted.

        Returns:
            str: the image representation of the session coverage
        """
        try:
            if (user is not None):
                # User level lesson coverage
                coverage = self._systemInfo['courses'][course][
                    'users'][user]['lessons_coverage'][lesson]
            else:
                # System level lesson coverage
                coverage = self._systemInfo['courses'][
                    course]['global_coverage'][lesson]
        except KeyError:
            # We don't have this information in the system
            return('<h2 class="text-center">Coverage unknown</h2>')
        return auto_plot.printLessonCoverage(coverage)

    def printNotesBarChart(self, course: str, user=None, session=None):
        """Returns a bar chart of the notes types distribution as html string.

        Note:
            Three charts can be plotted with this function, depending on the level (system, user, session).

        Args:
            course (str): The course we are considering.
            user (str): If set level < course (user or session)
            session (str): If set level = session, otherwise level = user

        Returns:
            str: the pie chart of the notes types distribution
        """
        # Select the data according to the level requested
        try:
            if(user is not None):
                if (session is not None):
                    # Session level chart
                    notes_types = self._systemInfo['courses'][course][
                        'users'][user]['sessions'][session]['notes_per_type']
                else:
                    # User level chart
                    notes_types = self._systemInfo['courses'][
                        course]['users'][user]['notes_per_type']
            else:
                # System level chart
                notes_types = self._systemInfo[
                    'courses'][course]['notes_per_type']
        except KeyError:
            # We don't have this information in the system
            return('<h2 class="text-center">Notes statistics unknown</h2>')
        return auto_plot.printNotesBarChart(notes_types)

    def printLessonsHistogram(self, course: str, user: str = None):
        """ Return the histogram that plots the number of users that have watched each lesson if level = system;
        if level = user it plots the number of sessions that the user has spent watching the video

        Args:
            course (str): The course we are considering.
            user (str): If set we are plotting the user histogram; otherwise, the course histogram.

        Returns:
            str: the histogram
        """
        try:
            if (user is not None):
                return auto_plot.printLessonsHistogram(self._systemInfo['courses'][course]['users'][user]['coverage_histogram'])
            else:
                return auto_plot.printLessonsHistogram(self._systemInfo['courses'][course]['coverage_histogram'])
        except KeyError:
             # We don't have this information in the system
            return('<h2 class="text-center">Histogram unknown</h2>')

    def printDaySessionDistribution(self, course: str, user: str = None):
        """ Return a figure with a polar and a bar chart with the distribution of sessions throughout the day 
        if level = user user level info is plotted; otherwise, course level info

        Args:
            course (str): The course we are considering.
            user (str): If set we are plotting the user distribution; otherwise, the course distribution.

        Returns:
            str: the figure
        """
        try:
            if (user is not None):
                return auto_plot.printDaySessionDistribution(self._systemInfo['courses'][course]['users'][user]['day_distribution'])
            else:
                return auto_plot.printDaySessionDistribution(self._systemInfo['courses'][course]['day_distribution'])
        except KeyError as e:
            # We don't have this information in the system
            return('<h2 class="text-center">Information unknown</h2>')

    def printLessonUserCorrelationGraph(self, course: str, time_format: str = None):
        """Print a 3d graph of users lesson visualization.

        The graph plots a function of the number of users against time and lessons: for every lesson,
        a curve is plotted to show when and how many users have watched the lessons. 

        Time has two formats: abs and rel. It expresses whether each lesson curve is plotted agains its registration date (rel)
        or against the registration date of the first lesson (abs).

        Params:
            lessons_visualization (dict): the dictionary of type {'lesson_id':ordered_list(datetime)}
            time_format (str): the time format (abs or rel). None == abs.
        """
        try:
            if time_format is not None:
                return auto_plot.printLessonUserCorrelationGraph(self._systemInfo['courses'][course]['lessons_visualization'], self._systemInfo['courses'][course]['registration_dates'], time_format)
            else:
                return auto_plot.printLessonUserCorrelationGraph(self._systemInfo['courses'][course]['lessons_visualization'], self._systemInfo['courses'][course]['registration_dates'],)
        except KeyError:
             # We don't have this information in the system
            return('<h2 class="text-center">Correlation unknown</h2>')

    def printClusteringResults(self):
        """Print a 3d graph of user clusters in a 3d graph"""
        pass

###############################################################################
#                               MACHINE LEARNING                              #
###############################################################################

    def runMl(self):
        """Run the machine learning algorithms
        """
        # Run data migration first
        self.migrateStatsToDataFrames()
        # Run the clustering algorithm
        for courseInfo in self._systemInfo['courses'].values():
            ml.executeUserClustering(courseInfo)

    @_takes_config(1, ['ml_mem_opt'])
    def migrateStatsToDataFrames(self, ml_mem_opt: bool = True):
        """Create a new dataframe for each course with a row for each user and set courseInfo['stats_dframe'] = DataFrame()
        """
        # if we are asked to keep memory low we discard statistics in dicts and
        # keep dataframes only
        for courseInfo in self._systemInfo['courses'].values():
            ml.migrateStatsToDataFrames(courseInfo, ml_mem_opt)
