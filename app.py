import uvicorn
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.vector import router as vector_router
from api.upload import router as upload_router
from api.workflow.workflow import router as workflow_router
from api.auth import router as auth_router
# from api.auth.token import router as token_router
from api.skill import router as skill_router
from api.tools import router as tools_router
from api.index import router as index_router
from api.llm import router as llm_router

from api.apps import app_api_router
from api.apps import router as apps_router

from api.agent import router as agent_router
from api.icon import router as icon_router
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlowPassword as OAuthFlowPasswordModel
from api.workspace import router as workspace_router
from api.chatroom.chatroom import router as chatroom_router
from api.tag import router as tag_router

from api.workflow.node import router as node_router
from api.supplier import router as supplier_router
from sqlalchemy import event
from sqlalchemy.engine import Engine
from config import settings
from log import Logger

sql_logger = Logger.get_logger("sql")

# Listen to SQLAlchemy events and record SQL execution logs
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    sql_logger.info(f"SQL Statement: {statement}")
    sql_logger.info(f"Parameters: {parameters}")
    sql_logger.info(f"SQL Statement & Parameters: {statement % parameters}")


class OAuth2PasswordBearerWithCookie(OAuth2Model):
    def __init__(self, tokenUrl: str):
        flows = OAuthFlowsModel(password=OAuthFlowPasswordModel(tokenUrl=tokenUrl))
        super().__init__(flows=flows)

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/v1/auth/login")

app = FastAPI(
    title="NexusAI API",
    description="There are APIs that does NexusAI things.",
    version="1.0.0"
)

"""
Allows requests from all origins, which is convenient for local debugging.
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(index_router, prefix='/v1/index', tags=["index"])
app.include_router(auth_router, prefix='/v1/auth', tags=["auth"])
app.include_router(workflow_router, prefix='/v1/workflow', tags=["workflow"])
# app.include_router(token_router, prefix="/v1/token", tags=["token"])
app.include_router(vector_router, prefix='/v1/vector', tags=["vector"])
app.include_router(upload_router, prefix='/v1/upload', tags=["upload"])
app.include_router(skill_router, prefix='/v1/skill', tags=["skill"])
app.include_router(agent_router, prefix='/v1/agent', tags=["agent"])
app.include_router(workspace_router, prefix='/v1/workspace', tags=["workspace"])
app.include_router(chatroom_router, prefix='/v1/chatroom', tags=["chatroom"])
app.include_router(app_api_router, prefix='/v1/app-api', tags=["app-api"])
app.include_router(apps_router, prefix='/v1/apps', tags=["apps"])
app.include_router(tools_router, prefix='/v1/tool', tags=["tool"])
app.include_router(llm_router, prefix='/v1/llm', tags=["llm"])
app.include_router(node_router, prefix='/v1/node', tags=["node"])
app.include_router(supplier_router, prefix='/v1/supplier', tags=["supplier"])
app.include_router(icon_router, prefix='/v1/icon', tags=["icon"])
app.include_router(tag_router, prefix='/v1/tag', tags=["tag"])


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=settings.API_PORT, workers=settings.FASTAPI_WORKERS)
