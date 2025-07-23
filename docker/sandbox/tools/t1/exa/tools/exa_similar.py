from collections.abc import Generator
from typing import Any, Dict, List, Optional
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ExaSimilarTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Find similar links based on a given URL using the Exa API.
        
        Args:
            tool_parameters: Dictionary containing:
                - url: The URL for which to find similar links (required)
                - num_results: Number of results to return (default: 10, max: 100)
                - text: Whether to include full text of results (default: False)
        
        Returns:
            Generator yielding ToolInvokeMessage with similar links results
        """
        try:
            # Get API key from runtime credentials
            api_key = self.runtime.credentials["exa_api_key"]
            
            # Required parameter
            url = tool_parameters.get("url")
            if not url:
                raise ValueError("URL is required")
                
            # Optional parameters with defaults
            num_results = int(tool_parameters.get("num_results", 10))
            if num_results > 100:
                num_results = 100  # API limit is 100 results
            text = tool_parameters.get("text", False)
            
            # Build request payload
            payload = {
                "url": url,
                "numResults": num_results
            }
            
            # Add optional parameters if provided
            if text:
                payload["text"] = True
                
            # Make API request
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            # Print request details for debugging
            print(f"Request URL: https://api.exa.ai/findSimilar")
            print(f"Request Payload: {json.dumps(payload)}")
            
            response = requests.post(
                "https://api.exa.ai/findSimilar",
                json=payload,
                headers=headers
            )
            
            # Log response status
            print(f"Response Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response Error: {response.text}")
                
            response.raise_for_status()
            result_data = response.json()
            
            # Return original JSON response
            yield self.create_json_message(result_data)
            
            # Format and return text response in Markdown
            markdown_response = self._format_results_as_markdown(result_data, url)
            yield self.create_text_message(markdown_response)
            
        except requests.RequestException as e:
            error_message = f"Error when calling Exa Find Similar API: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_message += f" - Status code: {e.response.status_code}"
                if hasattr(e.response, 'text'):
                    error_message += f" - Response: {e.response.text}"
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Error: {error_message}")
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Error: {error_message}")
    
    def _format_results_as_markdown(self, api_response: Dict, query_url: str) -> str:
        """Format API response as a readable Markdown string"""
        results = api_response.get("results", [])
        
        markdown = f"## Exa Similar Links Results\n\n"
        markdown += f"**Query URL:** {query_url}\n\n"
        markdown += f"**Total Results:** {len(results)}\n\n"
        
        if not results:
            markdown += "No similar links found.\n"
            return markdown
        
        # Add results
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            domain = result.get("domain", "Unknown source")
            published_date = result.get("publishedDate", "")
            author = result.get("author", "")
            
            markdown += f"### {i}. [{title}]({url})\n\n"
            markdown += f"**Source:** {domain}\n"
            
            if published_date:
                markdown += f"**Published:** {published_date}\n"
            
            if author:
                markdown += f"**Author:** {author}\n"
            
            if "score" in result:
                markdown += f"**Similarity Score:** {result['score']:.2f}\n"
            
            markdown += "\n"
            
            # Add text content if available
            if "text" in result and result["text"]:
                text_excerpt = result["text"]
                # Limit to ~500 characters for readability
                if len(text_excerpt) > 500:
                    text_excerpt = text_excerpt[:500] + "..."
                
                markdown += "**Content Excerpt:**\n\n"
                markdown += f"```\n{text_excerpt}\n```\n\n"
            
            markdown += "---\n\n"
        
        return markdown
