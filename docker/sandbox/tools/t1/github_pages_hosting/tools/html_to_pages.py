from collections.abc import Generator
from typing import Any
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 导入GitHub管理器
from utils.github_manager import GitHubPagesManager


class HtmlToPagesTool(Tool):
    """将HTML内容托管到GitHub Pages的工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        执行HTML到GitHub Pages的托管过程
        
        Args:
            tool_parameters: 工具参数字典
            
        Yields:
            ToolInvokeMessage: 工具执行消息
        """
        try:
            # 获取必需参数
            html_content = tool_parameters.get("html_content", "").strip()
            
            # 验证HTML内容
            if not html_content:
                yield self.create_text_message("错误：HTML内容不能为空")
                return
            
            # 获取可选参数 - 现在只需要一个唯一ID来生成文件名
            unique_id = tool_parameters.get("unique_id")
            if not unique_id:
                # 生成唯一ID（时间戳 + UUID）
                import uuid
                unique_id = f"{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # 使用唯一ID作为文件名
            file_name = f"{unique_id}.html"

            # 获取GitHub token
            github_token = self.runtime.credentials.get("github_token")
            if not github_token:
                yield self.create_text_message("错误：GitHub访问令牌未配置")
                return

            # 初始化GitHub管理器
            github_manager = GitHubPagesManager(github_token)
            
            # 验证HTML内容
            if not github_manager.validate_html_content(html_content):
                yield self.create_text_message("⚠️ 警告：提供的内容可能不是有效的HTML格式")
            
            # 获取用户信息
            user_info = github_manager.get_user_info()
            username = user_info["login"]
            
            # 使用用户的GitHub Pages仓库 {username}.github.io
            repository_name = f"{username}.github.io"

            # 确保GitHub Pages仓库存在
            repo_info = github_manager.ensure_pages_repository(username)

            repository_url = repo_info["html_url"]

            # 上传HTML文件到GitHub Pages仓库
            github_manager.upload_file(
                owner=username,
                repo=repository_name,
                file_path=file_name,
                content=html_content,
                message=f"Add {file_name} via Dify plugin"
            )
            

            # 确保GitHub Pages已启用（对于用户的GitHub Pages仓库）
            try:
                github_manager.ensure_pages_enabled(username, repository_name)
            except Exception as e:
                yield self.create_text_message(f"⚠️ GitHub Pages配置: {str(e)}")
            
            # 构建Pages URL - 直接使用用户的GitHub Pages域名
            pages_url = f"https://{username}.github.io/{unique_id}.html"

            # 等待部署完成（GitHub Pages仓库通常部署较快）
            deployment_success = github_manager.wait_for_pages_deployment(username, repository_name, max_wait=60)
            
            if deployment_success:
                status = "deployed"
            else:
                status = "deploying"
            
            # 返回结果
            result = {
                "pages_url": pages_url,
                "repository_url": repository_url,
                "file_path": file_name,
                "unique_id": unique_id,
                "status": status
            }
            
            yield self.create_json_message(result)
            
            # 为工作流提供变量
            yield self.create_variable_message("pages_url", pages_url)

        except Exception as e:
            error_message = f"❌ 处理过程中发生错误: {str(e)}"
            yield self.create_text_message(error_message)
            
            # 提供故障排除建议
            if "rate limit" in str(e).lower():
                yield self.create_text_message("💡 建议: GitHub API速率限制，请稍后重试")
            elif "token" in str(e).lower():
                yield self.create_text_message("💡 建议: 请检查GitHub访问令牌是否有效且具有正确权限")
            elif "repository" in str(e).lower():
                yield self.create_text_message("💡 建议: 仓库名称可能已存在或包含无效字符")
            else:
                yield self.create_text_message("💡 建议: 请检查网络连接和GitHub服务状态")
