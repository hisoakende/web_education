import enum
from typing import Any


class ExtendedEnumMeta(enum.EnumMeta):

    def __contains__(cls, item: Any) -> str:
        return item in sum([[val, val.value, val.name] for val in cls], [])


class WhatToDoWithLogin(enum.Enum, metaclass=ExtendedEnumMeta):
    authentication = '1'
    registration = '2'


class ProfileType(enum.Enum, metaclass=ExtendedEnumMeta):
    student = '1'
    teacher = '2'
    administrator = '3'


class CreateUser(enum.Enum, metaclass=ExtendedEnumMeta):
    yes = '1'
    no = '2'


class EnumSchoolClassConstructor(enum.Enum, metaclass=ExtendedEnumMeta):

    def __str__(self) -> str:
        return self.name
