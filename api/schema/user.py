from pydantic import BaseModel
from typing import Optional,Dict,Any,List

class Token(BaseModel):
    access_token: str
    token_type: str

class UserData(BaseModel):
    uid: Optional[int] = None
    team_id: Optional[int] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[int] = None
    language: Optional[str] = None
    
class RegisterTeamData(BaseModel):
    team_id: Optional[int] = 1

class ResRegisterTeamSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: RegisterTeamData

class RegisterUserData(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    nickname: Optional[str] = None

class ResRegisterUserSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: RegisterUserData

class ResUserInfoSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: UserData

class ResUserLogoutSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: str = 'success'

class ResDictSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: Dict[str, Any]
class CreateDataEmailList(BaseModel):
    role: int
    email_list: List[Any]
# switch_the_language
class SwitchLanguageSchema(BaseModel):
    language: str = 'en'

    
