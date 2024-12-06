import json
import pymysql
from datetime import datetime

def execute_sql_query_with_params(host: str, user: str, password: str, database: str, port: int, sql_query: str, params: str = None):
    result = {
        "status": 'False',
        "data":  {}
    }

    # Connect to the database
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        cursor = connection.cursor(pymysql.cursors.DictCursor)  # Use DictCursor to return results as dictionaries
    except Exception as e:
        raise ValueError(f"Error connecting to database: {str(e)}")

    try:
        # Parse parameters if provided
        if params:
            try:
                params = json.loads(params)
            except json.JSONDecodeError:
                params = None
        # Determine the type of SQL query
        sql_type = sql_query.strip().split()[0].upper()

        if sql_type == "SELECT":
            # Execute SELECT query
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
            rows = cursor.fetchall()
            # Convert datetime objects to strings
            for row in rows:
                for key in row:
                    if isinstance(row[key], datetime):
                        row[key] = row[key].strftime('%Y-%m-%d %H:%M:%S')
            result["data"] = rows
            result["status"] = 'True'
        else:
            # Execute non-SELECT query (e.g., INSERT, UPDATE, DELETE)
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
            connection.commit()
            result["status"] = 'True'

    except Exception as e:
        raise ValueError(f"Error executing query: {str(e)}")
    finally:
        # Ensure resources are always released
        cursor.close()
        connection.close()
    return result

# Example usage
host = "192.168.4.80"
user = "nexus_ai"
password = "3&hoX0fy7xDs*T0JJ^Qo"
database = "nexus_ai"
port = 3306

sql_update = "UPDATE users SET nickname = %s WHERE id = %s"
params_update = json.dumps(['xxx', 1])

result_update = execute_sql_query_with_params(host, user, password, database, port, sql_update, params_update)
print(result_update)