from typing import Dict,Any
from pydantic import BaseModel

class ErrorResponseSchema(BaseModel):
    status: int = 1000
    msg: str = "FAIL"
    data: Dict[str, Any] = {}

class RespBaseSchema(BaseModel):
    """
    Base response schema.
    
    Attributes:
        status (int): The response status code, 0 by default.
        msg (str): The response message, 'OK' by default.
        data (Dict): The response data, an empty dictionary by default.
    """
    code: int = 0
    detail: str = 'OK'
    data: Dict = {}

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "file_id": "123"
    #             }
    #         ]
    #     }
    # }