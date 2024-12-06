import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import Dict, List, Optional, Tuple, Union

from . import Node, UPLOAD_FILES_KEY
from ...variables import Variable, ArrayVariable, ObjectVariable, VariableTypes
from core.database.models import AppNodeExecutions, AppRuns, Apps, Datasets, Documents, UploadFiles
from core.dataset import DatasetManagement

project_root = Path(__file__).absolute().parent.parent.parent.parent.parent


class ImportToKBBaseNode(Node):
    '''
    Base class for all Import to Knowledge Base nodes.
    '''
    @classmethod
    def import_variable_to_knowledge_base(
        cls,
        variable: Variable,
        upload_file_id: int,
        source_string_for_db: str,
        source_string_for_kb: str,
        user_id: int,
        dataset_id: int,
        node_exec_id: int,
        is_input: bool
    ) -> None:
        dataset = Datasets().get_dataset_by_id(dataset_id)
        process_rule_id = dataset['process_rule_id']
        document_id = Documents().insert(
            {
                'user_id': user_id,
                'dataset_id': dataset_id,
                'name': source_string_for_db,
                'data_source_type': 4 if is_input else 3,
                'dataset_process_rule_id': process_rule_id,
                'upload_file_id': upload_file_id,
                'node_exec_id': node_exec_id,
                'word_count': 0,
                'tokens': 0
            }
        )
        match variable.type:
            case 'string':
                result = DatasetManagement.add_document_to_dataset(
                    document_id=document_id,
                    dataset_id=dataset_id,
                    process_rule_id=process_rule_id,
                    text=variable.value,
                    is_json=False,
                    source=source_string_for_kb
                )
            case 'file':
                result = DatasetManagement.add_document_to_dataset(
                    document_id=document_id,
                    dataset_id=dataset_id,
                    process_rule_id=process_rule_id,
                    file_path=str(project_root.joinpath(variable.value))
                )
            case 'json':
                result = DatasetManagement.add_document_to_dataset(
                    document_id=document_id,
                    dataset_id=dataset_id,
                    process_rule_id=process_rule_id,
                    text=variable.value,
                    is_json=True,
                    source=source_string_for_kb
                )
            case _:
                # This should never happen
                raise Exception('Invalid variable type!')
        word_count, num_tokens, indexing_latency = result
        Documents().update(
            [
                {'column': 'id', 'value': document_id},
                {'column': 'status', 'value': 1}
            ],
            {
                'word_count': word_count,
                'tokens': num_tokens,
                'indexing_latency': indexing_latency
            }
        )

    @classmethod
    def delete_documents_by_node_exec_id(cls, node_exec_id: int) -> None:
        if node_exec_id > 0:
            documents = Documents().select(
                columns=['id'],
                conditions=[
                    {'column': 'node_exec_id', 'value': node_exec_id},
                    {'column': 'status', 'op': '<', 'value': 3}
                ]
            )
            document_ids = [doc['id'] for doc in documents]
            for id_ in document_ids:
                DatasetManagement.delete_document(id_)
            Documents().soft_delete(
                {'column': 'id', 'op': 'in', 'value': document_ids}
            )
        
    def import_files_to_knowledge_base(
        self,
        knowledge_base_mapping_list: List[Tuple[int, str, str, int]],
        app_run_id: int,
        node_exec_id: int
    ) -> None:
        app_run = AppRuns().select_one(
            columns=['user_id'],
            conditions={'column': 'id', 'value': app_run_id}
        )
        assert app_run, 'Invalid app run ID!'
        user_id = app_run['user_id']
        for file_id, file_name, file_path, dataset_id in knowledge_base_mapping_list:
            file_var = Variable(name='file', type='file', value=file_path)
            file_path = Path(file_path).name
            self.import_variable_to_knowledge_base(
                file_var, file_id, file_name, file_path,
                user_id, dataset_id, node_exec_id, True
            )
    
    def import_variables_to_knowledge_base(
        self,
        variable: VariableTypes,
        knowledge_base_mapping: Dict[str, int],
        app_run_id: int,
        node_exec_id: int,
        is_input: bool,
        source_string: Optional[str] = None
    ) -> None:
        app_run = AppRuns().select_one(
            columns=['user_id', 'app_id'],
            conditions={'column': 'id', 'value': app_run_id}
        )
        assert app_run, 'Invalid app run ID!'
        user_id = app_run['user_id']
        app = Apps().get_app_by_id(app_run['app_id'])
        app_name = app['name']
        for variable_name, dataset_id in knowledge_base_mapping.items():
            if source_string is None:
                source_string_for_db = f'{app_name}-{self.data["title"]}-{variable_name}'
            else:
                source_string_for_db = f'{app_name}-{self.data["title"]}-{source_string}'
            source_string_for_kb = f'{source_string_for_db}-{node_exec_id}'
            if (
                isinstance(variable, Variable) and variable.name == variable_name
                and variable.type in ['string', 'file', 'json']
            ):
                self.import_variable_to_knowledge_base(
                    variable, 0, source_string_for_db, source_string_for_kb,
                    user_id, dataset_id, node_exec_id, is_input
                )
            elif isinstance(variable, ArrayVariable):
                for value in variable.values:
                    if value.name == variable_name:
                        self.import_variable_to_knowledge_base(
                            value, 0, source_string_for_db, source_string_for_kb,
                            user_id, dataset_id, node_exec_id, is_input
                        )
            elif isinstance(variable, ObjectVariable):
                if value := variable.properties.get(variable_name):
                    self.import_variable_to_knowledge_base(
                        value, 0, source_string_for_db, source_string_for_kb,
                        user_id, dataset_id, node_exec_id, is_input
                    )

    def delete_previous_documents(self, level: int, edge_id: str) -> None:
        prev_node_exec = AppNodeExecutions().select_one(
            columns=['id'],
            conditions=[
                {'column': 'level', 'value': level},
                {'column': 'edge_id', 'value': edge_id},
                {'column': 'status', 'value': 3}
            ],
            order_by='id DESC'
        )
        if prev_node_exec:
            self.delete_documents_by_node_exec_id(prev_node_exec['id'])

    def import_inputs_to_knowledge_base_and_get_file_list(
        self,
        app_run_id: int,
        node_exec_id: int,
        allow_upload_file: bool,
        import_to_knowledge_base: bool
    ) -> Optional[ArrayVariable]:
        # Generate file lists for both importing to knowledge base and uploading the LLM model
        file_list = None
        input_kb_mapping: Dict[str, Union[int, Dict[str, int]]] = self.data['knowledge_base_mapping'].get('input', {})
        input_files_kb_mapping: Optional[Dict[str, int]] = input_kb_mapping.pop(UPLOAD_FILES_KEY, None)
        if allow_upload_file:
            file_list = ArrayVariable(name='file_list', type='array[file]')
            upload_files: Optional[ArrayVariable] = self.data['input'].properties.get(UPLOAD_FILES_KEY)
            if upload_files:
                kb_mapping_list = []
                for file in upload_files.values:
                    file_id = file.value
                    file_data = UploadFiles().get_file_by_id(file_id)
                    file_name = file_data['name'] + file_data['extension']
                    file_path = file_data['path']
                    file_list.add_value(
                        Variable(
                            name=file.name,
                            type='file',
                            value=file_path
                        )
                    )
                    if (
                        input_files_kb_mapping
                        and (dataset_id := input_files_kb_mapping.get(file.name))
                    ):
                        kb_mapping_list.append((file_id, file_name, file_path, dataset_id))
                if import_to_knowledge_base and kb_mapping_list:
                    self.import_files_to_knowledge_base(
                        kb_mapping_list, app_run_id, node_exec_id
                    )
        # Import the input variables (except files) to the knowledge base
        if import_to_knowledge_base:
            self.import_variables_to_knowledge_base(
                self.data['input'], input_kb_mapping,
                app_run_id, node_exec_id, True
            )
        return file_list
    