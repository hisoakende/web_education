from typing import NamedTuple, Literal


class Request(NamedTuple):
    sql: str
    args: tuple
    type: Literal['with_output', 'without_output']
