import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
import time
import pymysql

from config import settings
from core.database.models import Documents
from core.dataset import DatasetManagement


MYSQL_HOST = settings.MYSQL_HOST
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_DB = settings.MYSQL_DB

project_root = Path(__file__).absolute().parent.parent
log_dir = project_root.joinpath('logs', 'import_documents_to_vdb')


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

def _import_document(documents_id: int, user_id: int):
    Documents().get_document_find(documents_id, user_id)
    documents_data = Documents().get_document_by_id(documents_id, user_id, 'api_vector_auth')
    if documents_data['archived'] == 1:
        print('The current document has been archived and cannot be operated')
        return
    Documents().update(
        [
            {'column': 'id', 'value': documents_id},
            {'column': 'status', 'op': '<', 'value': 3},
        ],
        {'status': 1}
    )
    DatasetManagement.enable_document(documents_id)


def import_documents(batch_number: int):
    match batch_number:
        case 0:
            document_ids = [1, 2, 3, 4, 5, 6, 7, 8]
            for document_id in document_ids:
                _import_document(document_id, 1)
            print(f'Batch {batch_number} successfully imported to dataset!')
            return
        case _:
            print('Invalid batch number:', batch_number)

def run_import():
    log_dir.mkdir(parents=True, exist_ok=True)
    for batch_number in range(1):
        log_file = log_dir.joinpath(str(batch_number))
        if not log_file.exists():
            import_documents(batch_number)
            log_file.touch()

if __name__ == "__main__":
    wait_for_mysql()
    run_import()
