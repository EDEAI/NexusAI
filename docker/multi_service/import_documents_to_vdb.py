import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
import time
import pymysql
import os
import traceback
from config import settings
from core.database.models import Documents,Datasets,Models
from core.dataset import DatasetManagement
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')

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

def _import_document(document_name: int, user_id: int):
    while True:
        try:
            documents_data = Documents().get_document_find_by_name(document_name, user_id)
            if documents_data:
                print(documents_data)
                dataset_data = Datasets().get_dataset_by_id(documents_data['dataset_id'])
                if dataset_data:
                    embedding_model_config_id = dataset_data['embedding_model_config_id']
                    models_data = Models().get_model_by_config_id(embedding_model_config_id)
                    if models_data:
                        model_config = models_data['supplier_config']
                        if model_config:
                            Documents().update(
                                [
                                    {'column': 'id', 'value': documents_data['id']},
                                    {'column': 'status', 'op': '<', 'value': 3},
                                ],
                                {'status': 1}
                            )
                            DatasetManagement.enable_document(documents_data['id'])
                            break
        except Exception as e:
            print(f'Failed to enable document {documents_data["id"]}: {e}')
        time.sleep(30)


def import_documents(batch_number: int):
    match batch_number:
        case 0:
            document_names = ['Michael Brown-builtin-1734079638.docx',
                            'Jane Doe-builtin-1734079639.docx', 
                            'Emily Johnson-builtin-1734079640.docx',
                            'John Smith-builtin-1734079641.docx',
                            'Technical terms-builtin-1734079699.txt',
                            'Store platform activities-builtin-1734079713.txt',
                            'After-sales support-builtin-1734079723.txt',
                            'Logistics consulting-builtin-1734079737.txt',
                            'Pre-sale of goods-builtin-1734079747.txt']
            for document_name in document_names:
                # built-in user_id is 1
                _import_document(document_name, 1)
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
