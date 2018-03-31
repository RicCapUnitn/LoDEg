class ImportException(Exception):
    pass


class ExportException(Exception):
    pass


class AutoPlotException(Exception):
    pass


class InvalidSessionException(Exception):
    pass


class LessonNotFoundExeption(Exception):

    def __init__(self, message, timestamp):
        super().__init__(message)
        self.timestamp = timestamp
