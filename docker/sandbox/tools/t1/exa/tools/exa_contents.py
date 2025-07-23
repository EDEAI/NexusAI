from collections.abc import Generator
from typing import Any, Dict, List, Optional
import requests
import json
import os
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ExaContentsTool(Tool):
    # Class attribute to store credentials
    _shared_credentials = {}
    
    @classmethod
    def from_credentials(cls, credentials: Dict[str, Any], runtime: Optional[Any] = None, session: Optional[Any] = None):
        """Create a tool instance with the given credentials"""
        instance = cls()
        # Store credentials in class attribute
        ExaContentsTool._shared_credentials = credentials
        if runtime:
            instance.runtime = runtime
        if session:
            instance.session = session
        return instance
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute a request to get content from URLs using the Exa API.
        
        Args:
            tool_parameters: Dictionary containing:
                - urls: List of URLs to fetch content from (required)
                - livecrawl: Live crawling strategy (never/fallback/always/auto)
                - full_page_text: Whether to include full webpage text
                - ai_page_summary: Whether to include AI-generated summary
                - number_of_subpages: Number of subpages to include
                - return_links: Number of links to return
        
        Returns:
            Generator yielding ToolInvokeMessage with content results
        """
        try:
            # Get API key from runtime credentials
            api_key = self.runtime.credentials["exa_api_key"]
            
            # Get required parameters
            urls_param = tool_parameters.get("urls", "")
            if not urls_param:
                raise ValueError("URLs parameter is required")
            
            # Process urls parameter - support multiple input formats
            urls = []
            
            # Print debug information
            print(f"Original URLs parameter: {urls_param} (type: {type(urls_param).__name__})")
            
            # If already in list format, use directly
            if isinstance(urls_param, list):
                urls = urls_param
            # If in JSON string format of an array, parse it
            elif isinstance(urls_param, str) and urls_param.strip().startswith("[") and urls_param.strip().endswith("]"):
                try:
                    urls = json.loads(urls_param)
                except json.JSONDecodeError:
                    # If parsing fails, treat as a string with separators
                    urls = self._parse_urls_string(urls_param)
            # Otherwise, treat as a string with separators
            elif isinstance(urls_param, str):
                urls = self._parse_urls_string(urls_param)
            else:
                # Unknown type, try to convert to string then split
                try:
                    urls = [str(urls_param).strip()]
                except Exception as e:
                    print(f"URLs parameter conversion error: {str(e)}")
                    raise ValueError(f"Cannot process URLs parameter: {urls_param}")
            
            # Ensure urls is a non-empty list
            if not urls:
                raise ValueError("No valid URLs provided")
            
            # Ensure no empty strings in URLs
            urls = [url for url in urls if url.strip()]
            if not urls:
                raise ValueError("No valid URLs after filtering")
                
            print(f"Processed URLs: {urls}")
            
            # Get optional parameters
            livecrawl_strategy = tool_parameters.get("livecrawl", "auto")  # Default to auto for better results
            full_page_text = tool_parameters.get("full_page_text", False)
            ai_page_summary = tool_parameters.get("ai_page_summary", False)
            number_of_subpages = int(tool_parameters.get("number_of_subpages", 1))
            return_links = int(tool_parameters.get("return_links", 1))
            
            # Prepare API request - modify to match exa_search.py header format
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            # New request format
            payload = {
                "ids": urls,  # Use ids field instead of urls, ensure it's in list format
                "livecrawl": livecrawl_strategy
            }
            
            # Print debug information
            print(f"Request payload: {json.dumps(payload)}")
            
            # Add conditional parameters
            if full_page_text:
                payload["text"] = True
                
            if ai_page_summary:
                payload["summary"] = True
                
            if number_of_subpages > 0:
                payload["subpages"] = number_of_subpages
                
            if return_links > 0:
                payload["extras"] = {"links": return_links}
            
            # Make API request
            response = requests.post(
                "https://api.exa.ai/contents",
                json=payload,
                headers=headers
            )
            
            # Log the request
            if response.status_code == 200:
                print("API request successful")
            else:
                print(f"API request failed, status code: {response.status_code}")
            
            # View API response
            print(f"API response: {response.text}")
            response.raise_for_status()
            result_data = response.json()
            
            # Return JSON response
            yield self.create_json_message(result_data)
            
            # Format response and return in Markdown format
            markdown_response = self._format_results_as_markdown(result_data, urls)
            yield self.create_text_message(markdown_response)
            
        except KeyError:
            # Return mock results if API key is not found
            yield self.create_text_message("API key not found. This is a mock implementation.")
            yield self.create_json_message({"status": "mock", "message": "Using mock data instead of actual API"})
            return
        except requests.RequestException as e:
            error_message = f"Error when calling Exa Contents API: {str(e)}"
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
            print(f"Handling exception: {error_message}")
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Error: {error_message}")
    
    def _parse_urls_string(self, urls_string: str) -> List[str]:
        """
        Parse a string containing multiple URLs, supporting various separators
        Supports English comma, Chinese comma, space, semicolon, etc. as separators
        """
        # Remove leading and trailing square brackets (if any)
        cleaned_string = urls_string.strip()
        if cleaned_string.startswith('['):
            cleaned_string = cleaned_string[1:]
        if cleaned_string.endswith(']'):
            cleaned_string = cleaned_string[:-1]
            
        # Use regular expression to split the string, supporting multiple separators
        # Separators include: English comma, Chinese comma, space, semicolon;
        split_urls = re.split(r'[,，\s;]+', cleaned_string)
        
        # Clean each URL, removing possible quotes
        clean_urls = []
        for url in split_urls:
            url = url.strip(' \'"')
            if url:  # Ensure not adding empty strings
                # Ensure URL is valid
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                clean_urls.append(url)
                
        return clean_urls
    
    def _format_results_as_markdown(self, api_response: Dict, urls: List[str]) -> str:
        """Format API response as a readable Markdown string"""
        if not api_response or "results" not in api_response:
            return "No content data available."
        
        markdown = f"## Exa Content Extraction Results\n\n"
        
        results = api_response.get("results", {})
        for url in urls:
            if url not in results:
                markdown += f"### URL: {url}\n\nNo data available for this URL.\n\n---\n\n"
                continue
                
            url_data = results[url]
            markdown += f"### URL: [{url}]({url})\n\n"
            
            # Add title (if any)
            if "title" in url_data:
                markdown += f"**Title:** {url_data['title']}\n\n"
            
            # Add summary (if any)
            if "summary" in url_data and url_data["summary"]:
                markdown += f"**Summary:**\n\n{url_data['summary']}\n\n"
            
            # Add links (if any)
            if "links" in url_data and url_data["links"]:
                markdown += "**Links:**\n\n"
                for link in url_data["links"]:
                    link_url = link.get("url", "")
                    link_title = link.get("title", link_url)
                    markdown += f"- [{link_title}]({link_url})\n"
                markdown += "\n"
            
            # Add text content (if any)
            if "text" in url_data and url_data["text"]:
                text_preview = url_data["text"]
                # Limit content length for better readability
                if len(text_preview) > 1000:
                    text_preview = text_preview[:1000] + "...\n(content truncated for readability)"
                
                markdown += "**Content:**\n\n```\n"
                markdown += text_preview
                markdown += "\n```\n\n"
            
            # Add subpage results (if any)
            if "subpages" in url_data and url_data["subpages"]:
                markdown += "**Subpages:**\n\n"
                
                for subpage in url_data["subpages"]:
                    subpage_url = subpage.get("url", "")
                    subpage_title = subpage.get("title", subpage_url)
                    
                    markdown += f"#### [{subpage_title}]({subpage_url})\n\n"
                    
                    if "summary" in subpage and subpage["summary"]:
                        markdown += f"**Summary:** {subpage['summary']}\n\n"
                    
                    if "text" in subpage and subpage["text"]:
                        text_preview = subpage["text"]
                        if len(text_preview) > 500:
                            text_preview = text_preview[:500] + "..."
                        
                        markdown += f"**Content Preview:**\n\n```\n{text_preview}\n```\n\n"
            
            markdown += "---\n\n"
        
        return markdown
