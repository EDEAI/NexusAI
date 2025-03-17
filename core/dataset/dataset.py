import json
import re

from datetime import datetime
from pathlib import Path
from time import monotonic
from typing import Any, Dict, List, Optional, Tuple

import tiktoken

from langchain_core.documents import Document
from langchain_core.runnables import chain, Runnable
from langchain_core.runnables.utils import Input, Output

from config import enable_reranking_on_single_retrival, settings
from core.database.models import (
    Apps,
    DatasetProcessRules,
    Datasets,
    Documents,
    DocumentSegmentRagRecords,
    DocumentSegments,
    Models,
    ModelConfigurations,
    RagRecords,
    UploadFiles,
    Users
)
from core.document import DocumentLoader, TextSplitter
from core.embeddings import Embeddings
from core.reranker import Reranker
from core.retriever import Retriever
from core.vdb import VectorDatabase
from core.vdb.vector_database import DeleteDatasetStatus

from api.utils.common import *
from languages import get_language_content
from log import Logger


project_root = Path(__file__).absolute().parent.parent.parent
logger = Logger.get_logger('dataset')

apps = Apps()
datasets = Datasets()
documents = Documents()
document_segment_rag_records = DocumentSegmentRagRecords()
document_segments = DocumentSegments()
models = Models()
rag_records = RagRecords()
upload_files = UploadFiles()
users = Users()

all_embeddings = {}
all_rerankers = {}

def get_embeddings_and_vector_database(
    embeddings_config_id: int,
    collection_name: str,
) -> Tuple[Embeddings, VectorDatabase]:
    if embeddings_config_id in all_embeddings:
        embeddings = all_embeddings[embeddings_config_id]
    else:
        embeddings_config = {}
        embeddings_data = models.get_model_by_config_id(embeddings_config_id)
        for key, value in embeddings_data['supplier_config'].items():
            embeddings_config[key] = value
        for key, value in embeddings_data['model_config'].items():
            # Override supplier config with model config
            embeddings_config[key] = value
        embeddings_type, embeddings_config = convert_to_type_and_config(embeddings_config)
        match embeddings_type:
            case 'OpenAIEmbeddings':
                embeddings_kwargs = {
                    'openai_api_key': embeddings_config['api_key'],
                    'model': embeddings_config['model']
                }
            case 'Text2vecEmbeddings':
                embeddings_kwargs = {
                    'model_name_or_path': './models/text2vec'
                }
            case _:
                embeddings_kwargs = {}
        embeddings = Embeddings(embeddings_type, **embeddings_kwargs)
        if embeddings_data['model_mode'] == 2:
            # Cache local models
            all_embeddings[embeddings_config_id] = embeddings
    
    vdb_type, vdb_config = get_vdb_type_and_config()
    match vdb_type:
        case 'Milvus':
            vdb_kwargs = {
                'embedding_function': embeddings,
                'collection_name': collection_name,
                'connection_args': {
                    'uri': f'http://{vdb_config["host"]}:{vdb_config["port"]}',
                    'user': vdb_config['user'],
                    'password': vdb_config['password']
                },
                'index_params': {
                    'metric_type': 'IP',
                    'index_type': 'HNSW',
                    'params': {'M': 8, 'efConstruction': 64}
                },
                'auto_id': True,
                'primary_field': 'index_id'
            }
            if 'timeout' in vdb_config:
                vdb_kwargs['timeout'] = vdb_config['timeout']
        case _:
            vdb_kwargs = {}
    vdb = VectorDatabase(vdb_type, **vdb_kwargs)
    
    return embeddings, vdb

def get_retriever(retriever_config: Dict[str, Any]) -> Dict[str, Any]:
    _, retriever_config = convert_to_type_and_config(retriever_config)
    return {
        'k': retriever_config['k'],
        'score_threshold': retriever_config['score_threshold']
    }

def get_reranker(team_id: int) -> Reranker:
    if team_id in all_rerankers:
        reranker = all_rerankers[team_id]
    else:
        reranker_config = {}
        reranker_data = models.get_model_by_type(3, team_id)
        for key, value in reranker_data['supplier_config'].items():
            reranker_config[key] = value
        for key, value in reranker_data['model_config'].items():
            # Override supplier config with model config
            reranker_config[key] = value
        reranker_type, reranker_config = convert_to_type_and_config(reranker_config)
        reranker_kwargs = {}
        if reranker_type == 'CrossEncoderReranker':
            reranker_kwargs['model_type'] = reranker_config['model_type']
            reranker_kwargs['model_kwargs'] = {
                'model_name': './models/bge-reranker-v2-m3'
            }
            reranker_kwargs['top_n'] = settings.RETRIEVER_K
        reranker = Reranker(reranker_type, **reranker_kwargs)
        if reranker_data['model_mode'] == 2:
            # Cache local models
            all_rerankers[team_id] = reranker
    
    return reranker


class DatasetManagement:
    @classmethod
    def document_segmentation(
        cls,
        file_path: str,
        text_splitter_type: str,
        process_rule: Dict[str, Any]
    ) -> List[Document]:
        '''
        Return: list of document segments (langchain Documents)
        '''
        dl = DocumentLoader(file_path=file_path)
        ts = TextSplitter(text_splitter_type, **process_rule)
        return dl.load_and_split(text_splitter=ts)

    @classmethod
    def get_num_tokens(
        cls, team_id: int, segments: List[Document]
    ) -> Tuple[int, float, str]:
        embeddings = models.get_model_by_type(2, team_id, 1)
        embeddings_name = embeddings['model_name']
        embeddings_config = embeddings['model_config']
        supplier_name = embeddings['supplier_name']
        total_num_tokens = 0
        input_pricing = embeddings_config['input_pricing']
        currency = embeddings_config['pricing_currency']
        if supplier_name == 'OpenAI':
            try:
                enc = tiktoken.encoding_for_model(embeddings_name)
            except KeyError:
                enc = tiktoken.get_encoding("cl100k_base")
            for segment in segments:
                text = segment.page_content
                # calculate the number of tokens in the encoded text
                tokenized_text = enc.encode(text)
                total_num_tokens += len(tokenized_text)
        
        elif supplier_name == 'Baichuan':
            def count_chinese_characters(text: str) -> int:
                return len(re.findall(r'[\u4e00-\u9fa5]', text))
            
            def count_english_vocabularies(text: str) -> int:
                # remove all non-alphanumeric characters but keep spaces and other symbols like !, ., etc.
                text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
                # count the number of words not characters
                return len(text.split())
            
            for segment in segments:
                text = segment.page_content
                num_tokens = int(count_chinese_characters(text) + count_english_vocabularies(text) * 1.3)
                total_num_tokens += num_tokens
                
        else:
            from transformers import GPT2Tokenizer as TransformerGPT2Tokenizer
            base_path = Path(__file__).absolute()
            gpt2_tokenizer_path = base_path.parent.joinpath('gpt2')
            _tokenizer = TransformerGPT2Tokenizer.from_pretrained(gpt2_tokenizer_path)
            for segment in segments:
                text = segment.page_content
                tokens = _tokenizer.encode(text, verbose=False)
                total_num_tokens += len(tokens)

        return total_num_tokens, round(total_num_tokens * input_pricing, 7), currency

    @classmethod
    def create_dataset(cls, embeddings_config_id: int) -> str:
        '''
        Return: dataset_id
        '''
        collection_name = get_new_collection_name()
        get_embeddings_and_vector_database(embeddings_config_id, collection_name)
        return collection_name

    @classmethod
    def add_document_to_dataset(
        cls,
        document_id: int,
        dataset_id: int,
        process_rule_id: int,
        file_path: str = '',
        text: str = '',
        is_json: bool = False,
        source: str = ''
    ) -> Tuple[int, int, float]:
        '''
        `text`, `is_json` and `source` is only used when `file_path` is empty
        
        Return: Tuple of (total_word_count, total_num_tokens, indexing_latency)
        '''
        def get_text_splitter(is_json) -> TextSplitter:
            process_rule = DatasetProcessRules().get_process_rule_by_id(process_rule_id)
            # if is_json:
            #     type_ = 'RecursiveJsonSplitter'
            #     config = {'max_chunk_size': process_rule['config']['chunk_size']}
            # else:
            type_, config = convert_to_type_and_config(process_rule['config'])
            return TextSplitter(text_splitter_type=type_, **config)
        
        dataset = datasets.get_dataset_by_id(dataset_id, check_is_reindexing=True)
        collection_name = dataset['collection_name']
        embeddings_config_id = dataset['embedding_model_config_id']
        _, vdb = get_embeddings_and_vector_database(embeddings_config_id, collection_name)
        ts = get_text_splitter(is_json=is_json)
        if file_path:
            dl = DocumentLoader(file_path=file_path)
            segments = dl.load_and_split(text_splitter=ts)
        elif text:
            if is_json:
                try:
                    text_obj = json.loads(text)
                    segments = ts.create_documents(
                        [text_obj],
                        [{'source': source}],
                        ensure_ascii=False
                    )
                except:
                    ts = get_text_splitter(is_json=False)
                    segments = ts.create_documents([text], [{'source': source}])
            else:
                segments = ts.create_documents([text], [{'source': source}])
        else:
            raise ValueError('Either file_path or text must be provided!')
        total_word_count = 0
        total_num_tokens = 0
        overall_indexing_start_time = monotonic()
        for segment in segments:
            page_content = segment.page_content
            word_count = len(page_content)
            total_word_count += word_count
            indexing_time = datetime.now()
            segment_id = document_segments.insert(
                {
                    'document_id': document_id,
                    'content': page_content,
                    'word_count': word_count,
                    'indexing_status': 1,
                    'indexing_time': indexing_time
                }
            )
            try:
                index_id = vdb.add_documents([segment])[0]
            except:
                document_segments.update(
                    {'column': 'id', 'value': segment_id},
                    {'indexing_status': 3}
                )
                raise
            else:
                completed_time = datetime.now()
                num_tokens = vdb.embeddings.get_and_reset_num_tokens()
                total_num_tokens += num_tokens
                document_segments.update(
                    {'column': 'id', 'value': segment_id},
                    {
                        'index_id': index_id,
                        'tokens': num_tokens,
                        'indexing_status': 2,
                        'completed_time': completed_time
                    }
                )
                
        indexing_latency = monotonic() - overall_indexing_start_time
        return total_word_count, total_num_tokens, indexing_latency

    @classmethod
    def enable_document(cls, document_id: int) -> Optional[bool]:
        document = documents.get_document_by_id(document_id)
        dataset = datasets.get_dataset_by_id(document['dataset_id'], check_is_reindexing=True)
        _, vdb = get_embeddings_and_vector_database(
            dataset['embedding_model_config_id'],
            dataset['collection_name']
        )
        if document['upload_file_id']:
            file = upload_files.get_file_by_id(document['upload_file_id'])
            source_string = str(project_root.joinpath(file['path']))
        else:
            source_string = f'{document["name"]}-{document["node_exec_id"]}'
        segments = document_segments.select(
            columns=['id', 'index_id', 'content'],
            conditions=[
                {'column': 'document_id', 'value': document_id},
                {'column': 'status', 'value': 1}
            ]
        )
        for segment in segments:
            segment_id = segment['id']
            indexing_time = datetime.now()
            document_segments.update(
                {'column': 'id', 'value': segment_id},
                {
                    'indexing_status': 1,
                    'indexing_time': indexing_time
                }
            )
            
            try:
                index_id = vdb.add_texts(
                    [segment['content']],
                    [{'source': source_string}]
                )[0]
            except:
                document_segments.update(
                    {'column': 'id', 'value': segment_id},
                    {'indexing_status': 3}
                )
                raise
            else:
                completed_time = datetime.now()
                num_tokens = vdb.embeddings.get_and_reset_num_tokens()
                update_data = {
                    'index_id': index_id,
                    'indexing_status': 2,
                    'completed_time': completed_time
                }
                if num_tokens > 0:
                    update_data['tokens'] = num_tokens
                document_segments.update(
                    {'column': 'id', 'value': segment_id},
                    update_data
                )
                
        return True

    @classmethod
    def disable_document(cls, document_id: int) -> Optional[bool]:
        document = documents.get_document_by_id(document_id)
        dataset = datasets.get_dataset_by_id(document['dataset_id'], check_is_reindexing=True)
        segments = document_segments.select(
            columns=['id', 'index_id'],
            conditions=[
                {'column': 'document_id', 'value': document_id},
                {'column': 'status', 'value': 1}
            ]
        )
        _, vdb = get_embeddings_and_vector_database(
            dataset['embedding_model_config_id'],
            dataset['collection_name']
        )
        result = vdb.delete([segment['index_id'] for segment in segments])
        document_segments.update(
            {'column': 'document_id', 'value': document_id},
            {'indexing_status': 0}
        )
        return result

    @classmethod
    def delete_document(cls, document_id: int) -> Optional[bool]:
        document = documents.get_document_by_id(document_id)
        if document['status'] == 2:
            document_segments.soft_delete(
                {
                    'column': 'document_id',
                    'value': document_id
                }
            )
            return True
        dataset = datasets.get_dataset_by_id(document['dataset_id'], check_is_reindexing=True)
        segments = document_segments.select(
            columns=['index_id', 'content', 'status'],
            conditions=[
                {'column': 'document_id', 'value': document_id},
                {'column': 'status', 'op': '<', 'value': 3}
            ]
        )
        index_ids = [segment['index_id'] for segment in segments if segment['status'] == 1]
        _, vdb = get_embeddings_and_vector_database(
            dataset['embedding_model_config_id'],
            dataset['collection_name']
        )
        result = vdb.delete(index_ids)
        contents = [segment['content'] for segment in segments]
        if contents:
            vdb.embeddings.document_embedding_store.mdelete(contents)
        document_segments.soft_delete(
            {
                'column': 'document_id',
                'value': document_id
            }
        )
        return result

    @classmethod
    def enable_segment(
        cls,
        segment: Dict[str, Any],
        document: Dict[str, Any],
        dataset: Dict[str, Any]
    ) -> str:
        if document['status'] != 1:
            document_segments.update(
                {'column': 'id', 'value': segment['id']},
                {'status': 1}
            )
            return segment['index_id']
        _, vdb = get_embeddings_and_vector_database(
            dataset['embedding_model_config_id'],
            dataset['collection_name']
        )
        if document['upload_file_id']:
            file = upload_files.get_file_by_id(document['upload_file_id'])
            source_string = str(project_root.joinpath(file['path']))
        else:
            source_string = f'{document["name"]}-{document["node_exec_id"]}'
        segment_id = segment['id']
        indexing_time = datetime.now()
        document_segments.update(
            {'column': 'id', 'value': segment_id},
            {
                'indexing_status': 1,
                'indexing_time': indexing_time,
                'status': 1
            }
        )
        
        try:
            index_id = vdb.add_texts(
                [segment['content']],
                [{'source': source_string}]
            )[0]
        except:
            document_segments.update(
                {'column': 'id', 'value': segment_id},
                {'indexing_status': 3}
            )
            raise
        completed_time = datetime.now()
        num_tokens = vdb.embeddings.get_and_reset_num_tokens()
        update_data = {
            'index_id': index_id,
            'indexing_status': 2,
            'completed_time': completed_time
        }
        if num_tokens > 0:
            update_data['tokens'] = num_tokens
        document_segments.update(
            {'column': 'id', 'value': segment_id},
            update_data
        )
        
        return index_id

    @classmethod
    def disable_segment(
        cls,
        segment: Dict[str, Any],
        document: Dict[str, Any],
        dataset: Dict[str, Any]
    ) -> Optional[bool]:
        if document['status'] != 1:
            document_segments.update(
                {'column': 'id', 'value': segment['id']},
                {'status': 2}
            )
            return True
        _, vdb = get_embeddings_and_vector_database(
            dataset['embedding_model_config_id'],
            dataset['collection_name']
        )
        result = vdb.delete([segment['index_id']])
        document_segments.update(
            {'column': 'id', 'value': segment['id']},
            {
                'indexing_status': 0,
                'status': 2
            }
        )
        
        return result

    @classmethod
    def reindex_dataset(cls, dataset_id: int, new_embeddings_config_id: int) -> None:
        dataset = datasets.get_dataset_by_id(dataset_id, check_is_reindexing=True)
        
        # Initialize old and new vector databases
        collection_name = dataset['collection_name']
        embeddings_config_id = dataset['embedding_model_config_id']
        _, vdb = get_embeddings_and_vector_database(embeddings_config_id, collection_name)
        new_collection_name = get_new_collection_name()
        _, new_vdb = get_embeddings_and_vector_database(new_embeddings_config_id, new_collection_name)

        # Update dataset status to reindexing
        datasets.update(
            {'column': 'id', 'value': dataset_id},
            {
                'collection_name': 'reindexing',
                'embedding_model_config_id': new_embeddings_config_id
            }
        )

        # Get all enabled documents and segments and update their status to not indexed
        enabled_documents = documents.select(
            columns=['id', 'name', 'upload_file_id', 'node_exec_id'],
            conditions=[
                {'column': 'dataset_id', 'value': dataset_id},
                {'column': 'archived', 'value': 0},
                {'column': 'status', 'value': 1}
            ]
        )
        enabled_segments_by_document_id = {}
        for document in enabled_documents:
            segments = document_segments.select(
                columns=['id', 'index_id', 'content'],
                conditions=[
                    {'column': 'document_id', 'value': document['id']},
                    {'column': 'status', 'value': 1}
                ]
            )
            enabled_segments_by_document_id[document['id']] = segments
            document_segments.update(
                [
                    {'column': 'document_id', 'value': document['id']},
                    {'column': 'status', 'value': 1}
                ],
                {
                    'tokens': 0,
                    'indexing_status': 0
                }
            )
        
        # Delete dataset from vector database
        status = vdb.delete_dataset()
        if status == DeleteDatasetStatus.ERROR:
            raise Exception('Cannot delete dataset from vector database!')
        if status == DeleteDatasetStatus.NOT_SUPPORTED:
            vdb.delete(
                [
                    segment['index_id']
                    for segments in enabled_segments_by_document_id.values()
                    for segment in segments
                ]
            )
        
        # Clear embedding cache
        for document in documents.select(
            columns=['id'],
            conditions=[
                {'column': 'dataset_id', 'value': dataset_id},
                {'column': 'status', 'op': '<', 'value': 3}
            ],
        ):
            segments = document_segments.select(
                columns=['id', 'content', 'status'],
                conditions=[
                    {'column': 'document_id', 'value': document['id']},
                    {'column': 'status', 'op': '<', 'value': 3}
                ],
            )
            contents = [segment['content'] for segment in segments]
            if contents:
                vdb.embeddings.document_embedding_store.mdelete(contents)
        
        # Add documents to new dataset
        for document in enabled_documents:
            if document['upload_file_id']:
                file = upload_files.get_file_by_id(document['upload_file_id'])
                source_string = str(project_root.joinpath(file['path']))
            else:
                source_string = f'{document["name"]}-{document["node_exec_id"]}'
            segments = enabled_segments_by_document_id[document['id']]
            for segment in segments:
                segment_id = segment['id']
                indexing_time = datetime.now()
                document_segments.update(
                    {'column': 'id', 'value': segment_id},
                    {
                        'indexing_status': 1,
                        'indexing_time': indexing_time
                    }
                )
                
                try:
                    index_id = new_vdb.add_texts(
                        [segment['content']],
                        [{'source': source_string}]
                    )[0]
                except:
                    document_segments.update(
                        {'column': 'id', 'value': segment_id},
                        {'indexing_status': 3}
                    )
                    raise
                else:
                    completed_time = datetime.now()
                    num_tokens = new_vdb.embeddings.get_and_reset_num_tokens()
                    document_segments.update(
                        {'column': 'id', 'value': segment_id},
                        {
                            'index_id': index_id,
                            'tokens': num_tokens,
                            'indexing_status': 2,
                            'completed_time': completed_time
                        }
                    )
        
        datasets.update(
            {'column': 'id', 'value': dataset_id},
            {'collection_name': new_collection_name}
        )

    @classmethod
    def delete_dataset(cls, dataset_id: int):
        # Delete dataset from vector database
        dataset = datasets.get_dataset_by_id(dataset_id, check_is_reindexing=True)
        collection_name = dataset['collection_name']
        embeddings_config_id = dataset['embedding_model_config_id']
        _, vdb = get_embeddings_and_vector_database(embeddings_config_id, collection_name)
        status = vdb.delete_dataset()
        if status == DeleteDatasetStatus.ERROR:
            raise Exception('Cannot delete dataset from vector database!')
        if status == DeleteDatasetStatus.NOT_SUPPORTED:
            vdb.delete(
                [
                    segment['index_id']
                    for segment in document_segments.select(
                        columns=['index_id'],
                        conditions=[
                            {'column': 'documents.dataset_id', 'value': dataset_id},
                            {'column': 'documents.archived', 'value': 0},
                            {'column': 'documents.status', 'value': 1},
                            {'column': 'document_segments.status', 'value': 1}
                        ],
                        joins=[
                            ['inner', 'documents', 'document_segments.document_id = documents.id']
                        ]
                    )
                ]
            )
        # Clear embedding cache
        for document in documents.select(
            columns=['id'],
            conditions=[
                {'column': 'dataset_id', 'value': dataset_id},
                {'column': 'status', 'op': '<', 'value': 3}
            ],
        ):
            segments = document_segments.select(
                columns=['id', 'content'],
                conditions=[
                    {'column': 'document_id', 'value': document['id']},
                    {'column': 'status', 'op': '<', 'value': 3}
                ],
            )
            contents = [segment['content'] for segment in segments]
            if contents:
                vdb.embeddings.document_embedding_store.mdelete(contents)
            document_segments.soft_delete(
                [
                    {'column': 'document_id', 'value': document['id']},
                    {'column': 'status', 'op': '<', 'value': 3}
                ]
            )


class DatasetRetrieval:
    @classmethod
    def single_retrieve(
        cls,
        dataset_id: int,
        agent_id: int,
        agent_run_id: int,
        workflow_id: int,
        workflow_run_id: int,
        user_id: int,
        run_type: int,
        search_in_documents: Optional[List[str]] = None
    ) -> Tuple[Runnable[Input, Output], List[Document], Dict[str, int]]:
        token_counter = {
            'embedding': 0,
            'reranking': 0
        }
        retrieval_result: List[Document] = []
        
        @chain
        def retrieval_chain(query: str) -> List[Document]:
            logger.info(f'Retrieving dataset {dataset_id} with query: {query}')
            logger.info(f'Search in documents: {search_in_documents}')
            rag_record_id = rag_records.insert(
                {
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'agent_run_id': agent_run_id,
                    'workflow_id': workflow_id,
                    'workflow_run_id': workflow_run_id,
                    'dataset_ids': [dataset_id],
                    'type': run_type,
                    'input': query,
                    'search_in_documents': search_in_documents,
                    'status': 1
                }
            )
            try:
                start_time = monotonic()
                user = users.get_user_by_id(user_id)
                assert user, 'User not found!'
                team_id = user['team_id']
                dataset = datasets.get_dataset_by_id(dataset_id, check_is_reindexing=True)
                app = apps.get_app_by_id(dataset['app_id'])
                apps.increment_execution_times(app['id'])
                collection_name = dataset['collection_name']
                embeddings_config_id = dataset['embedding_model_config_id']
                _, vdb = get_embeddings_and_vector_database(embeddings_config_id, collection_name)
                retriever_config = get_retriever(dataset['retriever_config'])
                logger.info(f'Retrieving documents from dataset {dataset_id}...')
                docs_and_similarities = vdb.similarity_search_with_relevance_scores(
                    query,
                    search_in_documents=search_in_documents,
                    **retriever_config
                )
                logger.info(f'Retrieved {len(docs_and_similarities)} documents.')
                result = []
                for doc, score in docs_and_similarities:
                    logger.debug(f'ID and score: {doc.metadata["index_id"]}, {score}')
                    doc.metadata['score'] = score
                    result.append(doc)
                token_counter['embedding'] += vdb.embeddings.get_and_reset_num_tokens()
                if result:
                    if enable_reranking_on_single_retrival:
                        reranker = get_reranker(team_id)
                        logger.info('Reranking documents...')
                        result = list(reranker.compress_documents(result, query))
                        token_counter['reranking'] += reranker.get_and_reset_num_tokens()
                        for doc in result:
                            logger.debug(f'ID and score: {doc.metadata["index_id"]}, {doc.metadata["relevance_score"]}')
                    result.sort(
                        key=lambda doc: (
                            -doc.metadata.get('relevance_score', 0.0),
                            -doc.metadata.get('score', 0.0)
                        )
                    )
                    retrieval_result.extend(result)
                    for document_segment in result:
                        index_id = str(document_segment.metadata['index_id'])
                        segment = document_segments.get_segment_by_index_id(index_id)
                        document = documents.get_document_by_id(segment['document_id'])
                        document_segments.increment_hit_count(segment['id'])
                        document_segment_rag_records.insert(
                            {
                                'rag_record_id': rag_record_id,
                                'dataset_id': dataset_id,
                                'document_id': document['id'],
                                'segment_id': segment['id'],
                                'score': document_segment.metadata.get('score', 0.0),
                                'reranking_score': document_segment.metadata.get('relevance_score', 0.0)
                            }
                        )
                rag_records.update(
                    {'column': 'id', 'value': rag_record_id},
                    {
                        'status': 2,
                        'elapsed_time': monotonic() - start_time,
                        'embedding_tokens': token_counter['embedding'],
                        'reranking_tokens': token_counter['reranking']
                    }
                )
                return result
            except Exception as e:
                rag_records.update(
                    {'column': 'id', 'value': rag_record_id},
                    {
                        'status': 3,
                        'error': str(e),
                        'elapsed_time': monotonic() - start_time,
                        'embedding_tokens': token_counter['embedding'],
                        'reranking_tokens': token_counter['reranking']
                    }
                )
                raise

        return retrieval_chain, retrieval_result, token_counter

    @classmethod
    def multiple_retrieve(
        cls,
        dataset_ids: List[int],
        agent_id: int,
        agent_run_id: int,
        workflow_id: int,
        workflow_run_id: int,
        user_id: int,
        run_type: int,
        search_in_documents: Optional[List[str]] = None
    ) -> Tuple[Runnable[Input, Output], Dict[int, List[Document]], Dict[str, int]]:
        token_counter = {
            'embedding': 0,
            'reranking': 0
        }
        retrieval_result: Dict[int, List[Document]] = {}

        @chain
        def retrieval_chain(query: str) -> List[Document]:
            logger.info(f'Retrieving datasets {dataset_ids} with query: {query}')
            logger.info(f'Search in documents: {search_in_documents}')
            rag_record_id = rag_records.insert(
                {
                    'user_id': user_id,
                    'agent_id': agent_id,
                    'agent_run_id': agent_run_id,
                    'workflow_id': workflow_id,
                    'workflow_run_id': workflow_run_id,
                    'dataset_ids': dataset_ids,
                    'type': run_type,
                    'input': query,
                    'search_in_documents': search_in_documents,
                    'status': 1
                }
            )
            try:
                start_time = monotonic()
                user = users.get_user_by_id(user_id)
                assert user, 'User not found!'
                team_id = user['team_id']
                for dataset_id in dataset_ids:
                    dataset = datasets.get_dataset_by_id(dataset_id)
                    app = apps.get_app_by_id(dataset['app_id'])
                    apps.increment_execution_times(app['id'])
                overall_result = []
                for dataset_id in dataset_ids:
                    dataset = datasets.get_dataset_by_id(dataset_id, check_is_reindexing=True)
                    collection_name = dataset['collection_name']
                    embeddings_config_id = dataset['embedding_model_config_id']
                    _, vdb = get_embeddings_and_vector_database(embeddings_config_id, collection_name)
                    retriever_config = get_retriever(dataset['retriever_config'])
                    logger.info(f'Retrieving documents from dataset {dataset_id}...')
                    docs_and_similarities = vdb.similarity_search_with_relevance_scores(
                        query,
                        search_in_documents=search_in_documents,
                        **retriever_config
                    )
                    for doc, score in docs_and_similarities:
                        logger.debug(f'ID and score: {doc.metadata["index_id"]}, {score}')
                        doc.metadata['score'] = score
                        overall_result.append(doc)
                    token_counter['embedding'] += vdb.embeddings.get_and_reset_num_tokens()
                if overall_result:
                    reranker = get_reranker(team_id)
                    logger.info('Reranking documents...')
                    overall_result = list(reranker.compress_documents(overall_result, query))
                    token_counter['reranking'] += reranker.get_and_reset_num_tokens()
                    for doc in overall_result:
                        logger.debug(f'ID and score: {doc.metadata["index_id"]}, {doc.metadata["relevance_score"]}')
                    overall_result.sort(
                        key=lambda doc: (
                            -doc.metadata.get('relevance_score', 0.0),
                            -doc.metadata.get('score', 0.0)
                        )
                    )
                    for document_segment in overall_result:
                        index_id = str(document_segment.metadata['index_id'])
                        segment = document_segments.get_segment_by_index_id(index_id)
                        document = documents.get_document_by_id(segment['document_id'])
                        dataset = datasets.get_dataset_by_id(document['dataset_id'])
                        retrieval_result.setdefault(document['dataset_id'], []).append(document_segment)
                        document_segments.increment_hit_count(segment['id'])
                        document_segment_rag_records.insert(
                            {
                                'rag_record_id': rag_record_id,
                                'dataset_id': dataset_id,
                                'document_id': document['id'],
                                'segment_id': segment['id'],
                                'score': document_segment.metadata.get('score', 0.0),
                                'reranking_score': document_segment.metadata.get('relevance_score', 0.0)
                            }
                        )
                rag_records.update(
                    {'column': 'id', 'value': rag_record_id},
                    {
                        'status': 2,
                        'elapsed_time': monotonic() - start_time,
                        'embedding_tokens': token_counter['embedding'],
                        'reranking_tokens': token_counter['reranking']
                    }
                )
                return overall_result
            except Exception as e:
                rag_records.update(
                    {'column': 'id', 'value': rag_record_id},
                    {
                        'status': 3,
                        'error': str(e),
                        'elapsed_time': monotonic() - start_time,
                        'embedding_tokens': token_counter['embedding'],
                        'reranking_tokens': token_counter['reranking']
                    }
                )
                raise

        return retrieval_chain, retrieval_result, token_counter

    @classmethod
    def get_full_documents(cls, retrieval_result: List[Document]) -> List[Dict[str, str]]:
        full_documents = []
        document_ids = set()
        for document in retrieval_result:
            index_id = str(document.metadata['index_id'])
            segment = document_segments.get_segment_by_index_id(index_id)
            document = documents.get_document_by_id(segment['document_id'])
            document_id = document['id']    
            if document_id not in document_ids:  
                document_ids.add(document_id)
                all_segments = document_segments.get_segments_by_document_id(document_id)
                full_documents.append(
                {
                    'name': document['name'],
                    'content': '\n'.join(segment['content'] for segment in all_segments)
                }
            )
        return full_documents
