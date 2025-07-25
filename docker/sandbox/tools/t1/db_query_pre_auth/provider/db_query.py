import logging

from dify_plugin import ToolProvider

from tools.db_util import DbUtil


class DbQueryProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        db_type = credentials.get("db_type", "")
        if not db_type:
            raise ValueError("Please select the database type")
        db_host = credentials.get("db_host", "")
        if not db_host:
            raise ValueError("Please fill in the database host")
        db_username = credentials.get("db_username", "")
        if not db_username:
            raise ValueError("Please fill in the database username")
        db_password = credentials.get("db_password", "")
        if not db_password:
            raise ValueError("Please fill in the database password")
        db_port = credentials.get("db_port", "")
        if DbUtil.is_not_empty(db_port) and not db_port.isdigit():
            raise ValueError("Database port can be empty or fill with integer value")
        db_name = credentials.get("db_name", "")
        db_properties = credentials.get("db_properties", "")

        try:
            with DbUtil(db_type=db_type,
                        username=db_username, password=db_password,
                        host=db_host, port=db_port,
                        database=db_name, properties=db_properties) as db:
                db.run_query(db.test_sql())
        except Exception as e:
            logging.exception("Database connection failed: %s", str(e))
            raise RuntimeError(f"Error connection database: {e}") from e
