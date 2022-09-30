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


class InvalidData(Exception):
    """Исключение, возникающие при некорректных данных, введенных пользователем"""


class InvalidDate(Exception):
    """Исключение, возникающие при обработке неккоректной даты"""


class ValidationError(Exception):
    """Исключение, возникающие при валидации данных"""


class NoSubjectsTaughtByTheTeacher(Exception):
    """
    Исключение, возникающие при невозможности выставить/удалить
    оценки ученикам(-ов) (Например, учитель не ведет ни одного предмета)
    """


class SemanticCommandError(Exception):
    """
    Исключение, возникающие при неверном смысле команды выставления/удаления оценок.
    (Например, при попытке удалить несуществующую оценку)
    """


class ExitGradingCommand(Exception):
    """Исключение, возникающие при желании пользователя выйти из системы оценивания"""
