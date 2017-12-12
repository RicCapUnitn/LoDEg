from abc import ABCMeta, abstractmethod
import pickle
import utility_queries as utils  # migrate


class Cache(metaclass=ABCMeta):
    """This class gives a black box for a generic caching system for the system

    Two implementations are provided at hte moment:
    - SQLite: the system work with the Django SQLite to cache data
    - MongoDB: the system works with a generic MongoDB implementation (not ready for production!!)
    """

    @abstractmethod
    def collectDataFromDb(self, systemInfo: dict, user: str = None) -> dict:
        """Queries the db for already computed information.

        Note:
            If the user is defined we query only the userInfo. Otherwise, it means
            that the user is an administrator of the system: in this case we query
            the cache for the whole systemInfo.

        Args:
            user (str): The id of the user whose userInfo we are quering the db.
            systemInfo (dict): The dictionary where the information will be stored.
        Returns:
            The updated SystemInfo dictionary.
        """
        pass

    @abstractmethod
    def saveDataToDb(self, systemInfo: dict, user: str = None):
        """Saves the current information into the database.

        Note:
            If the user is defined we save only the userInfo. Otherwise, it means
            that the user is an administrator of the system: in this case we save
            the whole systemInfo in the cache.

        Args:
             user (str): The id of the user whose userInfo we are saving. Defaults to None.
             systemInfo (dict): The dictionary that contains the information we want to store.
        """
        pass


class CacheMongoDb(Cache):
    """A MongoDb implementation of the cache

    Note: Not ready for production: at the moment the implementation does not support huge data structures; use GridFS to break the structure or a relational DB instead
    """

    def __init__(self, collection):
        """
        Args:
            collection: The collection we use for the cache
        """
        self._collection = collection

    def collectDataFromDb(self, systemInfo: dict, user: str = None):
        if (user is None):
            cursor = self._collection.find_one({'cache_system': 'admin'})
            if (cursor is not None):
                systemInfo = cursor['systemInfo']
                systemInfo['last_update'] = utils.getTimeFromObjectId(cursor[
                                                                      '_id'])
        else:
            # User level info
            cursor = self._collection.find_one(
                {'cache_user_id': user}, {'_id': 0})
            if (cursor is not None):
                systemInfo['users'][
                    cursor['cache_user_id']] = cursor['userInfo']
        return systemInfo

    def saveDataToDb(self, systemInfo: dict, user: str = None):
        if (user is None):
            self._collection.replace_one({'cache_system': 'admin'}, {
                'cache_system': 'admin', 'systemInfo': systemInfo}, upsert=True)
        else:
            self._collection.replace_one({'cache_user_id': user}, {
                'cache_user_id': user, 'userInfo': systemInfo['users'][user]}, upsert=True)


class CacheSQLite(Cache):
    """A SQLite implementation of the cache"""

    def __init__(self):
        from ..models import Cache as DjangoCache, LodegUser

    def collectDataFromDb(self, systemInfo: dict, user: str = None):
        if(user is None):
            # SystemLevel info
            user = LodegUser.objects.get(lodeg_user_id='admin')
            data = DjangoCache.objects.get(user=user).data
        else:
            # UserLevel info
            user = LodegUser.objects.get(lodeg_user_id=user)
            data = DjangoCache.objects.get(user=user).data
        return pickle.loads(data)

    def saveDataToDb(self, systemInfo: dict, user: str = None):
        data = pickle.dumps(systemInfo, pickle.HIGHEST_PROTOCOL)
        if (user is None):
            user = LodegUser.objects.get(lodeg_user_id='admin')
        else:
            user = LodegUser.objects.get(lodeg_user_id=user)
        # Might not be necessary
        DjangoCache.objects.filter(user=user).delete()
        DjangoCache.objects.create(user=user, data=data)
