from pydantic import BaseModel


class VideoSearchData(BaseModel):
    type: str
    typename: str
    bvid: str
    title: str
    description: str
    pic: str
    play: int
    review: int
    pubdate: int
    duration: str
    rank_score: int
    like: int


class SearchData(BaseModel):
    seid: str
    page: int
    pagesize: int
    numResults: int
    numPages: int
    result: list[VideoSearchData]


class SearchResult(BaseModel):
    code: int
    message: str
    ttl: int
    data: SearchData

class VideoOwner(BaseModel):
    mid: int
    name: str
    face: str


class VideoStats(BaseModel):
    aid: int
    view: int
    danmaku: int
    reply: int
    favorite: int
    coin: int
    share: int
    now_rank: int
    his_rank: int
    like: int
    dislike: int
    evaluation: str
    vt: int

class VideoData(BaseModel):
    bvid: str
    tname: str
    tname_v2: str
    pic: str
    title: str
    pubdate: int
    ctime: int
    desc: str
    owner: VideoOwner
    stat: VideoStats

class VideoResult(BaseModel):
    code: int
    message: str
    ttl: int
    data: VideoData