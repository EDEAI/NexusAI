from enum import Enum

from sqlglot import expressions


class SQLType(Enum):
    UNKNOWN = 0
    SELECT = 1
    DELETE = 2
    INSERT = 3
    UPDATE = 4


def typeOf(obj) -> SQLType:
    if isinstance(obj, expressions.Select):
        return SQLType.SELECT
    elif isinstance(obj, expressions.Insert):
        return SQLType.INSERT
    elif isinstance(obj, expressions.Delete):
        return SQLType.DELETE
    elif isinstance(obj, expressions.Update):
        return SQLType.UPDATE
    else:
        return SQLType.UNKNOWN
