import sys, os
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
import time
import pymysql
from config import settings

MYSQL_HOST = settings.MYSQL_HOST
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_DB = settings.MYSQL_DB

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
    project_root = Path(__file__).absolute().parent.parent
    migrated_dir = project_root / "logs/migrations"
    if not migrated_dir.exists():
        migrated_dir.mkdir(parents=True)

    migrations_dir = project_root / "docker/multi_service/db_migrations"
    if migrations_dir.is_dir():
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
                migration_path = migrations_dir / migration
                migrated_file = migrated_dir / migration
                if not migrated_file.is_file():
                    print(f"Running migration: {migration_path}")
                    with open(migration_path, 'r') as file:
                        sql = file.read()
                    sql_statements = sql.split(';')
                    with connection.cursor() as cursor:
                        for statement in sql_statements:
                            if statement.strip():
                                cursor.execute(statement)
                    connection.commit()
                    migrated_file.touch()
        finally:
            connection.close()

if __name__ == "__main__":
    wait_for_mysql()
    run_migrations()
