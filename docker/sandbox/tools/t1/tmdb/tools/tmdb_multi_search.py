from collections.abc import Generator
from typing import Any
import requests
import json
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TmdbMultiSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for movies, TV shows, and people in TMDB
        """
        # Get parameters
        query = tool_parameters.get("query")
        language = tool_parameters.get("language", "en-US")
        include_adult = tool_parameters.get("include_adult", False)
        results_limit = min(int(tool_parameters.get("results_limit", 10)), 20)
        
        # Validate required parameters
        if not query:
            yield self.create_text_message("Please provide keywords to search")
            return
            
        # Check API key
        if "api_key" not in self.runtime.credentials or not self.runtime.credentials.get("api_key"):
            yield self.create_text_message("TMDB API Key is required")
            return
            
        try:
            # Prepare API request
            api_key = self.runtime.credentials.get("api_key")
            base_url = "https://api.themoviedb.org/3"
            search_endpoint = f"{base_url}/search/multi"
            
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
                "include_adult": include_adult
            }
                
            # Make API request
            response = requests.get(search_endpoint, params=params, headers=headers)
            
            # Handle API response
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    yield self.create_text_message(f"No results found matching '{query}'")
                    return
                    
                # Limit results
                results = results[:results_limit]
                
                # Format results
                formatted_results = []
                image_base_url = "https://image.tmdb.org/t/p/w500"
                
                for item in results:
                    media_type = item.get("media_type")
                    
                    # Common fields
                    formatted_item = {
                        "id": item.get("id"),
                        "media_type": media_type,
                        "popularity": item.get("popularity"),
                    }
                    
                    # Movie specific fields
                    if media_type == "movie":
                        formatted_item.update({
                            "title": item.get("title"),
                            "original_title": item.get("original_title"),
                            "overview": item.get("overview"),
                            "release_date": item.get("release_date"),
                            "vote_average": item.get("vote_average"),
                            "vote_count": item.get("vote_count"),
                            "poster_path": f"{image_base_url}{item.get('poster_path')}" if item.get("poster_path") else None,
                            "backdrop_path": f"{image_base_url}{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
                            "adult": item.get("adult"),
                            "genre_ids": item.get("genre_ids"),
                            "tmdb_url": f"https://www.themoviedb.org/movie/{item.get('id')}"
                        })
                    
                    # TV show specific fields
                    elif media_type == "tv":
                        formatted_item.update({
                            "name": item.get("name"),
                            "original_name": item.get("original_name"),
                            "overview": item.get("overview"),
                            "first_air_date": item.get("first_air_date"),
                            "vote_average": item.get("vote_average"),
                            "vote_count": item.get("vote_count"),
                            "poster_path": f"{image_base_url}{item.get('poster_path')}" if item.get("poster_path") else None,
                            "backdrop_path": f"{image_base_url}{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
                            "genre_ids": item.get("genre_ids"),
                            "origin_country": item.get("origin_country"),
                            "tmdb_url": f"https://www.themoviedb.org/tv/{item.get('id')}"
                        })
                    
                    # Person specific fields
                    elif media_type == "person":
                        known_for = []
                        for known_item in item.get("known_for", []):
                            known_media_type = known_item.get("media_type")
                            known_title = known_item.get("title") if known_media_type == "movie" else known_item.get("name")
                            known_for.append({
                                "id": known_item.get("id"),
                                "media_type": known_media_type,
                                "title": known_title,
                                "tmdb_url": f"https://www.themoviedb.org/{known_media_type}/{known_item.get('id')}"
                            })
                        
                        formatted_item.update({
                            "name": item.get("name"),
                            "profile_path": f"{image_base_url}{item.get('profile_path')}" if item.get("profile_path") else None,
                            "adult": item.get("adult"),
                            "known_for": known_for,
                            "known_for_department": item.get("known_for_department"),
                            "tmdb_url": f"https://www.themoviedb.org/person/{item.get('id')}"
                        })
                    
                    formatted_results.append(formatted_item)
                
                # Return JSON response
                yield self.create_json_message({
                    "total_results": data.get("total_results"),
                    "results_shown": len(formatted_results),
                    "results": formatted_results
                })
            else:
                error_message = f"Error searching TMDB: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        if "status_message" in error_data:
                            error_message = f"Error: {error_data['status_message']}"
                    except:
                        pass
                yield self.create_text_message(error_message)
                
        except Exception as e:
            yield self.create_text_message(f"Error searching TMDB: {str(e)}") 