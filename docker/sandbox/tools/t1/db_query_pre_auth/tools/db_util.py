import datetime
import logging
from typing import Optional
from urllib import parse
from uuid import UUID

import oracledb
import pandas as pd
from pandas import Timestamp
from sqlalchemy import create_engine


class DbUtil:

    def __init__(self, db_type: str,
                 username: str, password: str,
                 host: str, port: Optional[str] = None,
                 database: Optional[str] = None,
                 properties: Optional[str] = None) -> None:
        self.db_type = db_type.lower()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.properties = properties
        if self.db_type == 'oracle11g':
            # To change from the default python-oracledb Thin mode to Thick mode
            oracledb.init_oracle_client()
        self.engine = create_engine(self.get_url(), pool_size=100, pool_recycle=36)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_driver_name(self):
        driver_name = self.db_type
        if self.db_type == 'mysql':
            driver_name = 'mysql+pymysql'
        elif self.db_type in {'oracle', 'oracle11g'}:
            driver_name = 'oracle+oracledb'
        elif self.db_type == 'postgresql':
            driver_name = 'postgresql+psycopg2'
        elif self.db_type == 'mssql':
            driver_name = 'mssql+pymssql'
        return driver_name

    def get_url(self):
        '''
        Get url
        '''
        parsed_username = parse.quote_plus(self.username)
        parsed_password = parse.quote_plus(self.password)
        parsed_host = parse.quote_plus(self.host)
        url = f"{self.get_driver_name()}://{parsed_username}:{parsed_password}@{parsed_host}"
        if self.is_not_empty(self.port):
            url = f"{url}:{str(self.port)}"
        url = f"{url}/"
        if self.is_not_empty(self.database):
            parsed_database = parse.quote_plus(self.database)
            url = f"{url}{parsed_database}"
        if self.is_not_empty(self.properties):
            url = f"{url}?{self.properties}"
        logging.info(f"url: {url}")
        return url

    def close(self):
        """Close all connections in the engine."""
        self.engine.dispose()

    def run_query(self, query_sql: str) -> list[dict]:
        '''
        Run SQL Query
        '''
        query_sql = query_sql.replace('%', '%%')
        df = pd.read_sql_query(sql=query_sql, con=self.engine, parse_dates="%Y-%m-%d %H:%M:%S")
        df = df.fillna('')
        records = []
        if len(df) > 0:
            records = df.to_dict(orient="records")
        for record in records:
            for key in record:
                if type(record[key]) is Timestamp:
                    record[key] = record[key].strftime('%Y-%m-%d %H:%M:%S')
                if type(record[key]) is datetime.date:
                    record[key] = record[key].strftime('%Y-%m-%d')
                if type(record[key]) is UUID:
                    record[key] = str(record[key])
        return records

    def test_sql(self):
        if self.db_type in {'oracle', 'oracle11g'}:
            return "SELECT 1 FROM DUAL"
        else:
            return "SELECT 1"

    @staticmethod
    def is_not_empty(s: str):
        return s is not None and s.strip() != ""
