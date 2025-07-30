import os
import json
import hashlib
import tempfile
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DeployHtmlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Deploy HTML content to EdgeOne Pages
        """
        try:
            html_content = tool_parameters.get("html_content", "")
            
            if not html_content:
                yield self.create_text_message("HTML content is required.")
                return
            
            # Generate installation ID
            installation_id = self._generate_installation_id()
            
            # Get base URL for deployment
            yield self.create_text_message("Getting EdgeOne Pages deployment endpoint...")
            base_url = self._get_base_url()
            
            # Deploy HTML content
            yield self.create_text_message("Deploying HTML content to EdgeOne Pages...")
            deployment_url = self._deploy_html(html_content, base_url, installation_id)
            
            # Return success message and URL
            yield self.create_text_message(f"✅ HTML deployed successfully!")
            yield self.create_text_message(f"🌐 Public URL: {deployment_url}")
            yield self.create_json_message({
                "success": True,
                "url": deployment_url,
                "type": "html_deployment",
                "message": "HTML content deployed successfully to EdgeOne Pages with global edge delivery"
            })
            
        except Exception as e:
            error_message = f"❌ Failed to deploy HTML: {str(e)}"
            yield self.create_text_message(error_message)
            yield self.create_json_message({
                "success": False,
                "error": str(e),
                "type": "html_deployment"
            })
    
    def _generate_installation_id(self) -> str:
        """Generate a unique installation ID"""
        try:
            id_file_path = os.path.join(tempfile.gettempdir(), 'edgeone-pages-id')
            
            if os.path.exists(id_file_path):
                with open(id_file_path, 'r') as f:
                    existing_id = f.read().strip()
                    if existing_id:
                        return existing_id
            
            # Generate new ID
            new_id = hashlib.md5(os.urandom(8)).hexdigest()[:16]
            
            try:
                with open(id_file_path, 'w') as f:
                    f.write(new_id)
            except Exception:
                pass  # Ignore write errors
            
            return new_id
            
        except Exception:
            # Fallback to random ID
            return hashlib.md5(os.urandom(8)).hexdigest()[:16]
    
    def _get_base_url(self) -> str:
        """Get the base URL for EdgeOne Pages deployment"""
        try:
            response = requests.get('https://mcp.edgeone.site/get_base_url', timeout=30)
            response.raise_for_status()
            
            data = response.json()
            base_url = data.get('baseUrl')
            
            if not base_url:
                raise Exception("Invalid response: missing baseUrl")
            
            return base_url
            
        except requests.RequestException as e:
            raise Exception(f"Failed to get deployment endpoint: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to parse deployment endpoint response: {str(e)}")
    
    def _deploy_html(self, html_content: str, base_url: str, installation_id: str) -> str:
        """Deploy HTML content to EdgeOne Pages"""
        try:
            payload = {
                'value': html_content
            }
            
            headers = {
                'Content-Type': 'application/json',
                'X-Installation-ID': installation_id,
            }
            
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            deployment_url = result.get('url')
            
            if not deployment_url:
                raise Exception("Invalid deployment response: missing URL")
            
            return deployment_url
            
        except requests.RequestException as e:
            raise Exception(f"Failed to deploy HTML content: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to process deployment response: {str(e)}")