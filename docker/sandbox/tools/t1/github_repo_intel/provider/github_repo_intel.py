from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GithubRepoIntelProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            github_token = credentials.get("github_token", "")
            
            # Test GitHub API access
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "GitHubRepoIntel-Dify-Plugin"
            }
            
            if github_token:
                # Test authenticated access
                headers["Authorization"] = f"Bearer {github_token}"
                response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Valid token
                    return
                elif response.status_code == 401:
                    raise ToolProviderCredentialValidationError("Invalid GitHub personal access token. Please check your token and try again.")
                else:
                    raise ToolProviderCredentialValidationError(f"GitHub API error: {response.status_code} - {response.text}")
            else:
                # Test unauthenticated access (basic rate limit check)
                response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Can access API without authentication
                    return
                else:
                    raise ToolProviderCredentialValidationError(f"Unable to access GitHub API: {response.status_code} - {response.text}")
                    
        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError("Timeout connecting to GitHub API. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Network error connecting to GitHub API: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Unexpected error during credential validation: {str(e)}")
