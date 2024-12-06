from typing import Any, Dict, List
from core.database import MySQL

class DocumentSegmentRagRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "document_segment_rag_records"
    """
    Indicates whether the `document_segment_rag_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def get_retrieval_history_count(self, dataset_id: int):
        """
        Retrieves the count of records in the `document_segment_rag_records` table.

        :param dataset_id: The ID of the dataset.
        :return: The count of records in the `document_segment_rag_records` table.
        """
        cmd_sql = f"""SELECT 
        (SELECT COUNT(*) FROM 
        (SELECT document_segment_rag_records.rag_record_id FROM document_segment_rag_records 
        INNER JOIN rag_records ON document_segment_rag_records.rag_record_id = rag_records.id 
        WHERE document_segment_rag_records.dataset_id = {dataset_id} 
        GROUP BY document_segment_rag_records.rag_record_id) 
        AS subquery) AS total_count"""
        return self.execute_query(cmd_sql).fetchone()[0]

    def get_retrieval_history_list(self, paging_information: Dict[str, Any], dataset_id: int):
        """
        Retrieves the list of records in the `document_segment_rag_records` table.

        :param paging_information: The paging information.
        :param dataset_id: The ID of the dataset.
        :return: A dictionary containing the list of records in the `document_segment_rag_records` table.
        """
        result = self.select(
            columns=[
                'rag_records.id',
                'rag_records.type',
                'rag_records.input',
                'rag_records.created_time',
            ],
            aggregates={"document_segment_rag_records.rag_record_id": "count"},
            joins=[
                ['inner', 'rag_records', 'document_segment_rag_records.rag_record_id = rag_records.id'],
            ],
            conditions=[
                {'column': 'document_segment_rag_records.dataset_id', 'value': dataset_id},
            ],
            group_by='document_segment_rag_records.rag_record_id',
            order_by='document_segment_rag_records.rag_record_id desc',
            limit=paging_information.get('limit'),
            offset=paging_information.get('offset')
        )
        return {'data': result, 'total_pages': paging_information['total_pages']}


    def get_dataset_id(self, rag_record_id: int) -> int:
        conditions = [
            {'column': 'rag_record_id', 'value': rag_record_id},
        ]
        datasets_id = self.select_one(
            columns=['dataset_id'],
            conditions=conditions,
        )
        return datasets_id['dataset_id']

    def get_retrieval_history_detail(self, rag_record_id: int):
        """
        Retrieves the list of records in the `document_segment_rag_records` table.

        :param rag_record_id: The ID of the rag_record.
        :return: A dictionary containing the list of records in the `document_segment_rag_records` table.
        """
        return self.select(
            columns=[
                'document_segment_rag_records.segment_id as id',
                'document_segments.index_id',
                'document_segments.content',
                'documents.name',
                'document_segment_rag_records.score',
                'document_segment_rag_records.reranking_score',

            ],
            joins=[
                ['inner', 'document_segments', 'document_segment_rag_records.segment_id = document_segments.id'],
                ['inner', 'documents', 'documents.id = document_segment_rag_records.document_id']
            ],
            conditions=[
                {'column': 'document_segment_rag_records.rag_record_id', 'value': rag_record_id},
            ],
        )
