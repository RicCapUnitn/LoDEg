from ..lodegML import utility_queries as utils  # migrate
from ..lodegML import exceptions  # migrate
from ..lodegML.exceptions import ImportException, ExportException  # migrate

import json
import pickle


def import_data(systemInfo: dict, filename: str, overwrite: bool = False):
    """Import the whole system or a part of it

    Args:
        systemInfo (dict): the systemInfo where to import the data
        filename (str): the filename (filepath) that we are importing;
        overwrite (bool): if the imported information is already present in the system and overwrite = False then a message is returned and the file is not imported. Defaults to False.
    Returns:
        A message containing the import status and the imported dictionary; Done if sucessful

    Todo:
        * update the returns section
    """

    data = None

    try:
        if filename.endswith('.json'):
            with open(filename, 'r') as fp:
                data = json.load(fp)
        elif filename.endswith('.p'):
            with open(filename, 'rb') as fp:
                data = pickle.load(fp)
        else:
            raise ImportException('File format not supported')
    except FileNotFoundError as exc:
        raise ImportException('File not found: {}'.format(filename)) from exc

    try:
        insertion_position = data['insertion_position']
        insertion_key = data['insertion_key']
        data = data['data']
    except KeyError as exc:
        raise ImportException(
            'The file is corrupted and does not contain the appropriate metadata') from exc

    system_flag = False
    tokens = insertion_key.split()

    try:
        if insertion_position == 'session':
            insertion_position = systemInfo['courses'][
                tokens[0]]['users'][tokens[1]]['sessions']
            insertion_key = tokens[2]
        elif insertion_position == 'user':
            insertion_position = systemInfo[
                'courses'][tokens[0]]['users']
            insertion_key = tokens[1]
        elif insertion_position == 'course':
            insertion_position = systemInfo['courses']
            insertion_key = tokens[0]
        elif insertion_position == 'system':
            insertion_position = systemInfo
            system_flag = True
    except KeyError as exc:
        raise ImportException(
            'Some layers above the level you are inserting are not present in the system') from exc
    except IndexError or TypeError as exc:
        raise ImportException(
            'Metadata are corrupted; the file cannot be imported') from exc

    if system_flag:
        if not overwrite:
            if len(systemInfo['courses']) > 0:
                raise ImportException(
                    'Trying to overwrite the whole system without permissions; try overwrite = True')
        systemInfo = data
    else:
        if not overwrite:
            if insertion_key in insertion_position.keys():
                raise ImportException(
                    'Import has overwrite conflict; try to launch with overwrite = True')
        insertion_position[insertion_key] = data

    return systemInfo


def export_data(
        systemInfo: dict, export_type: str, course: str=None, user: str=None,
        session: str=None, selected_keys: list=None, excluded_keys: list=None,
        pretty_printing: bool=False, folder: str= './'):
    """Export the whole system or a part of it.

    The json and the binary .p formats are supported.

    Args:
        systemInfo (dict): the systemInfo that contains the data to be exported;
        export_type (str): 'json' or 'bytes' export types are supported;
        course (str): if set the target CourseInfo is exported;
        user (str): if both course and user are set, the target UserInfo is exported;
        session (str): if all course, user and session are set, the target SessionInfo is exported;
        selected_keys (list of str): the keys (stats) that you want to export. Defaults to all;
        excluded_keys (list of str): the keys (stats) that you do not want to export. Defaults to None;
        pretty_printing (bool): if True json will be formatted with 4-spaces indentation. Defaults to False.
        folder (str): the folder where to save the file.

    Raises:
        KeyError: if the objective (the data to be exported) is not found.
    """

    data = None
    title = None
    insertion_level = 'system'
    insertion_key = ''

    # Locate the target data
    try:
        if course:
            if user:
                if session:
                    # SessionInfo
                    title = '{}-{}-{}'.format(course, user, session)
                    data = systemInfo['courses'][course][
                        'users'][user]['sessions'][session]
                    insertion_position = 'session'
                    insertion_key = '{} {} {}'.format(
                        course, user, session)
                else:
                    # UserInfo
                    title = '{}-{}'.format(course, user)
                    data = systemInfo['courses'][
                        course]['users'][user]
                    insertion_position = 'user'
                    insertion_key = '{} {}'.format(course, user)
            else:
                # CourseInfo
                title = course
                data = systemInfo['courses'][course]
                insertion_position = 'course'
                insertion_key = course
        else:
            # SystemInfo
            title = 'system'
            data = systemInfo
            insertion_position = 'system'
            insertion_key = ''

        # Select only requested keys
        dict_keys = set(data.keys())
        if selected_keys:
            target_keys = set(selected_keys)
            for unwanted_key in dict_keys - target_keys:
                del data[unwanted_key]
        if excluded_keys:
            for unwanted_key in dict_keys & set(excluded_keys):
                del data[unwanted_key]

    except KeyError:
        title = 'damaged'
        data = {'objective': 'not found'}

    # Json file
    if export_type == 'json':
        with open(folder + title + '-export.json', 'w') as fp:
            if pretty_printing:
                json.dump({'insertion_position': insertion_position,
                           'insertion_key': insertion_key, 'data': data},
                          fp, indent=4, skipkeys=True, cls=utils.BetterEncoder)
            else:
                json.dump({
                    'insertion_position': insertion_position,
                    'insertion_key': insertion_key,
                    'data': data}, fp, skipkeys=True, cls=utils.BetterEncoder)

    # Binary file
    elif export_type == 'bytes':
        with open(folder + title + '-export.p', 'wb') as fp:
            pickle.dump({
                'insertion_position': insertion_position,
                'insertion_key': insertion_key,
                'data': data}, fp)
