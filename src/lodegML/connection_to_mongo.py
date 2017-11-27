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


def connect_to_mongo(url="mongodb://127.0.0.1:27017", db_name="lodeg"):
    client = pymongo.MongoClient(url)
    db = client.get_database(db_name)
    return db
