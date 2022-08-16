from typing import NamedTuple, Literal, Union

from psycopg2.sql import Composed


class Request(NamedTuple):
    sql: Composed
    args: Union[tuple, list]
    type: Literal['with_output', 'without_output']
