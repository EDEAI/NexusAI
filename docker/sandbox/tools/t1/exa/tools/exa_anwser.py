from collections.abc import Generator
from typing import Any, Dict, List, Optional
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ExaAnswerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Generate an answer to a query using the Exa AI Answer API.
        
        Args:
            tool_parameters: Dictionary containing:
                - query: The question or query to answer (required)
                - text: Whether to include full text of the results (default: False)
                - model: Model to use for answering (default: 'exa')
        
        Returns:
            Generator yielding ToolInvokeMessage with generated answer and sources
        """
        try:
            # Get API key from runtime credentials
            api_key = self.runtime.credentials["exa_api_key"]
            
            # Required parameter
            query = tool_parameters.get("query")
            if not query:
                raise ValueError("Query is required")
                
            # Optional parameters with defaults
            text = tool_parameters.get("text", False)
            model = tool_parameters.get("model", "exa")
            
            # Build request payload
            payload = {
                "query": query,
                "text": text
            }
            
            # Add optional model parameter if not default
            if model != "exa":
                payload["model"] = model
                
            # Make API request using Authorization Bearer format
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Print request details for debugging
            print(f"Request URL: https://api.exa.ai/answer")
            print(f"Request Payload: {json.dumps(payload)}")
            
            response = requests.post(
                "https://api.exa.ai/answer",
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
            markdown_response = self._format_results_as_markdown(result_data, query)
            yield self.create_text_message(markdown_response)
            
        except requests.RequestException as e:
            error_message = f"Error when calling Exa Answer API: {str(e)}"
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
    
    def _format_results_as_markdown(self, api_response: Dict, query: str) -> str:
        """Format API response as a readable Markdown string"""
        answer = api_response.get("answer", "No answer provided.")
        sources = api_response.get("sources", [])
        
        markdown = f"## Exa Answer Results\n\n"
        markdown += f"**Query:** {query}\n\n"
        
        # Add the answer
        markdown += f"### Answer\n\n{answer}\n\n"
        
        # Add sources if available
        if sources:
            markdown += f"### Sources ({len(sources)})\n\n"
            
            for i, source in enumerate(sources, 1):
                title = source.get("title", "No title")
                url = source.get("url", "")
                author = source.get("author", "")
                published_date = source.get("publishedDate", "")
                
                markdown += f"**{i}. [{title}]({url})**\n\n"
                
                if author:
                    markdown += f"Author: {author}\n\n"
                
                if published_date:
                    markdown += f"Published: {published_date}\n\n"
                
                # Add text content if available
                if "text" in source and source["text"]:
                    text_excerpt = source["text"]
                    # Limit to ~300 characters for readability
                    if len(text_excerpt) > 300:
                        text_excerpt = text_excerpt[:300] + "..."
                    
                    markdown += f"```\n{text_excerpt}\n```\n\n"
                
                markdown += "---\n\n"
        else:
            markdown += "No sources provided.\n\n"
        
        return markdown
