import logging
from typing import Any, Dict, Generator, Tuple

import psycopg2
from dify_plugin import Tool
from dify_plugin.config.logger_format import plugin_logger_handler
from dify_plugin.entities.tool import ToolInvokeMessage
from jinja2 import Template
from sqlglot import exp, parse_one

from provider import dbcn_provider
from tools.api import SQLType, typeOf

logger = logging.getLogger(__name__)
logger.addHandler(plugin_logger_handler)


class PGNode(Tool):

    def __init__(self, runtime, session):
        super().__init__(runtime, session)
        try:
            credentials = self.runtime.credentials or runtime.credentials
            self.db_config, config = dbcn_provider.get_config(credentials)
            self.max_fetched_rows = config["max_fetched_rows"]
            if not self.max_fetched_rows:
                self.max_fetched_rows = 100
        except Exception as e:
            logger.error(f"Failed to initialize database conn: {str(e)}")

    def _check_conn(self):
        """
        插件短生命周期无法建立连接池
        """
        db_conn = psycopg2.connect(**self.db_config)
        logger.warning(f"Initialized database conn: {db_conn}")
        return db_conn

    def _check_query(self, query: str, parameters: Dict) -> Tuple[SQLType, str]:
        """
        1. 对条件化模板sql进行渲染 获得当前参数条件下准确sql语句
        2. 进行sql语法分析ast 找到参数变量后替换为psycopg2的命名参数
        3. 基于语法分析ast 确定该sql的DML类型
        """
        if not query:
            raise ValueError("SQL query is required")

        # {% ... %} for Statements
        # {{ ... }} for Expressions to print to the template output
        # {# ... #} for Comments not included in the template output
        if "{" in query:
            # 使用jinja2处理动态SQL
            tpl: Template = Template(query)
            query = tpl.render(parameters)  # Ex.

        try:
            ast = parse_one(query, dialect="postgres")  # Ex.
        except BaseException as ex:
            # maybe ex is pyo3_runtime.PanicException
            raise ValueError(f"SQL syntax error, query={query}. caused by={ex}")

        # logger.warning(f"SQL exp={ast} type={type(ast)}")
        for p in ast.find_all(exp.Placeholder):
            raise ValueError("Not allowed Placeholder -> `?`, Should use `$arg0~N`")
        for p in ast.find_all(exp.Parameter):
            if p.name.isnumeric():
                namedParam = f"%(arg{p.name})s "
            else:
                namedParam = f"%({p.name})s "
            p.replace(namedParam)
        return typeOf(ast), ast.sql()  # Ex.

    def _invoke(
        self, parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query: str = parameters.get("query")

        sql_type, sql_exp = self._check_query(query, parameters)
        conn = self._check_conn()
        cursor = None
        try:
            cursor = conn.cursor()
            # 已经是psycopg2的参数语法
            # cursor.execute(sql_exp, parameters)

            match sql_type:
                case SQLType.SELECT:
                    cursor.execute(sql_exp, parameters)
                    columns = [cn[0] for cn in cursor.description]
                    results = cursor.fetchmany(self.max_fetched_rows)

                    logger.warning(f"SQL-select exp={sql_exp}, count={len(results)}")
                    yield self.create_variable_message("data", results)
                    yield self.create_variable_message("columns", columns)
                    data = [dict(zip(columns, row)) for row in results]
                    yield self.create_json_message({"data": data})

                case SQLType.INSERT | SQLType.UPDATE | SQLType.DELETE:
                    cursor.execute(sql_exp, parameters)
                    conn.commit()
                    affected_rows = cursor.rowcount

                    logger.warning(
                        f"SQL-update exp={sql_exp}, affected_rows={affected_rows}"
                    )
                    yield self.create_variable_message("affected_rows", affected_rows)
                    yield self.create_json_message({"affected_rows": affected_rows})

                case _:
                    raise ValueError("Invalid operation type")
        except Exception as ex:
            logger.exception(f"SQL={sql_exp}, casued by={type(ex)}: {ex}")
            raise RuntimeError(f"{type(ex)}: {ex}") from ex

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
