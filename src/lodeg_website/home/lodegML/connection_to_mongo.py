""" This file contains the function connect_to_mongo, used to connect to the mongoDB instance.

    Args:
        url : url to the database (optional, default="mongodb://127.0.0.1:27017").
        db_name : the name of the MongoDb (otional, default="lodeg").
        user : the username used to connect to the database (optional, not implemented yet).
        password : the password used to connect to the database (otional, not implemented yet)  .
    Returns:
        db: the connection to the database
"""

import pymongo
from pymongo import MongoClient
import urllib.parse


def connect_to_mongo(uri="mongodb://127.0.0.1:27017", db_name="lodeg", username=None, password=None):

    if (username is not None) and (password is not None):
        username = urllib.parse.quote_plus(username)
        password = urllib.parse.quote_plus(password)
        host = uri.split('//')[1]
        uri = "mongodb://" + "%s:%s@" % (username, password) + host

    client = MongoClient(uri)
    db = client.get_database(db_name)

    return db
