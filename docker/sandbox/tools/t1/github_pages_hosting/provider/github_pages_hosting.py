from typing import Any
import requests
import json
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class GitHubPagesHostingProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证GitHub访问令牌的有效性
        
        Args:
            credentials: 包含GitHub token的凭证字典
            
        Raises:
            ToolProviderCredentialValidationError: 当凭证无效时抛出
        """
        try:
            token = credentials.get("github_token")
            if not token:
                raise ToolProviderCredentialValidationError("GitHub token is required")
            
            # 验证token是否有效
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Dify-GitHub-Pages-Plugin"
            }
            
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            
            if response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid GitHub token")
            elif response.status_code == 403:
                raise ToolProviderCredentialValidationError("GitHub token lacks required permissions")
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"GitHub API error: {response.status_code}")
            
            # 检查token权限范围
            token_scopes = response.headers.get("X-OAuth-Scopes", "")
            if "repo" not in token_scopes:
                raise ToolProviderCredentialValidationError("GitHub token must have 'repo' scope")
                
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to validate GitHub token: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Credential validation error: {str(e)}")
