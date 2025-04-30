from sqlalchemy.sql import text
from typing import Any, Dict, List, Optional
from core.database import MySQL
from languages import get_language_content


class Documents(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "documents"
    """
    Indicates whether the `documents` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    
    
    def get_document_by_id(self, document_id: int, user_id: int = 0, language_key: str = 'api_vector_available_document') -> Dict[str, Any]:
        """
        Retrieves the document information for the given document ID.

        :param document_id: The ID of the document.
        :return: A dictionary containing the document information.
        """

        conditions = [
            {'column': 'id', 'value': document_id},
            {'column': 'status', 'op': '<', 'value': 3},
        ]

        if user_id > 0:
            conditions.append({'column': 'user_id', 'value': user_id})

        document = self.select_one(
            columns=['id', 'dataset_id', 'name', 'upload_file_id', 'node_exec_id', 'archived', 'status'],
            conditions=conditions,
        )
        assert document, get_language_content(language_key)
        return document

    def documents_list_count(self, is_where: str = None) -> int:
        """
        Retrieves the total count of documents.

        :param is_where: Additional conditions for the query.
        :return: The total count of documents.
        """
        sql = f"""
            SELECT COUNT(DISTINCT(documents.id)) FROM documents
            LEFT JOIN document_segments ON documents.id = document_segments.document_id
            WHERE 1 {is_where}
        """
        # cmd_sql = text(sql)
        return self.execute_query(sql).fetchone()[0]

    def documents_list(self, paging_information: Dict[str, Any], conditions: List[Dict[str, Any]]):
        """
        Retrieves the list of documents.

        :param paging_information: The paging information.
        :param conditions: The  list of conditions.
        :return: A list of documents.
        """
        data = self.select(
            columns=[
                'documents.id', 'documents.data_source_type', 'documents.name',
                'documents.word_count', 'documents.created_time', 'documents.status', 'documents.archived'
            ],
            aggregates={'document_segments.hit_count': 'sum'},
            joins=[
                ['left', 'document_segments', 'documents.id = document_segments.document_id']
            ],
            conditions=conditions,
            group_by='documents.id',
            order_by=paging_information['file_time'],
            limit=paging_information.get('limit'),
            offset=paging_information.get('offset')
        )
        return {'data': data, 'total_pages': paging_information['total_pages']}

    def documents_dataset_process_rules(self, document_id: int) -> Dict[str, Any]:
        """
        Processes the document dataset process rules.

        :param document_id: The ID of the document.
        :return: A dictionary containing the document information.
        """
        data = self.select_one(
            columns=['documents.indexing_latency', 'documents.tokens', 'documents.text_split_config', 'dataset_process_rules.config'],
            joins=[
                ['left', 'dataset_process_rules', 'documents.dataset_process_rule_id = dataset_process_rules.id'],
            ],
            conditions=[
                {'column': 'documents.id', 'value': document_id},
                {'column': 'documents.status', 'op': '<', 'value': 3},
            ],
        )
        return data

    def get_document_by_is_public(self,document_id: int, team_id: int) -> int:
        """
        Retrieves the document information for the given document ID.

        :param document_id: The ID of the document.
        :return: Permission state
        """
        is_public = self.select_one(
            columns=['apps.is_public'],
            joins=[
                ['left', 'datasets', 'documents.dataset_id = datasets.id'],
                ['left', 'apps', 'datasets.app_id = apps.id']
            ],
            conditions=[
                {'column': 'documents.id', 'value': document_id},
                {'column': 'datasets.team_id', 'value': team_id},
                {'column': 'apps.team_id', 'value': team_id},
            ],
        )
        assert is_public, get_language_content('api_vector_auth')
        return is_public['is_public']

    def get_document_find(self, document_id: int, user_id: int) -> Dict[str, Any]:
        """
        Retrieves the document information for the given document ID.

        :param document_id: The ID of the document.
        :return: A dictionary containing the document information.
        """
        result = self.select_one(
            columns=['documents.id'],
            joins=[
                ['left', 'datasets', 'documents.dataset_id = datasets.id'],
            ],
            conditions=[
                {'column': 'documents.id', 'value': document_id},
                {'column': 'documents.user_id', 'value': user_id},
                {'column': 'datasets.user_id', 'value': user_id},
            ],
        )
        assert result, get_language_content('api_vector_auth')
        return result
    
    def get_document_find_by_name(self, document_name: str, user_id: int) -> Dict[str, Any]:
        """
        Retrieves the document information for the given document ID.

        :param document_id: The ID of the document.
        :return: A dictionary containing the document information.
        """
        result = self.select_one(
            columns=['documents.id','documents.dataset_id'],
            joins=[
                ['left', 'datasets', 'documents.dataset_id = datasets.id'],
            ],
            conditions=[
                {'column': 'documents.name', 'value': document_name},
                {'column': 'documents.user_id', 'value': user_id},
                {'column': 'datasets.user_id', 'value': user_id},
            ],
        )
        assert result, get_language_content('api_vector_auth')
        return result


    def get_file_path_by_id(self, document_id: int) -> Optional[str]:
        """
        Get file path by document id.

        :param document_id: The ID of the document.
        :return: File path.
        """
        document = self.select_one(
            columns=['upload_files.path'],
            joins=[
                ['left', 'upload_files', 'documents.upload_file_id = upload_files.id'],
            ],
            conditions=[
                {'column': 'documents.id', 'value': document_id},
            ],
        )
        if document:
            return document['path']
        return None

    def get_document_file_path_list(self,dataset_id: int) -> List[Dict[str,Any]]:
        """
        Get file path by dataset id.

        :param dataset_id: The ID of the dataset.
        :return: File path.
        """
        return self.select(
            columns=['upload_files.path'],
            joins=[
                ['left', 'upload_files', 'documents.upload_file_id = upload_files.id'],
            ],
            conditions=[
                {'column': 'documents.dataset_id', 'value': dataset_id},
            ],
            group_by='upload_files.id',
        )


    def document_segments_count(self, conditions: List[Dict[str,Any]]) -> int:
        """
        Count the number of document segments.

        :param conditions: The conditions for the query.
        :return: The count of document segments.
        """
        return self.select_one(
            aggregates={"document_segments.id": "count"},
            joins = [
                ['left', 'document_segments', 'documents.id = document_segments.document_id']
            ],
            conditions=conditions,
        )['count_document_segments.id']

    def document_segments_list(self, paging_information: Dict[str, Any], conditions: Dict[str, Any]) -> Dict[str, Any]:
        data = self.select(
            columns=['document_segments.id', 'document_segments.content', 'document_segments.word_count', 'document_segments.hit_count', 'document_segments.status'],
            joins = [
                ['left', 'document_segments', 'documents.id = document_segments.document_id']
            ],
            conditions=conditions,
            order_by=paging_information['hit_count'],
            limit=paging_information.get('limit'),
            offset=paging_information.get('offset')
        )
        return {'data': data, 'total_pages': paging_information['total_pages']}

    def get_document_indexing_status(self, document_id: int) -> Dict[str, Any]:
        """
        Get document indexing status

        :param document_id: The ID of the document.
        :return: Indexing status 0: Not indexed 1: Being indexed 2: Successfully indexed 3: Failed to be indexed
        """
        return self.select_one(
            columns=['document_segments.indexing_status'],
            joins=[
                ['left', 'document_segments', 'documents.id = document_segments.document_id']
            ],
            conditions=[
                {'column': 'documents.id', 'value': document_id},
                {'column': 'documents.status', 'op': '<', 'value': 3},
                {'column': 'document_segments.status', 'op': '<', 'value': 3},
                {'column': 'document_segments.indexing_status', 'value': 1},
            ],
        )