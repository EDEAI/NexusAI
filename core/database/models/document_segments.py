from typing import Any, Dict, List
from core.database import MySQL
from languages import get_language_content


class DocumentSegments(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "document_segments"
    """
    Indicates whether the `document_segments` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    

    def get_segment_by_id(self, segment_id: int) -> Dict[str, Any]:
        """
        Retrieves the document segment information for the given segment ID.

        :param segment_id: The ID of the document segment.
        :return: A dictionary containing the document segment information.
        """
        segment = self.select_one(
            columns=['id','document_id', 'index_id','content'],
            conditions=[
                {'column': 'id', 'value': segment_id},
                {'column': 'status', 'op' : '<', 'value': 3},
            ]
        )
        assert segment, get_language_content('api_vector_document_segment')
        return segment
    
    
    def get_segments_by_document_id(self, document_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the document segment information for the given document ID.

        :param document_id: The ID of the document.
        :return: A list of dictionaries containing the document segment information.
        """
        segments = self.select(
            columns=['id', 'content'],
            conditions=[
                {'column': 'document_id', 'value': document_id},
                {'column': 'status', 'value': 1},
            ]
        )
        return segments

    def get_segment_by_index_id(self, index_id: str) -> Dict[str, Any]:
        segment = self.select_one(
            columns=['id', 'document_id', 'hit_count'],
            conditions=[
                {'column': 'index_id', 'value': index_id},
                {'column': 'status', 'value': 1}
            ]
        )
        assert segment, 'No available document segment!'
        return segment

    def document_segments_file_set(self, document_id: int) -> Dict[str, Any]:
        """
        Retrieve the set of file names associated with the given document ID.

        :param document_id: The ID of the document.
        :return: Statistical result.
        """
        return self.select_one(
            aggregates={'word_count': 'avg', 'id': 'count', 'hit_count': 'sum'},
            conditions=[
                {'column': 'document_id', 'value': document_id},
                {'column': 'status', 'op': '<', 'value': 3}
            ],
        )
        
    def increment_hit_count(self, segment_id: int) -> bool:
        """
        Increments the hit_count field by 1 for the specified document segment.

        :param segment_id: The ID of the document segment to update.
        :return: True if the update affected one or more rows, False otherwise.
        """
        sql = f"UPDATE {self.table_name} SET hit_count = hit_count + 1, updated_time = NOW() WHERE id = {segment_id}"
        result = self.execute_query(sql)
        return result.rowcount > 0

    def get_segment_filename_content(self, index_id: str) -> Dict[str, Any]:
        """
        Retrieves the file name and content for the specified document segment.

        :param index_id: The index ID of the document segment.
        :return: A dictionary containing the file name and content.
        """
        return self.select_one(
            columns=[
                'document_segments.id',
                'document_segments.index_id',
                'document_segments.content',
                'documents.name'
            ],
            joins=[
                ['left', 'documents', 'documents.id = document_segments.document_id']
            ],
            conditions= [
                {'column': 'document_segments.index_id', 'value': index_id}
            ]
        )

    def get_segment_indexing_status(self, segment_id: int) -> Dict[str, Any]:
        """
        Retrieves the indexing_status field for the specified document segment.

        :param segment_id: The ID of the document segment.
        :return: A dictionary containing the indexing_status field.
        """
        return self.select_one(
            columns=['indexing_status'],
            conditions=[
                {'column': 'id', 'value': segment_id},
                {'column': 'indexing_status', 'value': 1},
                {'column':'status', 'op': '<', 'value': 3}
            ]
        )