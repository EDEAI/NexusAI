from collections.abc import Generator
from typing import Any
import requests
import json
from urllib.parse import quote

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TmdbMovieSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for movies in TMDB
        """
        # Get parameters
        query = tool_parameters.get("query")
        language = tool_parameters.get("language", "en-US")
        year = tool_parameters.get("year")
        results_limit = min(int(tool_parameters.get("results_limit", 5)), 20)
        
        # Validate required parameters
        if not query:
            yield self.create_text_message("Please provide a movie title or keywords to search")
            return
            
        # Check API key
        if "api_key" not in self.runtime.credentials or not self.runtime.credentials.get("api_key"):
            yield self.create_text_message("TMDB API Key is required")
            return
            
        try:
            # Prepare API request
            api_key = self.runtime.credentials.get("api_key")
            base_url = "https://api.themoviedb.org/3"
            search_endpoint = f"{base_url}/search/movie"
            
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
            if year:
                params["year"] = int(year)
                
            # Make API request
            response = requests.get(search_endpoint, params=params, headers=headers)
            
            # Handle API response
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if not results:
                    yield self.create_text_message(f"No movies found matching '{query}'")
                    return
                    
                # Limit results
                results = results[:results_limit]
                
                # Format results
                formatted_results = []
                image_base_url = "https://image.tmdb.org/t/p/w500"
                
                for movie in results:
                    formatted_movie = {
                        "id": movie.get("id"),
                        "title": movie.get("title"),
                        "original_title": movie.get("original_title"),
                        "overview": movie.get("overview"),
                        "release_date": movie.get("release_date"),
                        "vote_average": movie.get("vote_average"),
                        "vote_count": movie.get("vote_count"),
                        "popularity": movie.get("popularity"),
                        "poster_path": f"{image_base_url}{movie.get('poster_path')}" if movie.get("poster_path") else None,
                        "backdrop_path": f"{image_base_url}{movie.get('backdrop_path')}" if movie.get("backdrop_path") else None,
                        "adult": movie.get("adult"),
                        "genre_ids": movie.get("genre_ids"),
                        "tmdb_url": f"https://www.themoviedb.org/movie/{movie.get('id')}"
                    }
                    formatted_results.append(formatted_movie)
                
                # Return JSON response
                yield self.create_json_message({
                    "total_results": data.get("total_results"),
                    "results_shown": len(formatted_results),
                    "results": formatted_results
                })
            else:
                error_message = f"Error searching for movies: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        if "status_message" in error_data:
                            error_message = f"Error: {error_data['status_message']}"
                    except:
                        pass
                yield self.create_text_message(error_message)
                
        except Exception as e:
            yield self.create_text_message(f"Error searching for movies: {str(e)}") 