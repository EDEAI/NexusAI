import os
from typing import Any, Dict, List, Union, Optional
from sqlalchemy import Table, select, text, and_, or_, func, JSON
from sqlalchemy.exc import SQLAlchemyError
from . import SQLDatabase
from config import settings

# Define a type alias for conditions to simplify type hints
Condition = Dict[str, Any]
Conditions = Union[Condition, List[Union[Condition, List]]]

def is_auto_commit() -> bool:
    """
    Returns the value of the DATABASE_AUTO_COMMIT environment variable as a boolean.

    :return: True if DATABASE_AUTO_COMMIT is set to 'True', False otherwise.
    """
    return os.getenv('DATABASE_AUTO_COMMIT', 'False').lower() == 'true'

def build_condition(tables: Dict[str, Table], condition: Condition) -> Any:
    """
    Constructs a SQLAlchemy condition expression based on the provided condition dictionary.

    :param tables: A dictionary mapping table names to SQLAlchemy Table objects.
    :param condition: A dictionary representing a single condition with keys for column, operation, and value.
    :return: A SQLAlchemy condition expression.
    """
    column = condition["column"].strip()
    if "." not in column:
        column = tables[list(tables.keys())[0]].c[column]
    else:
        table_name, column_name = column.split(".")
        column = tables[table_name].c[column_name]
    op = condition.get("op", "=").lower().strip()
    value = condition.get("value")
    
    if op == "=":
        return column == value
    elif op == "!=":
        return column != value
    elif op == "<":
        return column < value
    elif op == ">":
        return column > value
    elif op == "<=":
        return column <= value
    elif op == ">=":
        return column >= value
    elif op == "like":
        return column.like(value)
    elif op == "ilike":
        return column.ilike(value)
    elif op == "in":
        return column.in_(value if isinstance(value, list) else [value])
    elif op == "not in":
        return column.notin_(value if isinstance(value, list) else [value])
    elif op == "is null":
        return column == None
    elif op == "is not null":
        return column != None
    else:
        raise ValueError(f"Unsupported operation: {op}")

def build_conditions(tables: Dict[str, Table], conditions: Conditions, logic: str = "and") -> Any:
    """
    Constructs a composite SQLAlchemy condition expression from a list or nested list of conditions.

    :param tables: A dictionary mapping table names to SQLAlchemy Table objects.
    :param conditions: A list or nested list of condition dictionaries or a single condition dictionary.
    :param logic: A string indicating the logical operator to use between conditions ("and" or "or").
    :return: A composite SQLAlchemy condition expression.
    """
    if isinstance(conditions, dict):
        conditions = [conditions]
        
    logic = logic.strip()
    if logic == "and":
        expr = and_
    elif logic == "or":
        expr = or_
    else:
        raise ValueError(f"Unsupported logic: {logic}")
    
    condition_expressions = []
    for condition in conditions:
        if isinstance(condition, list):
            nested_logic = condition[0].get("logic", "and").lower()
            condition_expressions.append(build_conditions(tables, condition, nested_logic))
        else:
            condition_expressions.append(build_condition(tables, condition))
    
    return expr(*condition_expressions)

class ORM(SQLDatabase):
    """
    A class representing a MySQL database, providing methods to execute various SQL operations.
    Inherits from SQLDatabase which is assumed to provide basic database interaction functionality.
    """
    
    def __init__(self):
        """
        Initializes the MySQL database connection using settings from the config module.
        """
        db_url = (
            f"mariadb+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
            "?charset=utf8mb4"
        )
        super().__init__(db_url)

    @classmethod
    def execute_query(cls, query: str) -> Any:
        """
        Executes a given SQL query string and commits the transaction.

        :param query: A SQL query string to be executed.
        :return: The result of the query execution.
        """
        session = cls.get_session()
        auto_commit = is_auto_commit()
        try:
            result = session.execute(text(query))
            if auto_commit:
                session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            if auto_commit:
                session.close()

    @classmethod
    def insert(cls, table_name: str, data: Dict[str, Any]) -> Any:
        """
        Inserts a new record into the specified table.

        :param table_name: The name of the table to insert the record into.
        :param data: A dictionary mapping column names to their respective values for the new record.
        :return: The primary key of the inserted record.
        """
        session = cls.get_session()
        auto_commit = is_auto_commit()
        table = Table(table_name, cls._metadata, autoload_with=cls._engine)
        for column in table.columns:
            if str(column.type) == 'LONGTEXT':
                column.type = JSON()
        try:
            query = table.insert().values(data)
            # print(str(query.compile(compile_kwargs={"literal_binds": True})))
            # print('SQL:')
            # pp(str(query.compile()))
            # print('Data:')
            # pp(data)
            result = session.execute(query)
            if auto_commit:
                session.commit()
            return result.inserted_primary_key[0]
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            if auto_commit:
                session.close()

    @classmethod
    def update(cls, table_name: str, conditions: Conditions, data: Dict[str, Any]) -> bool:
        """
        Updates records in the specified table that match the given conditions.

        :param table_name: The name of the table to update.
        :param conditions: Conditions that determine which records to update.
        :param data: A dictionary mapping column names to their new values.
        :return: True if the update affected one or more rows, False otherwise.
        """
        session = cls.get_session()
        auto_commit = is_auto_commit()
        table = Table(table_name, cls._metadata, autoload_with=cls._engine)
        for column in table.columns:
            if str(column.type) == 'LONGTEXT':
                column.type = JSON()
        try:
            if conditions:
                if isinstance(conditions, List) and isinstance(conditions[0], Dict):
                    nested_logic = conditions[0].get("logic", "and").lower()
                    query = table.update().where(build_conditions({table_name: table}, conditions, nested_logic)).values(data)
                else:
                    query = table.update().where(build_conditions({table_name: table}, conditions)).values(data)
            else:
                query = table.update().values(data)
            # print(str(query.compile(compile_kwargs={"literal_binds": True})))
            # print('SQL:')
            # pp(str(query.compile()))
            # print('Conditions:')
            # pp(conditions)
            # print('Data:')
            # pp(data)
            result = session.execute(query)
            if auto_commit:
                session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            if auto_commit:
                session.close()

    @classmethod
    def _build_select_query(cls, table_name: str, **kwargs: Any) -> Any:
        """
        Helper method to build the select query.

        :param table_name: The name of the table to select records from.
        :param columns: A list of column names to include in the result set. Can be '*' to select all columns.
        :param aggregates: A dictionary where keys are column names and values are aggregation functions (e.g., 'sum', 'avg').
        :param joins: A list of tuples specifying joins. Each tuple contains the join type ('inner', 'left'), the name of the table to join, and the join condition.
        :param conditions: A list or dictionary specifying conditions for filtering the results.
        :param group_by: A string specifying the column names to group the result set by.
        :param having: A string specifying a condition on the aggregated records.
        :param order_by: A string specifying the column names to order the result set by.
        :param limit: An integer specifying the maximum number of records to return.
        :param offset: An integer specifying the number of records to skip before starting to return records from the query.
        :return: A SQLAlchemy select query object.
        """
        columns = kwargs.get('columns')
        aggregates = kwargs.get('aggregates', {})
        joins = kwargs.get('joins')
        conditions = kwargs.get('conditions')
        group_by = kwargs.get('group_by')
        having = kwargs.get('having')
        order_by = kwargs.get('order_by')
        limit = kwargs.get('limit')
        offset = kwargs.get('offset')
        
        table = Table(table_name, cls._metadata, autoload_with=cls._engine)
        for column in table.columns:
            if str(column.type) == 'LONGTEXT':
                column.type = JSON()
        tables = {table_name: table}
        
        if joins:
            for join_type, join_table_name, join_condition in joins:
                join_type = join_type.strip()
                join_table_name = join_table_name.strip()
                if join_table_name not in tables:
                    tables[join_table_name] = Table(join_table_name, cls._metadata, autoload_with=cls._engine)
                    for column in tables[join_table_name].columns:
                        if str(column.type) == 'LONGTEXT':
                            column.type = JSON()
        
        query = select()
        
        if columns:
            if columns == '*':
                for table_name in tables:
                    query = query.add_columns(*tables[table_name].c)
            else:
                for col in columns:
                    col = col.strip()
                    alias = None
                    if ' as ' in col:
                        col, alias = col.split(' as ')
                        col, alias = col.strip(), alias.strip()
                    elif ' AS ' in col:
                        col, alias = col.split(' AS ')
                        col, alias = col.strip(), alias.strip()
                    if '.' in col:
                        table_name, column_name = col.split('.')
                        column = tables[table_name].c[column_name]
                    else:
                        column = table.c[col]
                    if alias:
                        column = column.label(alias)
                    query = query.add_columns(column)
                        
        for col, agg_func in aggregates.items():
            if '.' in col:
                table_name, column_name = col.split('.')
                column = tables[table_name].c[column_name]
            else:
                column = table.c[col]
            
            if agg_func == 'sum':
                query = query.add_columns(func.sum(column).label(f'sum_{col}'))
            elif agg_func == 'avg':
                query = query.add_columns(func.avg(column).label(f'avg_{col}'))
            elif agg_func == 'count':
                query = query.add_columns(func.count(column).label(f'count_{col}'))
            elif agg_func == 'max':
                query = query.add_columns(func.max(column).label(f'max_{col}'))
            elif agg_func == 'min':
                query = query.add_columns(func.min(column).label(f'min_{col}'))
            
        if joins:
            query = query.select_from(table)
            for join_type, join_table_name, join_condition in joins:
                join_type = join_type.strip()
                join_table_name = join_table_name.strip()
                if join_type == 'inner':
                    query = query.join(tables[join_table_name], text(join_condition))
                elif join_type == 'left':
                    query = query.join(tables[join_table_name], text(join_condition), isouter=True)

        if conditions:
            if isinstance(conditions, List) and isinstance(conditions[0], Dict):
                nested_logic = conditions[0].get("logic", "and").lower()
                query = query.where(build_conditions(tables, conditions, nested_logic))
            else:
                query = query.where(build_conditions(tables, conditions))
        if group_by:
            query = query.group_by(text(group_by))
        if having:
            query = query.having(text(having))
        if order_by:
            query = query.order_by(text(order_by))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        return query
    
    @classmethod
    def select(cls, table_name: str, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Selects records from the specified table, optionally applying filters, aggregations, and sorting.

        :param table_name: The name of the table to select records from.
        :param columns: A list of column names to include in the result set. Can be '*' to select all columns.
        :param aggregates: A dictionary where keys are column names and values are aggregation functions (e.g., 'sum', 'avg').
        :param joins: A list of tuples specifying joins. Each tuple contains the join type ('inner', 'left'), the name of the table to join, and the join condition.
        :param conditions: A list or dictionary specifying conditions for filtering the results.
        :param group_by: A string specifying the column names to group the result set by.
        :param having: A string specifying a condition on the aggregated records.
        :param order_by: A string specifying the column names to order the result set by.
        :param limit: An integer specifying the maximum number of records to return.
        :param offset: An integer specifying the number of records to skip before starting to return records from the query.
        :return: A list of dictionaries, each representing a row from the result set.
        """
        session = cls.get_session()
        query = cls._build_select_query(table_name, **kwargs)
        
        # print(str(query.compile(compile_kwargs={"literal_binds": True})))
        # print('SQL:')
        # pp(str(query.compile()))
        # print('kwargs:')
        # pp(kwargs)
        
        try:
            result = session.execute(query)
            rows = result.fetchall()
            columns = result.keys()
            dict_rows = [dict(zip(columns, row)) for row in rows]
            return dict_rows
        except SQLAlchemyError as e:
            raise e
        finally:
            if is_auto_commit():
                session.close()

    @classmethod
    def select_one(cls, table_name: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Selects the first record from the specified table, optionally applying filters, aggregations, and sorting.

        :param table_name: The name of the table to select records from.
        :param columns: A list of column names to include in the result set. Can be '*' to select all columns.
        :param aggregates: A dictionary where keys are column names and values are aggregation functions (e.g., 'sum', 'avg').
        :param joins: A list of tuples specifying joins. Each tuple contains the join type ('inner', 'left'), the name of the table to join, and the join condition.
        :param conditions: A list or dictionary specifying conditions for filtering the results.
        :param group_by: A string specifying the column names to group the result set by.
        :param having: A string specifying a condition on the aggregated records.
        :param order_by: A string specifying the column names to order the result set by.
        :param limit: An integer specifying the maximum number of records to return.
        :param offset: An integer specifying the number of records to skip before starting to return records from the query.
        :return: A dictionary representing the first row from the result set, or None if no records are found.
        """
        kwargs['limit'] = 1
        kwargs['offset'] = 0
        
        session = cls.get_session()
        query = cls._build_select_query(table_name, **kwargs)
        
        # print('SQL:')
        # pp(str(query.compile()))
        # print('kwargs:')
        # pp(kwargs)
        
        try:
            result = session.execute(query)
            row = result.fetchone()
            columns = result.keys()
            if row:
                dict_row = dict(zip(columns, row))
                return dict_row
            else:
                return None
        except SQLAlchemyError as e:
            raise e
        finally:
            if is_auto_commit():
                session.close()

    @classmethod
    def delete(cls, table_name: str, conditions: Conditions) -> bool:
        """
        Deletes records from the specified table that match the given conditions.

        :param table_name: The name of the table to delete records from.
        :param conditions: Conditions that determine which records to delete.
        :return: True if the delete operation affected one or more rows, False otherwise.
        """
        session = cls.get_session()
        auto_commit = is_auto_commit()
        table = Table(table_name, cls._metadata, autoload_with=cls._engine)
        for column in table.columns:
            if str(column.type) == 'LONGTEXT':
                column.type = JSON()
        try:
            if conditions:
                if isinstance(conditions, List) and isinstance(conditions[0], Dict):
                    nested_logic = conditions[0].get("logic", "and").lower()
                    query = table.delete().where(build_conditions({table_name: table}, conditions, nested_logic))
                else:
                    query = table.delete().where(build_conditions({table_name: table}, conditions))
            else:
                query = table.delete()
            # print(str(query.compile(compile_kwargs={"literal_binds": True})))
            # print('SQL:')
            # pp(str(query.compile()))
            # print('Conditions:')
            # pp(conditions)
            result = session.execute(query)
            if auto_commit:
                session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            if auto_commit:
                session.close()