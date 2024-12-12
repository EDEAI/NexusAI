import json
import os.path
from datetime import date
from mimetypes import guess_type
from typing import Any, Dict, Literal
from uuid import uuid4
from celery_app import run_dataset, reindex_dataset
from sqlalchemy.sql import roles

from log import Logger

from fastapi import APIRouter, UploadFile, File, Query
from languages import get_language_content
from core.database.models import (
    Apps,
    DatasetProcessRules,
    Datasets,
    Documents,
    ModelConfigurations,
    UploadFiles,
    DocumentSegments, AppRuns, Models, AgentDatasetRelation, DocumentSegmentRagRecords, RagRecords
)
from api.utils.auth import aes_decrypt_with_token
from api.utils.common import *
from api.utils.jwt import *
from api.schema.vector import *
from config import *
from core.dataset import DatasetManagement
logger = Logger.get_logger('vector')
router = APIRouter()

@router.get('/get_cost', response_model=CostResponse)
async def get_cost(
        file_ids: List[int] = Query(),
        indexing_mode: int = Query(),
        process_rule_id: int = Query(),
        userinfo: TokenData = Depends(get_current_user)) -> CostResponse:

    """
    dataset acquisition cost

    Args:
        file_ids: List[int], id of the file to be uploaded, file_ids is required.
        indexing_mode: int, Embedded mode 1: Paid, 2 free, indexing_mode is required.
        process_rule_id: int, Data set flow rule id, process_rule_id is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        Total number of tokens : num_tokens
        Total cost: cost
        Currency type: currency
    """
    team_id = userinfo.team_id
    user_id = userinfo.uid
    total_num_tokens = 0
    total_cost = 0.0
    currency = 'USD'
    team_id_list = UploadFiles().get_by_team_id(file_ids)
    if team_id_list:
        for item in team_id_list:
            if team_id != item['team_id']:
                logger.info('get_cost: Insufficient permissions, desc: files_id %s is not currently on your team, Current user id %s', item['id'], user_id)
                return response_error(get_language_content("api_vector_auth"))
    else:
        file_ids_str = ', '.join(map(str, file_ids))
        logger.info('get_cost: The uploaded file information is not matched, desc: The current files id %s do not exist, Current user id %s', file_ids_str, user_id)
        return response_error(get_language_content("api_vector_file_type"))

    if indexing_mode == 1:
        process_rule = DatasetProcessRules().get_process_rule_by_id(process_rule_id)
        if process_rule:
            type_, config = convert_to_type_and_config(process_rule['config'])
            for file_id in file_ids:
                file = UploadFiles().get_file_by_id(file_id)
                if file:
                    try:
                        segments = DatasetManagement.document_segmentation(
                            str(project_root.joinpath(file['path'])),
                            type_,
                            config
                        )
                        num_tokens, cost, currency = DatasetManagement.get_num_tokens(team_id, segments)
                    except AssertionError as e:
                        return response_error(str(e))
                    total_num_tokens += num_tokens
                    total_cost += cost
    return response_success({'num_tokens': total_num_tokens, 'cost': total_cost, 'currency': currency},get_language_content("api_vector_success"))


@router.get('/dataset_list/{is_individual}', response_model=DatasetListResponse)
async def dataset_list(is_individual: int, userinfo: TokenData = Depends(get_current_user)) -> DatasetListResponse:
    """
    Get a list of all datasets

    Args:
        userinfo: TokenData, the user information obtained from the token

    Returns:
        data: Dict, indicates data information.
            dataset_id: int, indicates dataset id.
            app_id: int, indicates app id.
            name: str, indicates dataset name.
            is_individual: int, 1 personage 2 Team visible and individual

    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    datasets_list = Datasets().get_dataset_list(team_id, user_id, is_individual)
    datasets_list = [{'dataset_id': item[0], 'app_id': item[1], 'name': item[2]} for item in datasets_list]
    response = {'data': datasets_list}
    return response_success(response,get_language_content("api_vector_success"))


@router.post('/create_dataset', response_model=CreateDatasetResponse)
async def create_dataset(data: CreateDatasetSchema,userinfo: TokenData = Depends(get_current_user)) -> CreateDatasetResponse:
    """
    Create a new dataset with the provided files.

    Args:
        data (CreateDatasetSchema): The schema for creating a new dataset.
        userinfo (TokenData): The user information obtained from the token.

    Returns:
        The ID of the newly created dataset.
    """

    user_id = userinfo.uid
    team_id = userinfo.team_id
    name = data.name
    description = data.description
    enable_api = data.enable_api
    is_public = data.is_public
    process_rule_id = data.process_rule_id
    data_source_type = data.data_source_type
    indexing_mode: Literal[1, 2] = data.indexing_mode
    try:
        embeddings_config_id = Models().get_model_by_type(2, team_id, indexing_mode, user_id)['model_config_id']
    except AssertionError as e:
        msg = str(e)
        logger.info('create_dataset: %s desc: Request model %s, Current user id %s', msg, user_id)
        return response_error(msg)
    collection_name = DatasetManagement.create_dataset(embeddings_config_id)
    retriever_config_dict = {item['key']: item['value'] for item in retriever_config}
    app_id = Apps().insert(
        {
            'team_id': team_id,
            'user_id': user_id,
            'name': name,
            'description': description,
            'mode': 3,
            'enable_api': enable_api,
            'is_public': is_public,
        }
    )
    dataset_id = Datasets().insert(
        {
            'team_id': team_id,
            'user_id': user_id,
            'app_id': app_id,
            'process_rule_id': process_rule_id,
            'data_source_type': data_source_type,
            'collection_name': collection_name,
            'embedding_model_config_id': embeddings_config_id,
            'retriever_config': retriever_config_dict
        }
    )
    return response_success({'dataset_id': dataset_id}, get_language_content("api_vector_success"))

@router.post('/add_document', response_model=AddDocumentResponse)
async def add_document(data: AddDocumentSchema, userinfo: TokenData = Depends(get_current_user)) -> AddDocumentResponse:
    """
    Add dataset documents in batches

    Args:
        app_id: int, app id, app_id is required.
        process_rule_id: int, Dataset process rule ID, process_rule_id is required.
        data_source_type: int, Data source type 1: Upload files 2: Synchronize other sites, data_source_type is required.
        file_ids: List[int], the id of the uploaded file, file_ids is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        success
    """
    app_id = data.app_id
    process_rule_id = data.process_rule_id
    data_source_type = data.data_source_type
    file_ids = data.file_ids
    user_id = userinfo.uid
    try:
        dataset_id = Datasets().get_dataset_id(
            app_id, user_id, 'api_vector_auth',
            check_is_reindexing=True
        )
    except AssertionError as e:
        msg = str(e)
        logger.info('add_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)
    for file_id in file_ids:
        file = UploadFiles().get_file_by_id(file_id)
        document_id = Documents().insert(
            {
                'user_id': user_id,
                'dataset_id': dataset_id,
                'name': file['name'] + file['extension'],
                'data_source_type': data_source_type,
                'dataset_process_rule_id': process_rule_id,
                'upload_file_id': file_id,
                'word_count': 0,
                'tokens': 0
            }
        )
        result = DatasetManagement.add_document_to_dataset(
            document_id=document_id,
            dataset_id=dataset_id,
            process_rule_id=process_rule_id,
            file_path=str(project_root.joinpath(file['path']))
        )
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
    return response_success({}, get_language_content("api_vector_success"))

@router.put('/enable_segment/{segment_id}', response_model=EnableSegmentResponse)
async def enable_segment(segment_id: int, userinfo: TokenData = Depends(get_current_user)) -> EnableSegmentResponse:
    """
    Turn on data set document segment

    Args:
        segment_id: int, Document segment id, segment_id is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        success
    """
    user_id = userinfo.uid
    try:
        segment = DocumentSegments().get_segment_by_id(segment_id)
        document = Documents().get_document_by_id(segment['document_id'], user_id, 'api_vector_auth')
        if document['archived'] == 1:
            return response_error("The current document has been archived and cannot be operated")
        dataset = Datasets().get_dataset_by_id(document['dataset_id'], check_is_reindexing=True)
        document_segments_indexing_status = DocumentSegments().get_segment_indexing_status(segment_id)
        if document_segments_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))
        DatasetManagement.enable_segment(segment, document, dataset)
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('enable_segment: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.put('/disable_segment/{segment_id}', response_model=DisableSegmentResponse)
async def disable_segment(segment_id: int, userinfo: TokenData = Depends(get_current_user)) -> DisableSegmentResponse:
    """
    Close the dataset document segment

    Args:
        segment_id: int, Document segment id, segment_id is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        success
    """
    user_id = userinfo.uid
    try:
        segment = DocumentSegments().get_segment_by_id(segment_id)
        document = Documents().get_document_by_id(segment['document_id'], user_id, 'api_vector_auth')
        dataset = Datasets().get_dataset_by_id(document['dataset_id'], check_is_reindexing=True)
        if document['archived'] == 1:
            return response_error("The current document has been archived and cannot be operated")

        document_segments_indexing_status = DocumentSegments().get_segment_indexing_status(segment_id)
        if document_segments_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))

        DatasetManagement.disable_segment(segment, document, dataset)
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('disable_segment: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.delete('/delete_document/{document_id}', response_model=DeleteDocumentResponse)
async def delete_document(document_id: int, userinfo: TokenData = Depends(get_current_user)) -> DeleteDocumentResponse:
    """
    Delete the dataset document

    Args:
        document_id: int, Document id, document_id is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        success
    """
    user_id = userinfo.uid
    try:
        Documents().get_document_find(document_id, user_id)
        document_indexing_status = Documents().get_document_indexing_status(document_id)
        if document_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))

        DatasetManagement.delete_document(document_id)
        Documents().soft_delete({'column': 'id', 'value': document_id})
        path = Documents().get_file_path_by_id(document_id)
        if path:
            file_path = project_root.joinpath(path)
            if file_path.exists():
                file_path.unlink()
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('delete_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.delete('/delete_dataset/{app_id}', response_model=DeleteDatasetResponse)
async def delete_dataset(app_id: int, userinfo: TokenData = Depends(get_current_user)) -> DeleteDatasetResponse:
    """
    Delete dataset

    Args:
        app_id: int, app id, app_id is required.
        userinfo: TokenData, the user information obtained from the token

    Returns:
         success
    """
    user_id = userinfo.uid
    try:
        dataset_id = Datasets().get_dataset_id(app_id, user_id, 'api_vector_auth', check_is_reindexing=True)
        indexing_status_dataset_data = Datasets().get_dataset_is_indexing_status(dataset_id)
        if indexing_status_dataset_data:
            return response_error(get_language_content("api_vector_indexing"))
        DatasetManagement.delete_dataset(dataset_id)
        Documents().soft_delete({'column': 'dataset_id', 'value': dataset_id})
        Datasets().soft_delete({'column': 'id', 'value': dataset_id})
        Apps().soft_delete({'column': 'id', 'value': app_id})
        AgentDatasetRelation().delete({'column': 'dataset_id', 'value': dataset_id})
        file_path_list = Documents().get_document_file_path_list(dataset_id)
        for path in file_path_list:
            if path and path.get('path'):
                file_path = project_root.joinpath(path['path'])
                if file_path.is_file():
                    file_path.unlink()
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('delete_dataset: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.get('/documents_list/{app_id}', response_model=DocumentsListResponse)
async def documents_list(
        app_id: int,
        page: int = Query(default=1),
        page_size: int = Query(default=10),
        name: str = Query(default=''),
        sort: str = Query(default='desc'),
        userinfo: TokenData = Depends(get_current_user)) -> DocumentsListResponse:
    """
    Get a list of all documents in the dataset

    Args:
        app_id: int, app id, app_id is required.
        page: int, page number, page is optional, default is 1.
        page_size: int, page size, page_size is optional, default is 10.
        name: str, document name, name is optional, default is ''.
        sort: str, sorting method, sort is optional, default is 'desc'.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        data: Dict, indicates data information.
            id: int, indicates document id.
            name: str, File name.
            extension: str, File suffix.
            size: int, File size.
            word_count: int, Document word count.
            created_time:str, Document creation time.
            status: int, Document status 1: Normal 2: Disabled 3: Deleted.
            sum_document_segments.hit_count:str, Document recall times.
        paging_information: Dict, Paging information
            total_pages: int, Total pages.
            total_count: int, Total number.
            page: int, Current page.
            page_size: int, Number of items per page.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        dataset_id = Datasets().get_dataset_id(app_id)
        is_where = f" AND documents.dataset_id = {dataset_id} AND documents.status < 3"
        conditions = [
            {'column': 'documents.dataset_id', 'value': dataset_id},
            {'column': 'documents.status', 'op': '<', 'value': 3},
        ]
        is_public = Datasets().get_dataset_is_public(dataset_id, team_id)
        if is_public == 0:
            Datasets().get_dataset_find(dataset_id, user_id, team_id)
            conditions.append({'column': 'documents.user_id', 'value': user_id}),
            is_where += f" AND documents.user_id = {user_id}"
    except AssertionError as e:
        msg = str(e)
        logger.info('documents_list: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

    dataset_detail = Datasets().get_dataset_detail(dataset_id)
    if name and name.strip():
        conditions.append({'column': 'documents.name', 'op': 'like', 'value': '%' + name + '%'})
        is_where += f" AND documents.name LIKE '%{name}%'"
    total_count = Documents().documents_list_count(is_where)
    paging_information = paging_result(page, page_size, total_count)
    paging_information['file_time'] = f'documents.created_time {sort}'
    result = Documents().documents_list(paging_information, conditions)
    for item in result['data']:
        item['created_time'] = str(item['created_time'])
        if item['sum_document_segments.hit_count'] is None:
            item['hit_count'] = "0"
        else:
            item['hit_count'] = item['sum_document_segments.hit_count']
        del item['sum_document_segments.hit_count']

    response = {
        'data': result['data'],
        'dataset_detail':dataset_detail,
        'paging_information': {
            "total_pages": result['total_pages'],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        }
    }
    return response_success(response, get_language_content("api_vector_success"))

@router.get('/document_segments_list/{document_id}', response_model=DocumentSegmentsListResponse)
async def document_segments_list(
        document_id: int,
        page: int = Query(default=1),
        page_size: int = Query(default=10),
        hit_count: str = Query(default='hit_count desc'),
        content: str = Query(default=''),
        status: int = Query(default=0),
        userinfo: TokenData = Depends(get_current_user)) -> DocumentSegmentsListResponse:
    """
    Get a list of all document segments in the document

    Args:
        document_id: int, Document id, document_id is required.
        page: int, page number, page is optional, default is 1.
        page_size: int, page size, page_size is optional, default is 10.
        hit_count: str, sort by hit count, hit_count is optional, default is 'hit_count desc'.
        content: str, search content, content is optional, default is ''.
        status: int, search status, status is optional, default is 0.
        userinfo: TokenData, the user information obtained from the token

    Returns:
        DocumentSegmentsListResponse:
        data: List[Dict], indicates data information.
            id: int, indicates document segment id.
            content: str, indicates document segment content.
            word_count:int, indicates document segment word count.
            hit_count: int, indicates document segment recall times.
            created_time: str, indicates document segment creation time.
            status: int, indicates document segment status 1: Normal 2: Disabled 3: Deleted.
            segnum: int, indicates document segment number.
        seg_set: Dict, indicates document segment set information.
            seg_Avg: str, indicates document segment average recall times.
            seg_Num: int,  Total number of document segments.
            hit_Num: str,  Total number of document segment recall times.
            Embedding_Time: str, Total time spent embedding.
            Embedding_Token: int, The embed costs the total number of tokens.
            seg_Len: int, The maximum length of each section of a document segment.
        paging_information: Dict, Paging information
            total_pages: int, Total pages.
            total_count: int, Total number.
            page: int, Current page.
            page_size: int, Number of items per page.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    conditions = [
        {'column': 'documents.id', 'value': document_id},
        {'column': 'documents.status', 'op': '!=', 'value': 3},
        {'column': 'document_segments.status', 'op': '!=', 'value': 3},
    ]
    try:
        is_public = Documents().get_document_by_is_public(document_id, team_id)
        if is_public == 0:
            Documents().get_document_find(document_id, user_id)
            conditions.append({'column': 'documents.user_id', 'value': user_id})
    except AssertionError as e:
        msg = str(e)
        logger.info('document_segments_list: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

    if not hit_count:
        hit_count = 'id'

    if content and content.strip():
        conditions.append({'column': 'document_segments.content', 'op': 'like', 'value': '%' + content + '%'})

    if status == 1 or status == 2:
        conditions.append({'column': 'document_segments.status',  'value': status})

    total_count = Documents().document_segments_count(conditions)
    segmented_information = DocumentSegments().document_segments_file_set(document_id)
    file_information = Documents().documents_dataset_process_rules(document_id)
    seg_set = {
        'seg_Avg': segmented_information.get("avg_word_count", ""),
        'seg_Num': segmented_information.get("count_id", ""),
        'hit_Num': segmented_information.get("sum_hit_count", ""),
        'Embedding_Time': file_information.get("indexing_latency", ''),
        'Embedding_Token': file_information.get("tokens", ''),
        'seg_Len': file_information.get('config', {}).get("chunk_size", ""),
    }
    paging_information = paging_result(page, page_size, total_count)
    paging_information['hit_count'] = hit_count
    result = Documents().document_segments_list(paging_information, conditions)
    if result['data']:
        result['data'] = [{**d, 'segnum': i} for i, d in enumerate(result['data'], start=1)]
    response = {
        'data': result['data'],
        'seg_set': seg_set,
        'paging_information': {
            "total_pages": result['total_pages'],
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        }
    }
    return response_success(response, get_language_content("api_vector_success"))

@router.put('/disable_document/{documents_id}', response_model=DisableDocumentResponse)
async def disable_document(documents_id: int, userinfo: TokenData = Depends(get_current_user)) -> DisableDocumentResponse:
    """
    Disable document.

    Args:
        documents_id: int, indicates document id, documents_id is required.
        userinfo: TokenData, indicates user information.

    Returns:
        success.
    """
    user_id = userinfo.uid
    try:
        Documents().get_document_find(documents_id, user_id)
        document_indexing_status = Documents().get_document_indexing_status(documents_id)
        if document_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))

        documents_data = Documents().get_document_by_id(documents_id, user_id, 'api_vector_auth')
        if documents_data['archived'] == 1:
            return response_error("The current document has been archived and cannot be operated")

        Documents().update(
            [
                {'column': 'id', 'value': documents_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ],
            {'status': 2}
        )
        DatasetManagement.disable_document(documents_id)
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('disable_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)


@router.put('/enable_document/{documents_id}', response_model=EnableDocumentResponse)
async def enable_document(documents_id: int, userinfo: TokenData = Depends(get_current_user)) -> EnableDocumentResponse:
    """
        Enable document.

        Args:
            documents_id: int, indicates document id, documents_id is required.
            userinfo: TokenData, indicates user information.

        Returns:
            success.
        """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        Documents().get_document_find(documents_id, user_id)
        document_indexing_status = Documents().get_document_indexing_status(documents_id)
        if document_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))
        documents_data = Documents().get_document_by_id(documents_id, user_id, 'api_vector_auth')
        if documents_data['archived'] == 1:
            return response_error("The current document has been archived and cannot be operated")

        Documents().update(
            [
                {'column': 'id', 'value': documents_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ],
            {'status': 1}
        )
        DatasetManagement.enable_document(documents_id)
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('enable_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.put('/archive_document/{document_id}', response_model=ArchivedDocumentResponse)
async def archive_document(document_id: int, userinfo: TokenData = Depends(get_current_user)) -> ArchivedDocumentResponse:
    """
    File away

    Args:
        document_id: int, indicates document id, document_id is required.
        userinfo: TokenData, indicates user information.

    Returns:
        success.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id

    try:
        Documents().get_document_find(document_id, user_id)
        document_indexing_status = Documents().get_document_indexing_status(document_id)
        if document_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))

        documents_data = Documents().get_document_by_id(document_id, user_id, 'api_vector_auth')

        if documents_data['status'] == 1:
            DatasetManagement.disable_document(document_id)

        Documents().update(
            [
                {'column': 'id', 'value': document_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ],
            {'archived': 1}
        )
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('archive_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)


@router.put('/cancel_archive_document/{document_id}', response_model=CancelArchivedDocumentResponse)
async def cancel_archive_document(document_id: int, userinfo: TokenData = Depends(get_current_user)) -> CancelArchivedDocumentResponse:
    """
    Cancel archive

    Args:
        document_id: int, indicates document id, document_id is required.
        userinfo: TokenData, indicates user information.

    Returns:
        success.
    """

    user_id = userinfo.uid
    team_id = userinfo.team_id
    role = userinfo.role
    try:
        Documents().get_document_find(document_id, user_id)
        document_indexing_status = Documents().get_document_indexing_status(document_id)
        if document_indexing_status:
            return response_error(get_language_content("api_vector_indexing"))
        documents_data = Documents().get_document_by_id(document_id, user_id, 'api_vector_auth')

        if documents_data['status'] == 1:
            DatasetManagement.enable_document(document_id)

        Documents().update(
            [
                {'column': 'id', 'value': document_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ],
            {'archived': 0}
        )
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('cancel_archive_document: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.put('/dataset_set/{app_id}', response_model=DatasetSetResponse)
async def dataset_set(
        app_id: int,
        data: DatasetSetSchema,
        userinfo: TokenData = Depends(get_current_user)
) -> DatasetSetResponse:
    """
    Data set Settings

    Args:
        app_id: int, indicates app id, app_id is required.
        name: str, indicates dataset name, name is required.
        description: str, indicates dataset description, description is required.
        public: int, Is it open to team members? 0: No 1: Yes.
        userinfo: TokenData, indicates user information.

    Returns:
        success
    """
    name = data.name
    description = data.description
    public = data.public
    mode = data.mode
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        dataset_id = Datasets().get_dataset_id(app_id, user_id, 'api_vector_auth', check_is_reindexing=True)
    except AssertionError as e:
        msg = str(e)
        logger.info('dataset_set: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)
    if (mode != 1 and mode != 2):
        return response_error(get_language_content("api_vector_available_model"))
    try:
        datasets_data = Datasets().get_dataset_by_id(dataset_id)
        conditions = [
            {'column': 'id', 'value': datasets_data['app_id']},
        ]
        Datasets().get_dataset_find(dataset_id, user_id, team_id)
        conditions.append({'column': 'user_id', 'value': user_id})
        indexing_status_dataset_data = Datasets().get_dataset_is_indexing_status(dataset_id)
        if indexing_status_dataset_data:
            return response_error(get_language_content("api_vector_indexing"))
        Apps().update(
            conditions,
            {'name': name, 'description': description, 'is_public': public}
        )

        try:
            embeddings_config_id = Models().get_model_by_type(2, team_id, mode, user_id)['model_config_id']
        except AssertionError as e:
            msg = str(e)
            logger.info('dataset_set: %s desc: Request model %s, Current user id %s', msg, user_id)
            return response_error(msg)

        if datasets_data['embedding_model_config_id'] != embeddings_config_id:
            Datasets().update(
                [
                    {'column': 'id', 'value': dataset_id},
                ],
                {'embedding_model_config_id': embeddings_config_id}
            )
            reindex_dataset.delay(dataset_id, embeddings_config_id)
        return response_success({}, get_language_content("api_vector_success"))
    except AssertionError as e:
        msg = str(e)
        logger.info('dataset_set: %s desc: Current user id %s', msg, user_id)
        return response_error(msg)


@router.get('/retrieval_test/{app_id}', response_model=RetrievalTestResponse)
async def retrieval_test(
        app_id: int,
        user_input: str,
        userinfo: TokenData = Depends(get_current_user)
) -> RetrievalTestResponse:
    """
    Data set retrieval test

    Args:
        app_id: int, indicates app id, app_id is required.
        user_input: str, indicates user input, user_input is required.
        userinfo: TokenData, indicates user information.

    Returns:
        data: List[Dict], indicates data information.
            id: int, indicates document segments id.
            index_id: str, indicates document segments index_id.
            content: str, indicates document segments content.
            node_exec_id: int, Node run ID.
            name: str, File name.
            extension: str, File extension.
            score:float, indicates document similarity score.
            reranking_score:float, indicates document segments reranking score.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        dataset_id = Datasets().get_dataset_id(app_id)
        is_public = Datasets().get_dataset_is_public(dataset_id, team_id)
        if is_public == 0:
            Datasets().get_dataset_find(dataset_id, user_id, team_id)

        task = run_dataset.delay(dataset_id=dataset_id, user_id=user_id, user_input=user_input)
        result = task.get()
        if result['status'] == 'failed':
            return response_error(get_language_content("api_vector_acquisition_failure"))

        response_data = []
        for item in result['data']:
            data = DocumentSegments().get_segment_filename_content(item['index_id'])
            data['score'] = float(round(item['score'], 4))
            data['reranking_score'] = float(round(item['reranking_score'], 4))
            response_data.append(data)
        return response_success({'data':response_data}, get_language_content("api_vector_success"))

    except AssertionError as e:
        msg = str(e)
        logger.info('recall_test: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.get('/retrieval_history_list/{app_id}', response_model=RetrievalHistoryListResponse)
async def retrieval_history_list(
        app_id: int,
        page: int = Query(default=1),
        page_size: int = Query(default=10),
        userinfo: TokenData = Depends(get_current_user)
) -> RetrievalHistoryListResponse:
    """
    Retrieve a list of retrieval history

    Args:
        app_id: int, indicates app id, app_id is required.
        page: int, indicates page number, page is required.
        page_size: int, indicates page size, page_size is required.
        userinfo: TokenData, indicates user information.

    Returns:
        data: List[Dict], indicates data information.
            id: int, indicates reg records id.
            type: int, indicates reg records type. 1: Debug 2: Run application
            content: str, indicates document segments content.
            input: str, Recall test content.
            created_time: str, indicates reg records create time.
        paging_information: Dict, Paging information
            total_pages: int, Total pages.
            total_count: int, Total number.
            page: int, Current page.
            page_size: int, Number of items per page.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        dataset_id = Datasets().get_dataset_id(app_id)
        is_public = Datasets().get_dataset_is_public(dataset_id, team_id)
        if is_public == 0:
            Datasets().get_dataset_find(dataset_id, user_id, team_id)

        total_count = DocumentSegmentRagRecords().get_retrieval_history_count(dataset_id)
        paging_information = paging_result(page, page_size, total_count)
        result = DocumentSegmentRagRecords().get_retrieval_history_list(paging_information, dataset_id)
        for item in result['data']:
            item['created_time'] = str(item['created_time'])
            item['document_segment_num'] = item['count_document_segment_rag_records.rag_record_id']

        response = {
            'data': result['data'],
            'paging_information': {
                "total_pages": result['total_pages'],
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
            }
        }
        return response_success(response, get_language_content("api_vector_success"))

    except AssertionError as e:
        msg = str(e)
        logger.info('retrieval_history: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)

@router.get('/get_model_information', response_model=ModelInformationResponse)
async def get_model_information(userinfo: TokenData = Depends(get_current_user)) -> ModelInformationResponse:
    """
    Get model information

    Args:
        userinfo: TokenData, indicates user information.

     Returns:
        data: List[Dict], indicates data information.
            online: Dict, indicates online model information.
                id: int, indicates local model information.
                name: str, indicates local model name.
                mode: int, indicates local model information.
                suppliers_name: str, indicates local model suppliers name.
            local: Dict, indicates online model information.
                id: int, indicates local model information.
                name: str, indicates local model name.
                mode: int, indicates local model information.
                suppliers_name: str, indicates local model suppliers name.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    online_model = Models().get_model_by_type(2, team_id, 1, user_id)
    local_model = Models().get_model_by_type(2, team_id, 2, user_id)
    data = {
        'online': {
            'id': online_model['model_id'],
            'name': online_model['model_name'],
            'mode': online_model['model_mode'],
            'suppliers_name': online_model['supplier_name']
        },
        'local': {
            'id': local_model['model_id'],
            'name': local_model['model_name'],
            'mode': local_model['model_mode'],
            'suppliers_name': local_model['supplier_name']
        }
    }

    return response_success({'data': data}, get_language_content("api_vector_success"))


@router.get('/retrieval_history_detail/{rag_record_id}', response_model=RetrievalHistoryDetailResponse)
async def retrieval_history_detail(
    rag_record_id: int,
    userinfo: TokenData = Depends(get_current_user)
) -> RetrievalHistoryDetailResponse:
    """
    Retrieve a detail of retrieval history

    Args:
        rag_record_id: int, indicates rag_record_id, rag_record_id is required.
        userinfo: TokenData, indicates user information.

    Returns:
        data: List[Dict], indicates data information.
            id: int, indicates reg records id.
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        dataset_id = DocumentSegmentRagRecords().get_dataset_id(rag_record_id)
        is_public = Datasets().get_dataset_is_public(dataset_id, team_id)
        if is_public == 0:
            Datasets().get_dataset_find(dataset_id, user_id, team_id)
        data = DocumentSegmentRagRecords().get_retrieval_history_detail(rag_record_id)
        for item in data:
            item['score'] = float(round(item['score'], 4))
            item['reranking_score'] = float(round(item['reranking_score'], 4))
        return response_success({'data': data}, get_language_content("api_vector_success"))

    except AssertionError as e:
        msg = str(e)
        logger.info('recall_test: %s desc: Current user id %s',
                    msg, user_id)
        return response_error(msg)