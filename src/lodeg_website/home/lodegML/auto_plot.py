import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import matplotlib.dates as mdates
import matplotlib.cm as cm
import mpld3
import datetime
import pytz

# Workaround for polar charts
import sys
import base64
import io

# For correlation_graph test only
# from ..lodegML import test_utils  # migrate


class AutoPlot:
    """A helper class that holds all the library plotting capabilities"""

    def __init__(self, target: str = 'console', title_font_size: int = 14):
        """
        Params:
            target (str): ['console','web'] the target of the plot function; if 'console' than the function plt.show() is used, otherwise it will be plotted as either html or png depending on the type of chart. Defaults to 'web'.
            title_font_size (int): figures title font size. Defaults to 14.
        """
        self._target = target
        self._title_font_size = title_font_size

    def _plot(self, figure, output_type='png'):
        if self._target == 'console':
            plt.show()
        elif self._target == 'web':
            if output_type == 'html':
                html = mpld3.fig_to_html(figure)
                return html
            elif output_type == 'png':
                f = io.BytesIO()
                figure.savefig(f, format="png")
                plt.clf()  # Might break everything when parallelizing
                return "data:image/png;base64," + base64.b64encode(f.getvalue()).decode()

    def printSessionCoverage(self, sessionInfo: dict, lesson_duration: float):
        """ Print the session coverage, i.e. which parts of the video have been watched.

        Params:
            sessionInfo (dict): the session that contains the session_coverage to be plotted.
            lesson_duration (float): the duration of the lesson to be plotted.

        Todo:
            * pass the session_coverage instead of the sessionInfo
        """
        session_coverage = sessionInfo['session_coverage']
        fig, ax = plt.subplots()
        ax.plot([0, lesson_duration], [-2, -2], color='b', linewidth=20)
        k = 0
        for i in session_coverage:
            k = k + 1
            ax.plot(i, [-2, -2], color='r', linewidth=20)
            ax.plot(i, [k, k], color='r', linewidth=6)
            ax.plot([i[0], i[0]], [-2, k], "g--", linewidth=0.5)
            ax.plot([i[1], i[1]], [-2, k], "g--", linewidth=0.5)
        ax.grid(True)
        ax.set_title('SESSION COVERAGE: which parts of the video have been watched',
                     fontsize=self._title_font_size)
        ax.set_xlabel('Seconds')
        ax.set_ylabel('Inteval number')
        return self._plot(fig, 'html')

    def printLessonCoverage(self, coverage: list):
        """Plot a bar chart of the number of users per time bucket for the lesson.

        Params:
            notes_types (dict): the dictionary of type {'note_name': #notes}

        Todo:
            * add a bucket_length parameter and scale the ticks accordingly
        """
        fig, ax = plt.subplots()
        ax.grid(True)
        ax.set_xlabel('Seconds')
        ax.set_ylabel('Number of users')
        bars = ax.bar(np.arange(len(coverage)), coverage)
        return self._plot(fig, 'html')

    def printNotesPolarChart(self, notes_types: dict):
        """
        Todo:
            * this method is never used and might be removed
        """
        # Compute pie slices
        N = len(notes_types)
        theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        radii = notes_types.values()
        width = 2 * np.pi / 3
        labels = list(notes_types.keys())

        fig, ax = plt.subplot(111, projection='polar')
        bars = ax.bar(theta, radii, width=width, bottom=0.0)

        ax.legend((bars[i] for i in range(len(bars))), (labels[i]
                                                        for i in range(len(bars))))

        # Use custom colors and opacity
        for r, bar in zip(radii, bars):
            bar.set_facecolor(plt.cm.plasma(r / 5.))
            bar.set_alpha(0.5)

        return self._plot(fig, 'png')

    def printNotesBarChart(self, notes_types: dict):
        """Plot a bar chart of the number of the notes per type.

        Params:
            notes_types (dict): the dictionary of type {'note_name': #notes}
        """
        number_of_types = np.arange(len(notes_types))
        types = list(notes_types.keys())

        fig, ax = plt.subplots()
        colors = ['r', 'b']
        bars = ax.bar(number_of_types, notes_types.values(),
                      color=colors, align="center")

        ax.set_title('Number of notes per type',
                     fontsize=self._title_font_size)
        ax.legend((bars[0], bars[1]), types)
        plt.xticks(range(2), types)
        ax.grid(True)

        return self._plot(fig, 'html')

    def printLessonsHistogram(self, histogram: dict, user_level: bool):
        """Plot a bar chart of the number of users/sessions per lesson.

        Params:
            histogram (dict): a dictionary of type {'lesson':'number_of_users'}
            user_level (bool): if True we are plotting the number of sessions
                per lesson for a given user; otherwise, the number of users per lesson for a given course.
        """
        fig, ax = plt.subplots()
        colors = ['r', 'b']
        x = np.arange(len(histogram))
        bars = ax.bar(x, histogram.values(), color=colors)

        # Set title according to the chart we aare plotting
        if user_level:
            # We are plotting the number of sessions per lesson
            ax.set_title('Number of sessions per lesson',
                         fontsize=self._title_font_size)
        else:
            # We are plotting the number of users per lesson
            ax.set_title('Number of users that have watched each lesson',
                         fontsize=self._title_font_size)

        plt.xticks(x, histogram.keys())
        ax.grid(True)

        return self._plot(fig, 'html')

    def printDaySessionDistribution(self, distribution: list):
        """A polar chart with the distribution of sessions throughout the day

        Args:
            distribution (list): a list of 24 values, i.e. the number of sessions for each time slice
        """
        # Check if the distribution has exactly 24 hours
        if len(distribution) == 24:
            # Compute pie slices
            theta = np.linspace(0.0, 2 * np.pi, 24, endpoint=False)
            radii = distribution
            width = 2 * np.pi / 24.0

            ax1 = plt.subplot(121, projection='polar')
            bars = ax1.bar(theta, radii, width=width, bottom=0.0)

            # Rotate bars
            ax1.set_theta_zero_location("N")
            # set labels
            ax1.set_xticklabels(['12', '', '9', '', '6', '', '3'])

            # Get max value of the distribution (for color scale normalization)
            max_radio = max(distribution)

            # Use custom colors and opacity
            for r, bar in zip(radii, bars):
                bar.set_facecolor(plt.cm.viridis(r / max_radio))

            ax2 = plt.subplot(122)
            bars = ax2.bar(range(0, 24), distribution)
            # Add text
            for bar in bars:
                height = bar.get_height()
                bar.set_facecolor(plt.cm.viridis(height / max_radio))
            ax2.set_xticks(range(0, 24, 2))

            fig = plt.gcf()
            fig.suptitle("Sessions day distribution",
                         fontsize=self._title_font_size)

        return self._plot(fig, 'png')

    def printLessonUserCorrelationGraph(self, lessons_visualization: dict, registration_dates: dict, time_format: str = 'abs'):
        """Print a 3d graph of users lesson visualization.

        The graph plots a function of the number of users against time and lessons: for every lesson,
        a curve is plotted to show when and how many users have watched the lessons.

        Time has two formats: abs and rel. It expresses wheter each lesson curve is plotted agains its registration date (rel)
        or against the registration date of the first lesson (abs).

        Params:
            lessons_visualization (dict): the dictionary of type {'lesson_id':Counter(datetime)}.
            registration_dates (dict): the dates of registration of every lesson.
            time_format (str): the time format (abs or rel). Defaults to abs.
        """

        """
        lessons_visualization = test_utils.correlation_graph_lessons_test()

        # Create the figure
        fig = plt.figure(figsize=(10,10))
        ax = fig.gca(projection='3d')

        # Set z as lessons
        y_ticks = lessons_visualization.keys()
        zs = np.arange(0, len(lessons_visualization))

        # Dates formatters
        months = mdates.MonthLocator()  # every month
        days = mdates.DayLocator()  # every day
        # Setup the DateFormatter for the x axis
        date_format = mdates.DateFormatter('%D')

        # Min/max for x ticks
        datemin = datetime.datetime.now(pytz.utc) + datetime.timedelta(days = -20) # Test
        #datemin = min(registration_dates.values())
        datemax = datetime.datetime.now(pytz.utc)

        # Maxvalue for z axis
        max_value = 0

        verts = []
        for lesson, dates_counter in lessons_visualization.items():
            # Get the dates that are present in the counter
            dates = sorted(dates_counter.keys())

            # Compute datemin and datemax
            max_date = max(dates)
            # Select a relative mindate if time_format = rel
            if (time_format == 'rel'):
                min_date = min(dates)
                if  min_date < datemin:
                    datemin = min_date
            else:
                min_date = datemin

            if max_date > datemax:
                datemax = max_date

            # Create verts adding a 0 before the first and after the last days
            xs = np.asarray([mdates.date2num(min_date + datetime.timedelta(days=-1))] + list(mdates.date2num(dates))
                            + [mdates.date2num(max_date + datetime.timedelta(days=1))])
            ys = [0]
            for date in dates:
                ys.append(dates_counter[date])
            ys.append(0)
            verts.append(list(zip(xs, ys)))

            # Update max_value
            tmp = max(dates_counter.values())
            if (tmp > max_value):
                max_value = tmp

        # Create PolyCollection
        facecolors = [cm.jet(x) for x in np.linspace(0,1,5)]
        #facecolors = [cm.jet(x) for x in np.linspace(0,1,len(registration_dates))]
        poly = PolyCollection(verts, facecolors = facecolors, edgecolor='black', linewidth=0.6)
        poly.set_alpha(0.7)


        # Add the collection to the graph
        ax.add_collection3d(poly, zs=zs, zdir='y')

        # Set ticks
        ax.set_yticklabels(y_ticks)

        # format the ticks
        #ax.xaxis_date()
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_minor_locator(days)
        ax.xaxis.set_major_formatter(date_format)

        # Set axis labels and limits
        ax.set_xlim3d(datemin + datetime.timedelta(days=-1), datemax + datetime.timedelta(days=1))
        ax.set_ylim3d(0, len(lessons_visualization))
        ax.set_zlabel('Users')
        ax.set_zlim3d(0, max_value)

        # Convert the image to a base64 binary stream
        if 'cStringIO' in sys.modules:
            f = cStringIO.StringIO()   # Python 2
        else:
            f = io.BytesIO()           # Python 3
        plt.savefig(f, format="png")
        plt.clf()
        return "data:image/png;base64," + base64.b64encode(f.getvalue()).decode()
        """

        # Create the figure
        fig = plt.figure(figsize=(8, 8))
        ax = fig.gca(projection='3d')

        # Set z as lessons
        y_ticks = lessons_visualization.keys()
        zs = iter(np.arange(0, len(lessons_visualization)))

        # Dates formatters
        months = mdates.MonthLocator()  # every month
        days = mdates.DayLocator()  # every day
        # Setup the DateFormatter for the x axis
        date_format = mdates.DateFormatter('%D')

        # Min/max for x ticks
        datemin = min(registration_dates.values())
        datemax = datetime.datetime.now(pytz.utc)

        # Maxvalue for z axis
        max_value = 0

        for lesson, dates_counter in lessons_visualization.items():
            # Get the dates that are present in the counter
            dates = sorted(dates_counter.keys())

            # Compute datemin and datemax
            max_date = max(dates)
            # Select a relative mindate if time_format = rel
            if (time_format == 'rel'):
                min_date = min(dates)
                if min_date < datemin:
                    datemin = min_date
            else:
                min_date = datemin

            if max_date > datemax:
                datemax = max_date

            # Create verts adding a 0 before the first and after the last days
            xs = np.asarray([mdates.date2num(min_date + datetime.timedelta(days=-1))] + list(mdates.date2num(dates))
                            + [mdates.date2num(max_date + datetime.timedelta(days=1))])
            ys = [0]
            for date in dates:
                ys.append(dates_counter[date])
            ys.append(0)

            # Update max_value
            tmp = max(dates_counter.values())
            if (tmp > max_value):
                max_value = tmp

            ax.set_xlim3d([datemin + datetime.timedelta(days=-1),
                           datemax + datetime.timedelta(days=1)])
            ax.set_ylim3d([0, len(lessons_visualization)])
            ax.set_zlim3d([0, max_value])

            ax.bar(xs, ys, zs=next(zs), zdir='y', alpha=0.8)

        # Set ticks
        ax.set_yticklabels(y_ticks)

        # format the ticks
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_minor_locator(days)
        ax.xaxis.set_major_formatter(date_format)

        # Set axis labels and limits
        ax.set_zlabel('Users')

        # Convert the image to a base64 binary stream
        return self._plot(fig, 'png')
