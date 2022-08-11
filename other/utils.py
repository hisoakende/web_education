from other.exceptions import ManyInstanceOfClassError


class Singleton:
    """Класс, реализующий паттерн singleton. Не дает создавать более одного экземпляра данного класса"""

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance:
            raise ManyInstanceOfClassError
        cls.__instance = super().__new__(cls)
        return cls.__instance


class ClassOrInstanceProperty:

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, instance, owner):
        if instance:
            return self.fget(instance)
        return self.fget(owner)
