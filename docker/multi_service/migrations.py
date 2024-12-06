import os
import time
import pymysql

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')

def wait_for_mysql():
    while True:
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DB
            )
            connection.close()
            break
        except pymysql.MySQLError:
            print("Waiting for MySQL to be ready...")
            time.sleep(2)

def run_migrations():
    migrated_dir = "/NexusAI/logs/migrations"
    if not os.path.exists(migrated_dir):
        os.makedirs(migrated_dir)

    migrations_dir = "/NexusAI/docker/multi_service/db_migrations"
    if os.path.isdir(migrations_dir):
        connection = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DB
        )
        try:
            migrations = sorted(os.listdir(migrations_dir))
            for migration in migrations:
                migration_path = os.path.join(migrations_dir, migration)
                migrated_file = os.path.join(migrated_dir, migration)
                if not os.path.isfile(migrated_file):
                    print(f"Running migration: {migration_path}")
                    with open(migration_path, 'r') as file:
                        sql = file.read()
                    sql_statements = sql.split(';')
                    with connection.cursor() as cursor:
                        for statement in sql_statements:
                            if statement.strip():
                                cursor.execute(statement)
                    connection.commit()
                    open(migrated_file, 'a').close()
        finally:
            connection.close()

if __name__ == "__main__":
    wait_for_mysql()
    run_migrations()
