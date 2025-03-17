from time import monotonic
from typing import Any, Dict, List, Optional, Union

from langchain_core.documents import Document

from . import Node
from ..context import Context, replace_variable_value_with_context
from ..variables import ArrayVariable, ObjectVariable, Variable, validate_required_variable, get_first_variable_value
from core.database.models import Documents, DocumentSegments
from core.dataset import DatasetRetrieval
from log import Logger


logger = Logger.get_logger('celery-app')


class RetrieverNode(Node):
    """
    A RetrieverNode object is used to retrieve data from a knowledge base.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        input: Optional[Union[Variable, ArrayVariable, ObjectVariable]] = None,
        datasets: List[int] = [],
        manual_confirmation: bool = False, 
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a RetrieverNode object.
        """
        init_kwargs = {
            "type": "retriever",
            "title": title,
            "desc": desc,
            "input": input,
            "datasets": datasets,
            "manual_confirmation": manual_confirmation,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        workflow_id: int = 0,
        user_id: int = 0,
        type: int = 0,
        app_run_id: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = monotonic()
            
            replace_variable_value_with_context(self.data['input'], context)
            validate_required_variable(self.data['input'])
            
            # RAG chain generation
            match len(self.data['datasets']):
                case 0:
                    raise Exception('No dataset selected!')
                case 1:
                    retrieval, _, retrieval_token_counter = DatasetRetrieval.single_retrieve(
                        self.data['datasets'][0], 0, 0, workflow_id, app_run_id, user_id, type
                    )
                case _:
                    retrieval, _, retrieval_token_counter = DatasetRetrieval.multiple_retrieve(
                        self.data['datasets'], 0, 0, workflow_id, app_run_id, user_id, type
                    )
            retrieval_result: List[Document] = retrieval.invoke(get_first_variable_value(self.data['input']))
            outputs = ArrayVariable(name='output', type='array[object]')
            for i, segment_obj in enumerate(retrieval_result):
                segment_var = ObjectVariable(
                    name=f'segment_{i}',
                    display_name=f'Segment {i}',
                    to_string_keys=['content', 'source']
                )
                index_id = str(segment_obj.metadata['index_id'])
                segment = DocumentSegments().get_segment_by_index_id(index_id)
                document = Documents().get_document_by_id(segment['document_id'])
                segment_var.add_property(
                    'content',
                    Variable(
                        name='content',
                        display_name='Content',
                        type='string',
                        value=segment_obj.page_content
                    )
                )
                segment_var.add_property(
                    'segment_id',
                    Variable(
                        name='segment_id',
                        display_name='Segment ID',
                        type='number',
                        value=segment['id']
                    )
                )
                segment_var.add_property(
                    'document_id',
                    Variable(
                        name='document_id',
                        display_name='Document ID',
                        type='number',
                        value=document['id']
                    )
                )
                segment_var.add_property(
                    'source',
                    Variable(
                        name='source',
                        display_name='Source',
                        type='string',
                        value=document['name']
                    )
                )
                outputs.add_value(segment_var)
            embedding_tokens = retrieval_token_counter['embedding']
            reranking_tokens = retrieval_token_counter['reranking']
            return {
                'status': 'success',
                'message': 'Retriever node executed successfully.',
                'data': {
                    'elapsed_time': monotonic() - start_time,
                    'inputs': self.data['input'].to_dict(),
                    'output_type': 1,
                    'outputs': outputs.to_dict(),
                    'embedding_tokens': embedding_tokens,
                    'reranking_tokens': reranking_tokens
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }
        