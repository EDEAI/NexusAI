from collections.abc import Generator
from typing import Any
import requests
import re
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class BitlyShortnerTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Unified Bitly tool that can either shorten URLs or get analytics
        """
        # Get access token from Dify credentials
        access_token = self.runtime.credentials.get("access_token")
        url_or_bitlink = tool_parameters.get("url_or_bitlink", "")
        domain = tool_parameters.get("domain", "bit.ly")
        group_guid = tool_parameters.get("group_guid", "")
        title = tool_parameters.get("title", "")
        unit = tool_parameters.get("unit", "day")
        units = tool_parameters.get("units", -1)
        
        # Validate parameters
        if not access_token:
            yield self.create_text_message("Bitly access token is required. Please set it in the plugin credentials.")
            return
        if not url_or_bitlink:
            yield self.create_text_message("URL or Bitly link is required.")
            return
        # Determine if input is a Bitly link or a long URL
        if self._is_bitly_link(url_or_bitlink):
            # Get analytics for Bitly link
            yield from self._get_analytics(url_or_bitlink, unit, units, access_token)
        else:
            # Shorten the URL
            yield from self._shorten_url(url_or_bitlink, domain, group_guid, title, access_token)
    
    def _is_bitly_link(self, url: str) -> bool:
        """
        Check if the URL is a Bitly link
        """
        # Common Bitly domains and patterns
        bitly_patterns = [
            r'^https?://bit\.ly/',
            r'^https?://[a-zA-Z0-9-]+\.ly/',
            r'^bit\.ly/',
            r'^[a-zA-Z0-9-]+\.ly/'
        ]
        
        for pattern in bitly_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def _shorten_url(self, long_url: str, domain: str, group_guid: str, title: str, access_token: str) -> Generator[ToolInvokeMessage, None, None]:
        """
        Shorten a long URL using Bitly API
        """
        try:
            # Prepare request data
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "long_url": long_url,
                "domain": domain
            }
            
            # Add optional parameters if provided
            if group_guid:
                data["group_guid"] = group_guid
            if title:
                data["title"] = title
                
            # Make API request to shorten URL
            response = requests.post(
                "https://api-ssl.bitly.com/v4/shorten",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Create response summary
                summary = f"URL shortened successfully: {result.get('link', 'N/A')}"
                yield self.create_text_message(summary)
                
                # Return detailed response
                yield self.create_json_message({
                    "action": "shorten",
                    "shortened_url": result.get("link"),
                    "id": result.get("id"),
                    "long_url": result.get("long_url"),
                    "created_at": result.get("created_at"),
                    "title": result.get("title"),
                    "archived": result.get("archived")
                })
                
            elif response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get("message", "Bad request")
                yield self.create_text_message(f"Error shortening URL: {error_message}")
                
            elif response.status_code == 401:
                yield self.create_text_message("Invalid Bitly access token. Please check your access token.")
                
            elif response.status_code == 403:
                yield self.create_text_message("Access denied. Please check your Bitly account permissions.")
                
            else:
                yield self.create_text_message(f"Error shortening URL: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
    
    def _get_analytics(self, bitlink: str, unit: str, units: int, access_token: str) -> Generator[ToolInvokeMessage, None, None]:
        """
        Get analytics for a Bitly link
        """
        try:
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get total clicks summary
            summary_url = f"https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary"
            summary_params = {
                "unit": unit,
                "units": units
            }
            
            summary_response = requests.get(summary_url, headers=headers, params=summary_params)
            
            if summary_response.status_code == 200:
                summary_data = summary_response.json()
                
                # Get geographic distribution
                countries_url = f"https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/countries"
                countries_params = {
                    "unit": unit,
                    "units": units,
                    "size": 10  # Top 10 countries
                }
                
                countries_response = requests.get(countries_url, headers=headers, params=countries_params)
                
                analytics_result = {
                    "action": "analytics",
                    "bitlink": bitlink,
                    "total_clicks": summary_data.get("total_clicks", 0),
                    "time_unit": summary_data.get("unit", unit),
                    "time_units": summary_data.get("units", units),
                    "unit_reference": summary_data.get("unit_reference")
                }
                
                # Add geographic data if available
                if countries_response.status_code == 200:
                    countries_data = countries_response.json()
                    analytics_result["geographic_distribution"] = countries_data.get("metrics", [])
                else:
                    analytics_result["geographic_distribution"] = []
                
                # Create response summary
                total_clicks = analytics_result["total_clicks"]
                summary = f"Analytics for {bitlink}: {total_clicks} total clicks"
                yield self.create_text_message(summary)
                
                # Return detailed analytics
                yield self.create_json_message(analytics_result)
                
            elif summary_response.status_code == 400:
                error_data = summary_response.json()
                error_message = error_data.get("message", "Bad request")
                yield self.create_text_message(f"Error getting analytics: {error_message}")
                
            elif summary_response.status_code == 401:
                yield self.create_text_message("Invalid Bitly access token. Please check your access token.")
                
            elif summary_response.status_code == 403:
                yield self.create_text_message("Access denied. Please check your Bitly account permissions.")
                
            elif summary_response.status_code == 404:
                yield self.create_text_message(f"Bitly link not found: {bitlink}")
                
            else:
                yield self.create_text_message(f"Error getting analytics: HTTP {summary_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
