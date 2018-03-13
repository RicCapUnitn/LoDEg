from datetime import datetime, date
from dateutil import tz
import dateutil.parser
import json


class BetterEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        # return json.JSONEncoder.default(self, obj)
        return {}


def utc_to_local_time(utc: datetime):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc_tzaware_time = utc.replace(tzinfo=from_zone)
    local_tzaware_time = utc_tzaware_time.astimezone(to_zone)

    return local_tzaware_time.strftime('%Y-%m-%d %H:%M:%S %Z')


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

    if (intervals is None) or (intervals == []):
        return [[start, end]]

    for i in range(0, len(intervals)):
        i_start = (intervals[i][0])
        i_end = (intervals[i][1])
        if (i_start <= start) and (i_end >= end):
            return intervals
        elif start < i_start:
            if end >= i_start:
                if start_index == -1:
                    start_index = i
                    concatenating = True
                if end < i_end:
                    end = i_end
            else:
                concatenating = False
            if end < i_end:
                if not concatenating:
                    if end_index == -1:
                        concatenating = True
                        end_index = i
                if concatenating:
                    end_index = i
        else:  # (start >= i_start)
            if start <= i_end:
                if start_index == -1:
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
    elif start_index == -1:
        intervals.insert(end_index, [start, end])
        return intervals

    # strict_end and boundary_end
    elif end_index == -1:
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
