class ManyInstanceOfClassError(Exception):
    """Исключение, возникающие при попытке создать второй или более экземпляр класса"""

    def __str__(self) -> str:
        return 'Может сущестовать только один экземпляр данного класса'


class InstanceCantExist(Exception):
    """Исключение, возникающие при попытке создать экземпляр класса, экземпляры которого создавать запрещено"""

    def __str__(self) -> str:
        return 'Невозможно создать экземпляр'


class DontExistUnexecutedRequests(Exception):
    """Исключение, возникающие при попытке обработать SQL-запросы при их отсутсвии"""

    def __str__(self) -> str:
        return 'Отстувуют запросы для обработки'


class InvalidGradingCommand(Exception):
    """Исключение, возникающие при неправильной команде выставления оценок"""


class ValidationError(Exception):
    """Исключение, возникающие при валидации данных"""
