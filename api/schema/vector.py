from typing import List, Dict, Any, Optional, Union
from fastapi import UploadFile
from pydantic import BaseModel, Field

class ReqUploadFileSchema(BaseModel):
    user_id: str
    file: UploadFile

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123",
                    "file": "select your file"
                }
            ]
        }
    }

class UploadFileResponse(BaseModel):
    code: int
    detail: str
    data: Optional[Dict[str, Any]] = None

class CostResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DatasetListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class CreateDatasetResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class AddDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class EnableSegmentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DisableSegmentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DeleteDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DeleteDatasetResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DocumentsListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DocumentSegmentsListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DisableDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class EnableDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ArchivedDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class CancelArchivedDocumentResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RecallLogSchemaResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class DatasetSetResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RetrievalTestResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RetrievalHistoryListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class RetrievalHistoryDetailResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class ModelInformationResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class CreateDatasetSchema(BaseModel):
    name: str
    description: str
    enable_api: int
    is_public: int
    process_rule_id: int
    data_source_type: int
    indexing_mode: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name" : "TestName",
                    "description" : "Description",
                    "enable_api": "1",
                    "is_public": "1",
                    "process_rule_id": "1",
                    "data_source_type": "1",
                    "indexing_mode": "2"
                }
            ]
        }
    }

class AddDocumentSchema(BaseModel):
    app_id: int
    process_rule_id: int
    data_source_type: int
    file_ids: List[int]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "app_id" : 240,
                    "process_rule_id" : 1,
                    "data_source_type": 1,
                    "file_ids": [45,46],
                }
            ]
        }
    }

class EnableDocumentSchema(BaseModel):
    documents_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "documents_id" : 0,
                }
            ]
        }
    }


class DocumentsListSchema(BaseModel):
    dataset_id: int
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    name: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "dataset_id": "18",
                    "name" : 'name,page,page_size',
                    "page":1,
                    "page_size":10,
                }
            ]
        }
    }

class GetCostSchema(BaseModel):
    file_ids: List[int]
    indexing_mode: int
    process_rule_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "file_ids": [1,2],
                    "indexing_mode": 1,
                    "process_rule_id": 1
                }
            ]
        }
    }

class DatasetSetSchema(BaseModel):
    name: str
    description: str
    public: int
    mode: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": '1',
                    "description": '',
                    "public": 1,
                    "mode": 1
                }
            ]
        }
    }