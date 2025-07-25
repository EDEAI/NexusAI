from enum import Enum

from pydantic import BaseModel, Field

KOOK_API_URL = "https://www.kookapp.cn/api/v3"


class MsgType(Enum):
    Warning = ("Warning", "#FFA500")  # Orange
    Error = ("Error", "#FF0000")  # Red
    Info = ("Info", "#145AEF")  # Blue
    Success = ("Success", "#008000")  # Green

    def __init__(self, value: str, color: str):
        self._value_ = value
        self.color = color

    @property
    def color_code(self) -> str:
        return self.color


class Input(BaseModel):
    title: str = Field(default="Title")
    content: str = Field(default="Content")
    type: MsgType = Field(default=MsgType.Info)
