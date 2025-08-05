from pydantic import BaseModel
from typing import Optional,Dict,Any,List,Union

class Token(BaseModel):
    access_token: str
    token_type: str

class UserData(BaseModel):
    uid: Optional[int] = None
    team_id: Optional[int] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    role: Optional[int] = None
    language: Optional[str] = None
    team_type: Optional[int] = None
    three_list: List[Any]
    
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
    role: Union[str, int]
    email_list: List[Any]
# switch_the_language
class SwitchLanguageSchema(BaseModel):
    language: str = 'en'

# Third-party user login/register schemas
class ThirdPartyLoginData(BaseModel):
    platform: str
    openid: str
    sundry: Union[str, int]
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = 'en'

class ThirdPartyUserData(BaseModel):
    uid: Optional[int] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    language: Optional[str] = None
    platform: Optional[str] = None
    openid: Optional[str] = None

class ResThirdPartyLoginSchema(BaseModel):
    code: int = 0
    detail: str = 'OK'
    data: Dict[str, Any]

class AccountBindingWithThreeParties(BaseModel):
    platform: str
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    sundry: Union[str, int]

class OpenidList(BaseModel):
    openid_list: List[Any]