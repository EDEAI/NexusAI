import aniRequest, { BASE_URL } from './request';

export const getUploadUrl = async () => {
    return `${BASE_URL}/v1/upload/upload_file`;
};

// Query document list
export const documentList = async (data: any) => {
    let app_id = data.app_id;
    delete data.app_id;
    const res = await aniRequest<any>(`/v1/vector/documents_list/${app_id}`, {
        method: 'GET',
        data: data,
    });
    return res;
};

// Get supplier and model names
export const getInforMation = async (embeddingModelConfigId: any) => {
    const res = await aniRequest<any>(`/v1/vector/get_model_information/${embeddingModelConfigId||0}`, { method: 'GET' });
    return res;
};

// Add document
export const addDocument = async (data: any) => {
    const res = await aniRequest<any>('/v1/vector/add_document', { method: 'POST', data: data });
    return res;
};

// Disable document
export const disableDocument = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/disable_document/${data}`, { method: 'PUT' });
    return res;
};

// Enable document
export const enableDocument = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/enable_document/${data}`, { method: 'PUT' });
    return res;
};

// Delete document
export const deleteDocument = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/delete_document/${data}`, { method: 'DELETE' });
    return res;
};

// Load document details
export const documentSegmentsList = async (data: any) => {
    let document_id = data.document_id;
    delete data.document_id;
    const res = await aniRequest<any>(`/v1/vector/document_segments_list/${document_id}`, {
        method: 'GET',
        data: data,
    });
    return res;
};

// Enable document segment
export const enableSegment = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/enable_segment/${data}`, { method: 'PUT' });
    return res;
};

// Disable document segment
export const disableSegment = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/disable_segment/${data}`, { method: 'PUT' });
    return res;
};

// Modify settings
export const datasetSet = async (data: any) => {
    let app_id = data.app_id;
    delete data.app_id;
    const res = await aniRequest<any>(`/v1/vector/dataset_set/${app_id}`, { method: 'PUT', data });
    return res;
};

// Retrieval history
export const retrievalHistoryList = async (data: any, id) => {
    const res = await aniRequest<any>(`/v1/vector/retrieval_history_list/${id}`, {
        method: 'GET',
        data: data,
    });
    return res;
};

// Retrieval test
export const retrievalTest = async (data: any, id) => {
    const res = await aniRequest<any>(`/v1/vector/retrieval_test/${id}`, {
        method: 'GET',
        data: data,
    });
    return res;
};

// Archive
export const archiveDocument = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/archive_document/${data}`, { method: 'PUT' });
    return res;
};

// Cancel archive
export const cancelArchiveDocument = async (data: any) => {
    const res = await aniRequest<any>(`/v1/vector/cancel_archive_document/${data}`, {
        method: 'PUT',
    });
    return res;
};

// Retrieval test history
export const retrievalHistoryDetail = async id => {
    const res = await aniRequest<any>(`/v1/vector/retrieval_history_detail/${id}`, {
        method: 'GET',
    });
    return res;
};