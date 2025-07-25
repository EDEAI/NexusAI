from collections.abc import Generator
from typing import Any, Mapping
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GoogleBooksExplorerTool(Tool):
    """
    A Dify Tool Plugin to research book information (title, authors, description, preview link)
    by integrating with the Google Books API.
    """

    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the Google Books API to retrieve book information.

        Args:
            tool_parameters (Mapping[str, Any]): A dictionary containing the tool's input parameters.
                Expected keys:
                - "query" (str): The search query (e.g., 'harry potter', 'machine learning'). (required)
                - "max_results" (int, optional): The maximum number of results to return.
                                                 Defaults to 10. Max is 40 as per API.

        Yields:
            ToolInvokeMessage: A JSON message containing the book information.
            ToolInvokeMessage: Text messages for progress or errors.
        """
        query = tool_parameters.get("query")
        # Use .get() with a default for optional parameters
        max_results = tool_parameters.get("max_results", 10) 
        max_results = int(max_results)  # Ensure max_results is an integer
        if not query:
            yield self.create_text_message("Error: Missing required parameter 'query'. Please provide a search term for books.")
            return

        # Ensure max_results is an integer and within the valid range
        if not isinstance(max_results, int) or not (1 <= max_results <= 40):
            yield self.create_text_message("Error: Invalid 'max_results'. It must be an integer between 1 and 40.")
            return

        # Retrieve Google Books API key from Dify credentials.
        # The key name 'google_books_api_key' must match the 'name' defined in api.yaml under 'credentials'.
        google_books_api_key = self.runtime.credentials.get("google_books_api_key")

        if not google_books_api_key:
            yield self.create_text_message("Error: Google Books API key is not configured. Please set 'google_books_api_key' in plugin credentials in Dify.")
            return

        yield self.create_text_message(f"Searching Google Books for '{query}' with {max_results} results...")

        base_url = "https://www.googleapis.com/books/v1"
        endpoint = f"{base_url}/volumes"
        params = {
            "q": query,
            "maxResults": max_results,
            "key": google_books_api_key # API key is passed as a query parameter
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            book_data = response.json()

            items = book_data.get("items", [])
            
            # Process and format the results to be more concise and useful for Dify's output
            results_list = []
            if items:
                for item in items:
                    volume_info = item.get("volumeInfo", {})
                    title = volume_info.get("title", "N/A")
                    authors = ", ".join(volume_info.get("authors", ["N/A"]))
                    published_date = volume_info.get("publishedDate", "N/A")
                    # Truncate description if it's too long
                    description = volume_info.get("description", "No description available.")
                    if len(description) > 300:
                        description = description[:300] + "..."
                    preview_link = volume_info.get("previewLink", "N/A")

                    results_list.append({
                        "title": title,
                        "authors": authors,
                        "published_date": published_date,
                        "description": description,
                        "preview_link": preview_link
                    })
            
            if results_list:
                # Yield the structured JSON message with the books found
                yield self.create_json_message({"books_found": results_list})
                yield self.create_text_message(f"Successfully retrieved information for {len(results_list)} book(s) related to '{query}'.")
            else:
                yield self.create_text_message(f"No books found for '{query}'. Please try a different search term or broaden your query.")

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (e.g., 400 Bad Request, 403 Forbidden - often due to invalid API key)
            yield self.create_text_message(f"Error from Google Books API: {e.response.status_code} - {e.response.text}. Please check your API key or the query parameters.")
        except requests.exceptions.RequestException as e:
            # Handle general request errors (e.g., network issues, DNS problems)
            yield self.create_text_message(f"Network error when connecting to Google Books API: {e}. Please check your internet connection or API endpoint.")
        except Exception as e:
            # Catch any other unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during Google Books research: {e}.")

