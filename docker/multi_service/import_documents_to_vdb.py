import json
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))
import time
import pymysql
import os
from core.database.models import Documents,Datasets,Models
from core.dataset import DatasetManagement
os.environ['DATABASE_AUTO_COMMIT'] = 'False'

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB')

project_root = Path(__file__).absolute().parent.parent.parent
mig_dir = project_root.joinpath('docker', 'multi_service', 'vdb_migrations')
log_dir = project_root.joinpath('logs', 'import_documents_to_vdb')

documents = Documents()
datasets = Datasets()
models = Models()

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
    documents_data = documents.get_document_find_by_name(document_name, user_id)
    print(f'Importing document {documents_data["id"]}...')
    assert documents_data, 'No available document!'
    dataset_data = datasets.get_dataset_by_id(documents_data['dataset_id'])
    assert dataset_data, 'No available dataset!'
    embedding_model_config_id = dataset_data['embedding_model_config_id']
    models_data = models.get_model_by_config_id(embedding_model_config_id)
    assert models_data, 'No available embeddings model!'
    model_config = models_data['supplier_config']
    assert model_config, 'Please set a valid OpenAI API key!'
    documents.update(
        [
            {'column': 'id', 'value': documents_data['id']},
            {'column': 'status', 'op': '<', 'value': 3},
        ],
        {'status': 1}
    )
    DatasetManagement.enable_document(documents_data['id'])
    documents.commit()


def import_documents(batch_number: int):
    while True:
        try:
            print(f'Importing batch {batch_number}...')
            try:
                with mig_dir.joinpath(f'{batch_number}.json').open() as f:
                    document_names = json.load(f)
            except:
                raise Exception('Load JSON file error!')
            for document_name in document_names:
                # built-in user_id is 1
                _import_document(document_name, 1)
            print(f'Batch {batch_number} successfully imported to dataset!')
            break
        except Exception as e:
            print(f'Failed to import batch {batch_number}: {e}')
            documents.close()
        time.sleep(30)

def run_import():
    mig_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    for mig_file in mig_dir.iterdir():
        if mig_file.is_file() and (match := re.fullmatch(r'(\d+)\.json', mig_file.name)):
            batch_number_str = match[1]
            log_file = log_dir.joinpath(batch_number_str)
            if not log_file.exists():
                import_documents(int(batch_number_str))
                log_file.touch()

if __name__ == "__main__":
    wait_for_mysql()
    run_import()
