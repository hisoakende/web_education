from typing import NamedTuple, Literal

from psycopg2.sql import Composed


class Request(NamedTuple):
    sql: Composed
    args: list[int, str]
    type: Literal['with_output', 'without_output']
