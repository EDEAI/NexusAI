import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
import pymysql
import hashlib
import os
import time
from config import settings

# Get the initial admin password from command line input
init_admin_password = input("Enter the initial admin password: ")

# Database connection information

MYSQL_HOST = settings.MYSQL_HOST
MYSQL_PORT = int(settings.MYSQL_PORT)
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_DB = settings.MYSQL_DB

print(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT)
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
    INIT_ADMIN_PASSWORD = input("Enter the initial admin password: ")
    # Connect to the MySQL database
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        db=MYSQL_DB
    )

    try:
        with connection.cursor() as cursor:
            # Query the current password of the admin
            cursor.execute("SELECT password, password_salt FROM users WHERE id = 1")
            result = cursor.fetchone()

            if result:
                current_password_hash, password_salt = result

                # Encrypt the password using MD5 with salt
                password_with_salt = hashlib.md5((hashlib.md5(INIT_ADMIN_PASSWORD.encode()).hexdigest() + password_salt).encode()).hexdigest()

                if current_password_hash != password_with_salt:
                    # Update the password
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