import json
import logging
from typing import Any, Dict, Generator, List, Tuple

import psycopg2
from dify_plugin import Tool
from dify_plugin.config.logger_format import plugin_logger_handler
from dify_plugin.entities.tool import ToolInvokeMessage
from psycopg2.extras import execute_batch
from sqlglot import exp, parse_one

from provider import dbcn_provider
from tools.api import SQLType, typeOf

logger = logging.getLogger(__name__)
logger.addHandler(plugin_logger_handler)


def extract_values(input: List[Dict[str, Any]], columns: List[str]) -> List[List[Any]]:
    return [[item.get(col) for col in columns] for item in input]


class PGBatchNode(Tool):

    def __init__(self, runtime, session):
        super().__init__(runtime, session)
        try:
            credentials = self.runtime.credentials or runtime.credentials
            self.db_config, _ = dbcn_provider.get_config(credentials)
        except Exception as e:
            logger.error(f"Failed to initialize database conn: {str(e)}")

    def _check_conn(self):
        db_conn = psycopg2.connect(**self.db_config)
        logger.warning(f"Initialized database conn: {db_conn}")
        return db_conn

    def _check_sql_type(self, query) -> Tuple[SQLType, str]:
        try:
            ast = parse_one(query, dialect="postgres")
        except BaseException as ex:
            # maybe ex is pyo3_runtime.PanicException
            raise ValueError(f"SQL syntax error, query={query}. caused by={ex}")

        # 允许Placeholder 转为%s
        for i in ast.find_all(exp.Placeholder):
            i.replace("%s")
        # 允许Parameter 转为%s
        for p in ast.find_all(exp.Parameter):
            # 转换 $0~N
            if p.name.isnumeric():
                namedParam = f"%s "
            else:  # 保留 $argXYZ
                namedParam = f"%({p.name})s "
            p.replace(namedParam)
        return typeOf(ast), ast.sql()

    def _check_query(self, query):
        if query:
            return self._check_sql_type(query)
        raise ValueError("SQL query is required")

    def _invoke(
        self, parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        # 获取sql
        query: str = parameters.get("query")
        args: str | List[Any] = parameters.get("args")
        keys: str | List[str] = parameters.get("keys_of_obj")
        if args:
            args = json.loads(args)
            assert isinstance(args, list), f"Not support: {type(args)}"
        if not args:
            # 当args 为空时，直接返回
            yield self.create_variable_message("affected_rows", -1)
            yield self.create_json_message({"affected_rows": -1})
            return

        sql_type, sql_exp = self._check_query(query)
        if sql_type != SQLType.INSERT:
            raise ValueError(f"Not support: {sql_type}")

        if keys:
            # current args: [{k1:1, k2:2, ...}]
            # keys: [k1,k3]
            # then args: [[1,3]]
            keys = [i.strip() for i in keys.split(",")]
            args = extract_values(args, keys)
        # else: Consider args as list[list]

        conn, cursor = None, None
        try:
            conn = self._check_conn()
            cursor = conn.cursor()

            # 批操作
            # cursor.executemany(exp, args)
            execute_batch(cursor, sql_exp, args)
            conn.commit()

            affected_rows = cursor.rowcount
            logger.warning(
                f"SQL-batch-update exp={sql_exp}, affected_rows={affected_rows}"
            )
            yield self.create_variable_message("affected_rows", affected_rows)
            yield self.create_json_message({"affected_rows": affected_rows})

        except Exception as ex:
            logger.error(f"SQL={sql_exp}, args={args}, {type(ex)}: {ex}")
            raise RuntimeError(f"{type(ex)}: {ex}") from ex
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
