import os
import time
import pymysql
import hashlib

MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
MYSQL_DB = os.environ.get('MYSQL_DB')
INIT_ADMIN_PASSWORD = os.environ.get('INIT_ADMIN_PASSWORD')
print(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, INIT_ADMIN_PASSWORD)
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

def init_admin_password():
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT password, password_salt FROM users WHERE id = 1")
            result = cursor.fetchone()

            if result:
                current_password_hash, password_salt = result

                password_with_salt = hashlib.md5((hashlib.md5(INIT_ADMIN_PASSWORD.encode()).hexdigest() + password_salt).encode()).hexdigest()

                if current_password_hash != password_with_salt:
                    cursor.execute(
                        "UPDATE users SET password = %s WHERE id = 1",
                        (password_with_salt,)
                    )
                    connection.commit()
                    print("Admin password updated.")
                else:
                    print("Admin password is already up-to-date.")
            else:
                print("Admin user not found.")
    finally:
        connection.close()

if __name__ == "__main__":
    wait_for_mysql()
    init_admin_password()