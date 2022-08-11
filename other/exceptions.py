class ManyInstanceOfClassError(Exception):
    """Исключение, возникающие при попытке создать второй или более экземпляр класса 'Database'"""

    def __str__(self) -> str:
        return 'Может сущестовать только один экземпляр данного класса'


class DontExistUnexecutedRequests(Exception):
    """Исключение, возникающие при попытке обработать SQL-запросы при их отсутсвии"""
