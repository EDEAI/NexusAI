import json, os, sys, time, threading, traceback
os.environ['DATABASE_AUTO_COMMIT'] = 'True'
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

import asyncio
from typing import Dict, Any
from languages import get_language_content
from core.workflow.variables import create_variable_from_dict
from core.llm.prompt import create_prompt_from_dict
from api.utils.common import response_error, response_success
from api.utils.jwt import TokenData
from celery_app import run_app

# 引入Agent相关模型
from core.database.models.agents import Agents
from core.database.models.apps import Apps
from core.database.models.agent_abilities import AgentAbilities


class AgentModel:
    """Agent模型层，负责数据访问"""
    
    def __init__(self):
        self.agents = Agents()
        self.apps = Apps()
        self.abilities = AgentAbilities()
    
    def get_agent(self, agent_id: int, team_id: int):
        """获取Agent信息"""
        return self.agents.select_one(
            columns="*",
            conditions=[
                {"column": "id", "value": agent_id},
                {"column": "team_id", "value": team_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
    
    def get_app(self, app_id: int, team_id: int):
        """获取App信息"""
        return self.apps.select_one(
            columns="*", 
            conditions=[
                {"column": "id", "value": app_id},
                {"column": "team_id", "value": team_id},
                {"column": "mode", "value": 1},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
    
    def get_ability(self, ability_id: int, agent_id: int):
        """获取能力信息"""
        return self.abilities.select_one(
            columns="*",
            conditions=[
                {"column": "id", "value": ability_id},
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )


class AgentProvider:
    """Agent提供者层，负责业务逻辑"""
    
    async def run_agent(self, agent_id: int, ability_id: int, input_dict: Dict[str, Any], 
                        prompt: Dict[str, Any], userinfo: TokenData, model: AgentModel):
        """运行Agent
        
        Args:
            agent_id: Agent ID
            ability_id: 能力ID
            input_dict: 输入数据
            prompt: 提示数据
            userinfo: 用户信息
            model: 模型层实例
            
        Returns:
            处理结果
        """
        # 验证输入
        if agent_id <= 0:
            return response_error(get_language_content("api_agent_run_agent_id_required"))
        if not input_dict:
            return response_error(get_language_content("api_agent_run_input_dict_required"))
        try:
            create_variable_from_dict(input_dict)
        except:
            return response_error(get_language_content("api_agent_run_input_dict_wrong"))
        if not prompt:
            return response_error(get_language_content("api_agent_run_prompt_required"))
        try:
            create_prompt_from_dict(prompt)
        except:
            return response_error(get_language_content("api_agent_run_prompt_wrong"))
            
        # 获取agent
        agent = model.get_agent(agent_id, userinfo.team_id)
        if not agent:
            return response_error(get_language_content("api_agent_run_agent_error"))
        if agent["user_id"] != userinfo.uid:
            if agent["status"] != 1:
                return response_error(get_language_content("api_agent_run_agent_status_not_normal"))
            if agent["publish_status"] != 1:
                return response_error(get_language_content("api_agent_run_not_creators"))

        # 获取app
        app = model.get_app(agent["app_id"], userinfo.team_id)
        if not app:
            return response_error(get_language_content("api_agent_run_app_error"))
        if app["user_id"] != userinfo.uid:
            if app["is_public"] == 0:
                return response_error(get_language_content("api_agent_run_team_not_open"))
            if app["status"] != 1:
                return response_error(get_language_content("api_agent_run_app_status_not_normal"))

        # 获取agent ability
        if ability_id != 0:
            ability = model.get_ability(ability_id, agent_id)
            if not ability:
                return response_error(get_language_content("api_agent_run_ability_error"))
            if ability["user_id"] != userinfo.uid and ability["status"] != 1:
                return response_error(get_language_content("api_agent_run_ability_status_not_normal"))

        # 执行任务
        task = run_app.delay(
            app_type="agent", 
            id_=agent_id, 
            user_id=userinfo.uid, 
            input_dict=input_dict, 
            ability_id=ability_id,
            prompt=prompt
        )
        
        # 等待任务完成
        while not task.ready():
            await asyncio.sleep(0.1)
        result = task.get()
        if result["status"] != "success":
            return response_error(result["message"])

        return response_success(
            {"outputs": result["data"]["outputs"], "outputs_md": result["data"]["outputs_md"]},
            get_language_content("api_agent_success")
        )


class MCPClient:
    """MCP客户端，控制器层"""
    
    def __init__(self):
        # 初始化Agent MCP组件
        self.agent_model = AgentModel()
        self.agent_provider = AgentProvider()
        
    async def run_agent(self, agent_id: int, ability_id: int, input_dict: Dict[str, Any], 
                        prompt: Dict[str, Any], userinfo: TokenData):
        """运行Agent的MCP封装方法
        
        Args:
            agent_id: Agent ID
            ability_id: 能力ID
            input_dict: 输入数据
            prompt: 提示数据
            userinfo: 用户信息
            
        Returns:
            处理结果
        """
        print(111111111111111111111111111111111111111111111111)
        return await self.agent_provider.run_agent(
            agent_id=agent_id,
            ability_id=ability_id,
            input_dict=input_dict,
            prompt=prompt,
            userinfo=userinfo,
            model=self.agent_model
        )