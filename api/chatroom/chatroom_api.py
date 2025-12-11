import re
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Header
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from jose import jwt

from api.utils.common import response_error, response_success
from config import settings
from core.database import redis
from core.database.models import Apps, ChatroomAgentRelation, ChatroomMessages, Chatrooms
from core.helper import decrypt_id, encrypt_id


router = APIRouter()

SESSION_TOKEN_TYPE = 'chatroom_api'
# Keep the session short-lived to limit exposure of a leaked URL
SESSION_EXPIRE_SECONDS = 3600


def _parse_bearer_token(authorization: str) -> Optional[str]:
    match = re.fullmatch(r'Bearer (.+)', authorization or '')
    if not match:
        return None
    return match.group(1)


def _build_ws_url(token: str) -> str:
    api_base = urlparse(settings.WEB_API_URL)
    scheme = 'wss' if api_base.scheme == 'https' else 'ws'
    host = api_base.hostname or '127.0.0.1'
    port = settings.CHATROOM_WEBSOCKET_PORT
    return f'{scheme}://{host}:{port}/ws_chat?token={token}'


def _get_app(app_id: int, api_token: str):
    app = Apps().select_one(
        columns=['id', 'team_id', 'user_id', 'enable_api', 'status', 'mode', 'api_token', 'description'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'status', 'value': 1},
            {'column': 'mode', 'value': 5},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None or app['api_token'] != api_token:
        return None
    return app


class SessionResponse(BaseModel):
    ws_url: str
    session_id: str
    expires_in: int
    session_name: str


@router.post('/{encrypted_chatroom_app_id}/session')
async def create_chatroom_session(
    authorization: Annotated[str, Header(description='API key')],
    encrypted_chatroom_app_id: str,
):
    """
    Create a short-lived chatroom session and return the websocket URL.
    """
    try:
        app_id = decrypt_id(encrypted_chatroom_app_id)
    except Exception:
        return response_error('Invalid URL')

    api_token = _parse_bearer_token(authorization)
    if not api_token:
        return response_error('Invalid authorization header')

    app = _get_app(app_id, api_token)
    if app is None:
        return response_error('Invalid app API token, or the app is not enabled for API.')

    base_chatroom = Chatrooms().select_one(
        columns=['id', 'team_id', 'user_id', 'app_id', 'max_round'],
        conditions=[
            {'column': 'app_id', 'value': app_id},
            {'column': 'status', 'value': 1},
            {'column': 'is_temporary', 'value': 0}
        ]
    )
    if base_chatroom is None:
        return response_error('No available chatroom for this app.')

    session_app_id = Apps().insert(
        {
            'team_id': app['team_id'],
            'user_id': app['user_id'],
            'name': '新会话',
            'description': app.get('description', ''),
            'mode': 5,
            'status': 1,
            'enable_api': 1,
            'api_token': app['api_token']
        }
    )

    session_chatroom_id = Chatrooms().insert(
        {
            'team_id': base_chatroom['team_id'],
            'user_id': base_chatroom['user_id'],
            'app_id': session_app_id,
            'max_round': base_chatroom['max_round'],
            'status': 1,
            'is_temporary': 1
        }
    )

    agents = ChatroomAgentRelation().get_agents_by_chatroom_id(base_chatroom['id'])
    if agents:
        ChatroomAgentRelation().insert_agent(
            {
                'chatroom_id': session_chatroom_id,
                'agent': [
                    {'agent_id': agent['agent_id'], 'active': agent['active']}
                    for agent in agents
                ]
            }
        )

    exp = datetime.now(timezone.utc) + timedelta(seconds=SESSION_EXPIRE_SECONDS)
    payload = {
        'type': SESSION_TOKEN_TYPE,
        'chatroom_id': session_chatroom_id,
        'session_id': session_app_id,
        'exp': exp
    }
    session_token = jwt.encode(payload, settings.ACCESS_TOKEN_SECRET_KEY, algorithm='HS256')
    redis.setex(f'chatroom_api_token:{session_app_id}', SESSION_EXPIRE_SECONDS, session_token)

    encrypted_session_id = encrypt_id(session_app_id)
    ws_url = _build_ws_url(session_token)

    return response_success(
        {
            'ws_url': ws_url,
            'session_id': encrypted_session_id,
            'expires_in': SESSION_EXPIRE_SECONDS,
            'session_name': '新会话'
        }
    )


@router.get('/session/{session_id}/messages')
async def get_session_messages(
    authorization: Annotated[str, Header(description='API key')],
    session_id: str,
    page: int = 1,
    page_size: int = 10,
    chat_base_url: Optional[str] = None
):
    """
    Fetch chatroom messages for a temporary session.
    """
    api_token = _parse_bearer_token(authorization)
    if not api_token:
        return response_error('Invalid authorization header')

    try:
        raw_session_app_id = decrypt_id(session_id)
    except Exception:
        return response_error('Invalid session ID')

    session_chatroom = Chatrooms().select_one(
        columns=['id', 'app_id'],
        conditions=[
            {'column': 'app_id', 'value': raw_session_app_id},
            {'column': 'status', 'value': 1},
            {'column': 'is_temporary', 'value': 1}
        ]
    )
    if session_chatroom is None:
        return response_error('Session chatroom not found')

    app = _get_app(session_chatroom['app_id'], api_token)
    if app is None:
        return response_error('Invalid app API token, or the app is not enabled for API.')

    if not redis.get(f'chatroom_api_token:{raw_session_app_id}'):
        return response_error('Session has expired or is invalid')

    chatroom_history_msg = ChatroomMessages().history_chatroom_messages(
        session_chatroom['id'], page, page_size, chat_base_url
    )

    Chatrooms().update(
        {"column": "id", "value": session_chatroom['id']},
        {'active': 0}
    )
    ChatroomMessages().update(
        {"column": "chatroom_id", "value": session_chatroom['id']},
        {'is_read': 1}
    )

    return response_success(chatroom_history_msg)


@router.get('/{encrypted_chatroom_app_id}/openapi')
async def chatroom_api_openapi(encrypted_chatroom_app_id: str):
    """
    Generate OpenAPI schema for chatroom API.
    """
    try:
        app_id = decrypt_id(encrypted_chatroom_app_id)
    except Exception:
        return response_error('Invalid URL')

    app = Apps().select_one(
        columns=['name', 'description'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'status', 'value': 1},
            {'column': 'mode', 'value': 5},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None:
        return response_error('App is not enabled for API.')

    dummy_router = APIRouter()

    @dummy_router.post(
        f'/v1/chatroom-api/{encrypted_chatroom_app_id}/session',
        response_model=SessionResponse
    )
    async def _session_endpoint(
        authorization: Annotated[str, Header(description='API key, format: "Bearer <api_token>"')],
    ):
        pass

    @dummy_router.get(
        f'/v1/chatroom-api/session/{{session_id}}/messages'
    )
    async def _messages_endpoint(
        authorization: Annotated[str, Header(description='API key, format: "Bearer <api_token>"')],
        session_id: str,
        page: int = 1,
        page_size: int = 10,
        chat_base_url: Optional[str] = None
    ):
        pass

    openapi_schema = get_openapi(
        title=app['name'],
        version='1.0.0',
        description=app['description'],
        routes=dummy_router.routes
    )
    return openapi_schema


@router.get('/{encrypted_chatroom_app_id}/docs')
async def chatroom_api_docs(encrypted_chatroom_app_id: str):
    """
    Render Redoc documentation for chatroom API.
    """
    try:
        app_id = decrypt_id(encrypted_chatroom_app_id)
    except Exception:
        return response_error('Invalid URL')
    app = Apps().select_one(
        columns=['name'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'status', 'value': 1},
            {'column': 'mode', 'value': 5},
            {'column': 'enable_api', 'value': 1}
        ]
    )
    if app is None:
        return response_error('App is not enabled for API.')
    return get_redoc_html(
        openapi_url=f'/v1/chatroom-api/{encrypted_chatroom_app_id}/openapi',
        title=app['name']
    )
