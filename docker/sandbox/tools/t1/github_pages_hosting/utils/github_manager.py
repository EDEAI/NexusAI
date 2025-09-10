import requests
import base64
import json
import time
import uuid
from typing import Dict, Any, Optional


class GitHubPagesManager:
    """GitHub Pages管理器，处理仓库创建、文件上传和Pages配置"""
    
    def __init__(self, token: str):
        """
        初始化GitHub API客户端
        
        Args:
            token: GitHub个人访问令牌
        """
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Dify-GitHub-Pages-Plugin"
        }
        self.base_url = "https://api.github.com"
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取当前用户信息"""
        response = requests.get(f"{self.base_url}/user", headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def create_repository(self, name: str, description: str = "", is_private: bool = False) -> Dict[str, Any]:
        """
        创建GitHub仓库
        
        Args:
            name: 仓库名称
            description: 仓库描述
            is_private: 是否为私有仓库
            
        Returns:
            仓库信息字典
        """
        payload = {
            "name": name,
            "description": description,
            "private": is_private,
            "auto_init": True,
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False
        }
        
        response = requests.post(
            f"{self.base_url}/user/repos",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 422:
            # 仓库可能已存在，尝试获取
            user_info = self.get_user_info()
            username = user_info["login"]
            return self.get_repository(username, name)
        
        response.raise_for_status()
        return response.json()
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库信息"""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, owner: str, repo: str, file_path: str, content: str, message: str = "Add HTML file") -> Dict[str, Any]:
        """
        上传文件到GitHub仓库
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            file_path: 文件路径
            content: 文件内容
            message: 提交消息
            
        Returns:
            上传结果
        """
        # 检查文件是否已存在
        existing_file = None
        try:
            existing_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}",
                headers=self.headers,
                timeout=10
            )
            if existing_response.status_code == 200:
                existing_file = existing_response.json()
        except:
            pass
        
        # 准备文件内容（Base64编码）
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        payload = {
            "message": message,
            "content": content_encoded
        }
        
        # 如果文件已存在，需要提供SHA
        if existing_file:
            payload["sha"] = existing_file["sha"]
            message = f"Update {file_path}"
            payload["message"] = message
        
        response = requests.put(
            f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        # 提供更详细的错误信息
        if not response.ok:
            error_detail = f"HTTP {response.status_code}: {response.reason}"
            try:
                error_json = response.json()
                if 'message' in error_json:
                    error_detail += f" - {error_json['message']}"
                if 'errors' in error_json:
                    error_detail += f" - Errors: {error_json['errors']}"
            except:
                error_detail += f" - Response: {response.text[:200]}"
            
            raise requests.exceptions.HTTPError(error_detail)
        
        return response.json()
    
    def enable_pages(self, owner: str, repo: str, source_branch: str = "main") -> Dict[str, Any]:
        """
        启用GitHub Pages
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            source_branch: 源分支
            
        Returns:
            Pages配置信息
        """
        payload = {
            "source": {
                "branch": source_branch,
                "path": "/"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/repos/{owner}/{repo}/pages",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        
        # Pages可能已经启用
        if response.status_code == 409:
            return self.get_pages_info(owner, repo)
        
        response.raise_for_status()
        return response.json()
    
    def get_pages_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取GitHub Pages信息"""
        response = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}/pages",
            headers=self.headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def generate_unique_repo_name(self, base_name: str = "html-hosting") -> str:
        """生成唯一的仓库名称"""
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        return f"{base_name}-{timestamp}-{unique_id}"
    
    def validate_html_content(self, html_content: str) -> bool:
        """验证HTML内容的基本有效性"""
        if not html_content or not html_content.strip():
            return False
        
        # 基本的HTML标签检查
        html_lower = html_content.lower()
        has_html_tags = any(tag in html_lower for tag in ['<html', '<head', '<body', '<div', '<p', '<h1', '<h2', '<h3'])
        
        return has_html_tags
    
    def wait_for_pages_deployment(self, owner: str, repo: str, max_wait: int = 300) -> bool:
        """
        等待GitHub Pages部署完成
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            max_wait: 最大等待时间（秒）
            
        Returns:
            是否部署成功
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                pages_info = self.get_pages_info(owner, repo)
                if pages_info.get("status") == "built":
                    return True
                elif pages_info.get("status") == "errored":
                    return False
            except:
                pass
            
            time.sleep(10)  # 等待10秒后重试
        
        return False
    
    def ensure_pages_repository(self, username: str) -> Dict[str, Any]:
        """
        确保用户的GitHub Pages仓库存在
        
        Args:
            username: GitHub用户名
            
        Returns:
            仓库信息字典
        """
        repo_name = f"{username}.github.io"
        
        try:
            # 尝试获取现有仓库
            return self.get_repository(username, repo_name)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # 仓库不存在，创建新的GitHub Pages仓库
                return self.create_repository(
                    name=repo_name,
                    description=f"{username}'s GitHub Pages repository",
                    is_private=False  # GitHub Pages必须是公开仓库
                )
            else:
                raise
    
    def ensure_pages_enabled(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        确保GitHub Pages已启用
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            Pages配置信息
        """
        try:
            # 尝试获取现有Pages配置
            return self.get_pages_info(owner, repo)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Pages未启用，启用GitHub Pages
                return self.enable_pages(owner, repo)
            else:
                raise
