from collections.abc import Generator
from typing import Any, Dict, List, Optional
import os
import requests
from datetime import datetime
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ExaSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute a search using the Exa Search API.
        
        Args:
            tool_parameters: Dictionary containing:
                - query: The search query string (required)
                - search_type: "neural", "keyword", or "auto" (default: neural)
                - num_results: Maximum number of results to return (default: 10)
                - include_domains: Comma-separated list of domains to include
                - exclude_domains: Comma-separated list of domains to exclude
                - start_published_date: Start date for filtering results (YYYY-MM-DD)
                - end_published_date: End date for filtering results (YYYY-MM-DD)
                - use_autoprompt: Whether to use Exa's query enhancement (default: True)
                - text_contents: Whether to include full text of results (default: False)
                - highlight_results: Whether to highlight relevant snippets (default: False)
                - category: Filter results by category
                - includeText: Text that must be present in results
                - excludeText: Text that must not be present in results
        
        Returns:
            Generator yielding ToolInvokeMessage with search results (both JSON and text formats)
        """
        try:
            # Get API key from runtime credentials
            api_key = self.runtime.credentials["exa_api_key"]
            
            # Required parameter
            query = tool_parameters.get("query")
            if not query:
                raise ValueError("Search query is required")
                
            # Optional parameters with defaults
            search_type = tool_parameters.get("search_type", "neural")
            num_results = int(tool_parameters.get("num_results", 10))
            include_domains = tool_parameters.get("include_domains", "")
            exclude_domains = tool_parameters.get("exclude_domains", "")
            start_published_date = tool_parameters.get("start_published_date", "")
            end_published_date = tool_parameters.get("end_published_date", "")
            use_autoprompt = tool_parameters.get("use_autoprompt", True)
            text_contents = tool_parameters.get("text_contents", True)
            highlight_results = tool_parameters.get("highlight_results", False)
            category = tool_parameters.get("category", None)
            include_text = tool_parameters.get("includeText", None)
            exclude_text = tool_parameters.get("excludeText", None)
            
            # Process domain lists
            include_domains_list = [d.strip() for d in include_domains.split(",")] if include_domains else []
            exclude_domains_list = [d.strip() for d in exclude_domains.split(",")] if exclude_domains else []
            
            # Build request payload
            payload: Dict[str, Any] = {
                "query": query,
                "numResults": num_results,
                "useAutoprompt": use_autoprompt,
                "type": search_type if search_type != "auto" else None,
                "includeDomains": include_domains_list if include_domains_list else None,
                "excludeDomains": exclude_domains_list if exclude_domains_list else None,
                "startPublishedDate": start_published_date if start_published_date else None,
                "endPublishedDate": end_published_date if end_published_date else None,
                "category": category,
                "includeText": [include_text] if include_text else None,
                "excludeText": [exclude_text] if exclude_text else None
            }
            
            # Remove None values from payload
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Add contents options if needed
            contents_options = {}
            if text_contents:
                contents_options["text"] = True
            if highlight_results:
                contents_options["highlights"] = True
            
            if contents_options:
                payload["contents"] = contents_options
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            print("Payload being sent to Exa API:")
            print(json.dumps(payload, indent=2))
            response = requests.post(
                "https://api.exa.ai/search",
                json=payload,
                headers=headers
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            # Yield the raw JSON response first
            yield self.create_json_message(result_data)

            # Format and yield the results as markdown text
            markdown_output = self._format_results_as_markdown(result_data, query)
            yield self.create_text_message(markdown_output)
            
            # Extract urls and images from results
            urls = []
            images = []
            raw_results = result_data.get("results", [])
            for result in raw_results:
                if url := result.get("url"):
                    urls.append(url)
                # Handle image extraction with proper validation
                if "image" in result:
                    image = result["image"]
                    if isinstance(image, str) and image.strip():  # Ensure non-empty string
                        if image.startswith(('http://', 'https://')):  # Basic URL validation
                            images.append(image)

            # Debug output
            print("\n===== EXTRACTED URLS AND IMAGES =====")
            print("URLs:", urls)
            print("Images:", images)
            print("===== END OF EXTRACTION =====\n")

            # Yield urls and images as separate variables
            yield self.create_variable_message("urls", urls)
            yield self.create_variable_message("images", images)

            # Debug output
            print("\n===== AFTER create_variable_message =====")
            print("Variable 'urls' sent to Dify:")
            print(json.dumps(urls, indent=2))
            print("Variable 'images' sent to Dify:")
            print(json.dumps(images, indent=2))
            print("===== END OF DEBUG OUTPUT =====\n")

        except requests.RequestException as e:
            error_message = f"Error when calling Exa Search API: {str(e)}"
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
        results = api_response.get("results", [])
        
        markdown = f"## Exa Search Results\n\n"
        markdown += f"**Query:** {query}\n\n"
        markdown += f"**Total Results:** {len(results)}\n\n"
        
        if not results:
            markdown += "No results found.\n"
            return markdown
        
        # Add results
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "")
            domain = result.get("domain", "Unknown source")
            published_date = result.get("publishedDate", "")
            author = result.get("author", "")
            
            markdown += f"### {i}. [{title}]({url})\n\n"
            
            # Add image if available
            image_url = result.get("image", "")
            if image_url:
                markdown += f"![Image from {domain}]({image_url})\n\n"
            
            markdown += f"**Source:** {domain}\n"
            
            if published_date:
                markdown += f"**Published:** {published_date}\n"
            
            if author:
                markdown += f"**Author:** {author}\n"
            
            if "score" in result:
                markdown += f"**Relevance Score:** {result['score']:.2f}\n"
            
            markdown += "\n"
            
            # Add highlights if available
            if "highlights" in result and result["highlights"]:
                markdown += "**Highlights:**\n\n"
                for highlight in result["highlights"]:
                    markdown += f"> {highlight}\n"
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
