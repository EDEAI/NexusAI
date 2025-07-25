"""Tool for batch getting data from Google Sheets."""

from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .utils.google_service import get_sheets_service, handle_google_api_error


class BatchGetTool(Tool):
    """Tool for retrieving data from multiple ranges in a Google Sheet."""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Invoke the batch get operation.
        
        Args:
            tool_parameters: The parameters for the tool
                spreadsheet_id: The ID of the spreadsheet
                ranges: A list of ranges to retrieve as a JSON string
                date_time_render_option: How dates, times, and durations should be represented
                major_dimension: The major dimension that results should use
                value_render_option: How values should be represented in the output
                
        Yields:
            Either a success message with the retrieved data or an error message
        """
        # Extract parameters
        spreadsheet_id = tool_parameters.get('spreadsheet_id')
        ranges_str = tool_parameters.get('ranges', '[]')
        date_time_render_option = tool_parameters.get('date_time_render_option')
        major_dimension = tool_parameters.get('major_dimension')
        value_render_option = tool_parameters.get('value_render_option')

        if not spreadsheet_id:
            yield self.create_text_message("Missing required parameter: spreadsheet_id")
            return
        
        try:
            # Parse the ranges string as JSON
            if isinstance(ranges_str, str):
                try:
                    ranges = json.loads(ranges_str)
                except json.JSONDecodeError:
                    yield self.create_text_message("Invalid JSON format for ranges. Please provide a valid JSON array.")
                    return
            else:
                ranges = ranges_str
            
            # Validate ranges
            if not isinstance(ranges, list):
                yield self.create_text_message("Ranges must be a list of strings in JSON format")
                return
                
            if not ranges:
                yield self.create_text_message("Missing required parameter: ranges")
                return
            
            # Get credentials
            creds = self.runtime.credentials.get('credentials_json')
            creds_json = json.loads(creds)
            
            # Build service
            service = get_sheets_service(creds_json)
            
            # Prepare parameters for batch get
            params = {
                'spreadsheetId': spreadsheet_id,
                'ranges': ranges
            }
            
            # Add optional parameters if provided
            if date_time_render_option:
                params['dateTimeRenderOption'] = date_time_render_option
            
            if major_dimension:
                params['majorDimension'] = major_dimension
            
            if value_render_option:
                params['valueRenderOption'] = value_render_option
            
            # Execute batch get
            result = service.spreadsheets().values().batchGet(**params).execute()
            
            # Return result
            yield self.create_json_message(result)
            
        except json.JSONDecodeError:
            yield self.create_text_message("Invalid JSON format for ranges. Please provide a valid JSON array.")
        except Exception as e:
            error_message = handle_google_api_error(e)
            yield self.create_text_message(error_message) 