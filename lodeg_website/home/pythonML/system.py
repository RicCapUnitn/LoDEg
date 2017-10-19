from ..pythonML import utility_queries as utils
from ..pythonML import auto_plot
from ..pythonML import data_extraction
from ..pythonML import connection_to_mongo
from ..pythonML import cache
from ..pythonML import ml

from django.http import HttpResponse
import pandas as pd
import csv

class LodegSystem:
    """The class that represents the system."""
    
    _config = {
            'query_mem_opt' : True,
            'keep_user_info' : True,
            'keep_session_data' : False,
            'ml_mem_opt': True,
            'ml_autorun': True, # Default should be false
            'cache' : 'sqlite' # Default should be set to None or be always available
        }
                
    def __init__(self,  config: dict = _config, **kwargs,):
        """ Object constructur, accepts config dictionary."""
        self._systemInfo = {'courses': {}, 'last_update':'never'}
        # Update class settings if required during instantiation
        if (kwargs is not None):
            self.modify_class_settings(**kwargs)
        
        # Get default collections
        self._db = connection_to_mongo.connect_to_mongo()
        self._logs = self._db.get_collection('web_mockup_population')
        self._lessons = self._db.get_collection('web_mockup_lessons')
        
        # Get appropriate cache (or set default one if available)
        requested_cache = config['cache']
        if requested_cache is not None:
            # self.check_available_caches()
            #if requested_cache in available_caches:
                #pass # get the appropriate cache somehow                    
            if requested_cache == 'sqlite':
                self._cache = cache.CacheSQLite()        
            else:
                self._cache = cache.CacheMongoDb(self._db.get_collection('system_cache'))
            
        
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
            if param in _config:
                if type(_config[param]) == type(param_value):
                    _config[param] = param_value
                    
    def getData(self):
        """Get the systemInfo"""
        return self._systemInfo
        
    def getLastUpdate(self):
        """Get the local time representation of the last data extraction"""
        if (self._systemInfo['last_update'] != 'never'):
            return utils.utc_to_local_time(self._systemInfo['last_update'])
        else:            
            return 'never'
        
    def extractUserData(self, course:str, user: str, keep_session_data = _config['keep_session_data']):
        """Extracts the statistics for the target user.

        Args:
            course (str): The id of the course we are interested in.
            user (str): The id of the user whose userInfo we are extracting.
            keep_session_data (bool): Keep the raw session data in the system. Defaults to config.
        """
        # Check if the course is already known by the system
        if course not in self._systemInfo['courses'].keys():
            self._systemInfo['courses'][course] = {'users':{}}
        courseInfo = self._systemInfo['courses'][course]
        # Check if the lessons_durations have already been computed
        if ('lessons_durations' not in courseInfo.keys()):
            utils.get_lessons_durations(self._lessons, course, courseInfo)
        lessons_durations = courseInfo['lessons_durations']
        # Extract user data
        userInfo = {}
        data_extraction.execute_userInfo_extraction(self._logs, lessons_durations, course, user, userInfo, keep_session_data)
        # Save the user in the system
        courseInfo['users'][user] = userInfo 
        
    def executeCompleteExtraction(self, 
                                  keep_session_data = _config['keep_session_data'], 
                                  keep_user_info = _config['keep_user_info'],
                                  query_mem_opt = _config['query_mem_opt'],
                                  ml_autorun = _config['ml_autorun']):
        """Extract the data and compute all the statistics.

        Args:
            keep_session_data (bool): Keep the raw session data in the system. Defaults to False. 
            keep_user_info (bool): Keep all computed userInfos in the system. Defaults to False. 
        """
        systemInfo = {'courses':{}}
        data_extraction.execute_complete_extraction(self._logs, self._lessons, systemInfo, keep_session_data, keep_user_info, query_mem_opt)
        self._systemInfo = systemInfo
        # If ml_autorun is run the ml algorithms
        if ml_autorun:
            self.runMl()

    def collectDataFromDb(self, user: str = None):
        """Queries the db for already computed information.
        
        Note:
            If the user is defined we query only the userInfo. Otherwise, it means
            that the user is an administrator of the system: in this case we query
            the cache for the whole systemInfo.

        Args:
            user (str): The id of the user whose userInfo we are quering the db.
        """
        self._systemInfo = self._cache.collectDataFromDb(self._systemInfo, user)

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
        response['Content-Disposition'] = 'attachment; filename= "' + course + 'Export.csv"'
        courseInfo = self._systemInfo['courses'][course]
        
        if 'stats_dframe' not in courseInfo:
            # Create the DataFrame
            ml.migrateStatsToDataFrames(courseInfo, mem_opt = False)
        
        csv_export = courseInfo['stats_dframe'].to_csv()
        response.write(csv_export)
        
        return response
        
    def getNumberOfUsers(self, course:str = None):
        """Get the number of users saved in the system.
        
        Args:
            course(str): if specified, we are asking for course level info; otherwise, system level.

        Returns:
            The total number of users if the information is known by the system.
        """
        number_of_users = 0
        try:
            if (course is not None):
                number_of_users = len(self._systemInfo['courses'][course]['users'])
            else:
                for course in self._systemInfo['courses'].keys():
                    number_of_users += len(self._systemInfo['courses'][course]['users'])
        except KeyError:
            number_of_users = 'Unknown'
        return number_of_users

    def getNumberOfSessions(self, course:str = None, user: str = None):
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
                    numberOfSessions = len(self._systemInfo['courses'][course]['users'][user]['sessions'])
                else:
                    # Course level info
                    numberOfSessions = self._systemInfo['courses'][course]['number_of_sessions']
            else:
                # System level info
                numberOfSessions = self._systemInfo['number_of_sessions'] #<------------ Not implemented yet
        except KeyError:
            # We don't have the information in the system
            numberOfSessions = "Unknown"
        return numberOfSessions
    
    def getNumberOfLessons(self, course:str):
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

    def getUserCoveragePercentage(self, course:str, user: str):
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

    def getUsers(self, course:str = None):
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
    

    def getUserSessionsHeaders(self, course:str, user: str):
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
                sessions_dates.append({'session_id':session, 'header':(sessionInfo['lesson_id'] + "-> " + str(sessionInfo['date']))})
        except KeyError:
            # We don't have this information in the system or the user has no session
            sessions_dates = []
        return sessions_dates
    
    
    def getLessonsHeaders(self, course:str):
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

    def printSessionCoverage(self, course:str, user: str, session: str):
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
            self._systemInfo['courses'][course] = {'users': {user: {'sessions': {}}}}
        else:
            if (user not in self._systemInfo['courses'][course]['users'].keys()):
                self._systemInfo['courses'][course]['users'][user] = {'sessions':{}} 
        # Check if it is the first time we encounter this session
        try:
            sessionInfo = self._systemInfo['courses'][course]['users'][user]['sessions'][session]
        except KeyError:
            # We have never computed the sessionInfo for this user -> execute a
            # complete extraction for this session
            sessionInfo = {}
            data_extraction.execute_sessionInfo_extraction(sessionInfo,
                logs_collection = self._logs, session = session, keep_session_data = _config['keep_session_data'])
            self._systemInfo['courses'][course]['users'][user]['sessions'][session] = sessionInfo

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
    
    def printLessonCoverage(self, lesson: str, course:str, user: str = None):
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
                coverage = self._systemInfo['courses'][course]['users'][user]['lessons_coverage'][lesson]
            else:
                # System level lesson coverage
                coverage = self._systemInfo['courses'][course]['global_coverage'][lesson]            
        except KeyError:
            # We don't have this information in the system
            return('<h2 class="text-center">Coverage unknown</h2>')
        return auto_plot.printLessonCoverage(coverage)
            
        
    
    def printNotesBarChart(self, course: str, user = None, session = None):
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
                    notes_types = self._systemInfo['courses'][course]['users'][user]['sessions'][session]['notes_per_type']
                else:
                    # User level chart
                    notes_types = self._systemInfo['courses'][course]['users'][user]['notes_per_type']
            else:
                # System level chart
                notes_types = self._systemInfo['courses'][course]['notes_per_type']
        except KeyError:
            # We don't have this information in the system
            return('<h2 class="text-center">Notes statistics unknown</h2>')
        return auto_plot.printNotesBarChart(notes_types)
    
    
    def printLessonsHistogram(self, course:str, user:str = None):
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
        
    def printDaySessionDistribution(self, course:str, user:str = None):
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
        
            
    def printLessonUserCorrelationGraph(self, course:str, time_format:str = None):
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

    def migrateStatsToDataFrames(self, config = _config):
        """Create a new dataframe for each course with a row for each user and set courseInfo['stats_dframe'] = DataFrame()
        """
        # if we are asked to keep memory low we discard statistics in dicts and keep dataframes only
        for courseInfo in self._systemInfo['courses'].values():
            ml.migrateStatsToDataFrames(courseInfo, config['ml_mem_opt'])
            
            