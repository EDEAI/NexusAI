"""Tool for batch updating data in Google Sheets."""

from collections.abc import Generator
from typing import Any
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from .utils.google_service import get_sheets_service, handle_google_api_error


class BatchUpdateTool(Tool):
    """Tool for updating data in multiple ranges in a Google Sheet."""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Invoke the batch update operation.
        
        Args:
            tool_parameters: The parameters for the tool
                spreadsheet_id: The ID of the spreadsheet
                data: A list of objects, each containing 'range' and 'values' keys
                      (either as a JSON string or already parsed)
                value_input_option: How the input data should be interpreted
                include_values_in_response: Whether to include the values in the response
                response_value_render_option: How the values in the response should be rendered
                response_date_time_render_option: How dates, times, and durations in the response should be rendered
                
        Yields:
            Either a success message with the update results or an error message
        """
        # Extract parameters
        spreadsheet_id = tool_parameters.get('spreadsheet_id')
        data_param = tool_parameters.get('data')
        value_input_option = tool_parameters.get('value_input_option', 'USER_ENTERED')
        include_values_in_response = tool_parameters.get('include_values_in_response', False)
        response_value_render_option = tool_parameters.get('response_value_render_option')
        response_date_time_render_option = tool_parameters.get('response_date_time_render_option')
        
        if not spreadsheet_id:
            yield self.create_text_message("Missing required parameter: spreadsheet_id")
            return
            
        if not data_param:
            yield self.create_text_message("Missing required parameter: data")
            return
            
        try:
            # Parse data if it's a string
            if isinstance(data_param, str):
                try:
                    data = json.loads(data_param)
                except json.JSONDecodeError:
                    yield self.create_text_message("Invalid JSON format for data. Please provide a valid JSON array.")
                    return
            else:
                data = data_param
                
            # Validate data format
            if not isinstance(data, list):
                yield self.create_text_message("Data must be a list of objects, each with 'range' and 'values' keys")
                return
            
            # Get credentials from provider
            creds = self.runtime.credentials.get('credentials_json')
            creds_json = json.loads(creds)
            
            # Build service
            service = get_sheets_service(creds_json)
            
            # Prepare data for batch update
            batch_update_values_request_body = {
                'valueInputOption': value_input_option,
                'data': []
            }
            
            # Add optional parameters
            if include_values_in_response:
                batch_update_values_request_body['includeValuesInResponse'] = include_values_in_response
                
            if response_value_render_option:
                batch_update_values_request_body['responseValueRenderOption'] = response_value_render_option
                
            if response_date_time_render_option:
                batch_update_values_request_body['responseDateTimeRenderOption'] = response_date_time_render_option
            
            # Process the data items
            for item in data:
                if 'range' not in item or 'values' not in item:
                    yield self.create_text_message("Each data item must contain 'range' and 'values' keys")
                    return
                    
                batch_update_values_request_body['data'].append({
                    'range': item['range'],
                    'values': item['values']
                })
            
            # Execute batch update
            result = service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=batch_update_values_request_body
            ).execute()
            
            # Return result
            yield self.create_json_message(result)
            
        except Exception as e:
            error_message = handle_google_api_error(e)
            yield self.create_text_message(error_message) 