from collections.abc import Generator
from typing import Any
import requests
import json
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TmdbTvSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for TV shows in TMDB
        """
        # Get parameters
        query = tool_parameters.get("query")
        language = tool_parameters.get("language", "en-US")
        first_air_date_year = tool_parameters.get("first_air_date_year")
        results_limit = min(int(tool_parameters.get("results_limit", 5)), 20)
        
        # Validate required parameters
        if not query:
            yield self.create_text_message("Please provide a TV show title or keywords to search")
            return
            
        # Check API key
        if "api_key" not in self.runtime.credentials or not self.runtime.credentials.get("api_key"):
            yield self.create_text_message("TMDB API Key is required")
            return
            
        try:
            # Prepare API request
            api_key = self.runtime.credentials.get("api_key")
            base_url = "https://api.themoviedb.org/3"
            search_endpoint = f"{base_url}/search/tv"
            
            # Prepare request headers with Bearer token
            headers = {
                'Authorization': f'Bearer {api_key}',
                'accept': 'application/json'
            }
            
            # Build query parameters
            params = {
                "query": query,
                "language": language,
                "page": 1,
                "include_adult": False
            }
            
            # Add year filter if provided
            if first_air_date_year:
                params["first_air_date_year"] = int(first_air_date_year)
                
            # Make API request
            response = requests.get(search_endpoint, params=params, headers=headers)
            
            # Handle API response
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    yield self.create_text_message(f"No TV shows found matching '{query}'")
                    return
                    
                # Limit results
                results = results[:results_limit]
                
                # Format results
                formatted_results = []
                image_base_url = "https://image.tmdb.org/t/p/w500"
                
                for tv_show in results:
                    formatted_tv_show = {
                        "id": tv_show.get("id"),
                        "name": tv_show.get("name"),
                        "original_name": tv_show.get("original_name"),
                        "overview": tv_show.get("overview"),
                        "first_air_date": tv_show.get("first_air_date"),
                        "vote_average": tv_show.get("vote_average"),
                        "vote_count": tv_show.get("vote_count"),
                        "popularity": tv_show.get("popularity"),
                        "poster_path": f"{image_base_url}{tv_show.get('poster_path')}" if tv_show.get("poster_path") else None,
                        "backdrop_path": f"{image_base_url}{tv_show.get('backdrop_path')}" if tv_show.get("backdrop_path") else None,
                        "genre_ids": tv_show.get("genre_ids"),
                        "origin_country": tv_show.get("origin_country"),
                        "tmdb_url": f"https://www.themoviedb.org/tv/{tv_show.get('id')}"
                    }
                    formatted_results.append(formatted_tv_show)
                
                # Return JSON response
                yield self.create_json_message({
                    "total_results": data.get("total_results"),
                    "results_shown": len(formatted_results),
                    "results": formatted_results
                })
            else:
                error_message = f"Error searching for TV shows: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        if "status_message" in error_data:
                            error_message = f"Error: {error_data['status_message']}"
                    except:
                        pass
                yield self.create_text_message(error_message)
                
        except Exception as e:
            yield self.create_text_message(f"Error searching for TV shows: {str(e)}") 