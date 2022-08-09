class ManyInstanceOfDatabaseError(Exception):
    """Исключение, возникающие при попытке создать второй или более экземпляр класса 'Database'"""


class DontExistUnexecutedRequests(Exception):
    """Исключение, возникающие при попытке обработать SQL-запросы при их отсутсвии"""
