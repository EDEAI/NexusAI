import json
import logging
import time
from collections.abc import Generator
from typing import Any, List, Dict, Optional, Union

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.dubbo_utils import dubbo_client_utils


class DubboInvokeTool(Tool):
    """Tool for invoking Dubbo services"""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Execute Dubbo service invocation"""
        
        # Get credentials (Dubbo version and timeout configuration)
        # 添加容错处理，如果runtime不存在则使用默认值
        if hasattr(self, 'runtime') and self.runtime and hasattr(self.runtime, 'credentials'):
            credentials = self.runtime.credentials
            dubbo_version = credentials.get("dubbo_version", "2.4.10")
            timeout = int(credentials.get("timeout", "60000"))
        else:
            # 测试环境或runtime不可用时使用默认值
            dubbo_version = "2.4.10"
            timeout = 60000
        
        # Get parameters
        registry_address = tool_parameters.get("registry_address", "")
        service_uri = tool_parameters.get("service_uri", "")
        interface = tool_parameters.get("interface", "")
        method = tool_parameters.get("method", "")
        
        # Get parameter related fields
        parameter_types = tool_parameters.get("parameter_types", None)
        parameter_values = tool_parameters.get("parameter_values", None)
        
        # Validate parameters
        if not interface:
            yield self.create_text_message("Error: Interface name must be provided")
            return
            
        if not method:
            yield self.create_text_message("Error: Method name must be provided")
            return
            
        if not registry_address and not service_uri:
            yield self.create_text_message("Error: Registry address or service URI must be provided")
            return
            
        # If both are provided, use service URI
        if registry_address and service_uri:
            logging.info("Both registry address and service URI provided, service URI will be used with priority")
        
        try:
            # Start timing
            start_time = time.time()
            
            # Process parameters
            param_objects, param_types = self._process_typed_parameters(parameter_types, parameter_values)
            
            # Execute invocation
            if service_uri:
                logging.info(f"Start invoking service: {service_uri}, {interface}.{method}, params: {param_objects}, types: {param_types}, dubbo_version: {dubbo_version}, timeout: {timeout}ms")
                result = dubbo_client_utils.invoke_service(
                    service_uri, interface, method, param_objects, param_types, dubbo_version, timeout
                )
            else:
                logging.info(f"Start invoking service through registry: {registry_address}, {interface}.{method}, params: {param_objects}, types: {param_types}, dubbo_version: {dubbo_version}, timeout: {timeout}ms")
                result = dubbo_client_utils.invoke_with_registry(
                    registry_address, interface, method, param_objects, param_types, dubbo_version, timeout
                )
                
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            logging.info(f"Dubbo service invocation completed, elapsed time: {elapsed_time:.2f} seconds")
            
            # Check if invocation was successful
            if result.get("success", False):
                logging.info("Invocation successful")
                # Return result
                yield self.create_text_message(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                # Invocation failed
                error_message = f"Dubbo service invocation failed: {result.get('message', 'Unknown error')}"
                logging.error(error_message)
                yield self.create_text_message(error_message)
            
        except Exception as e:
            error_message = f"Dubbo service invocation exception: {str(e)}"
            logging.error(error_message, exc_info=True)
            yield self.create_text_message(error_message)
    
    def _process_typed_parameters(
        self, parameter_types: str, parameter_values: str
    ) -> tuple[Any, List[str]]:
        """
        Process typed parameters
        
        Args:
            parameter_types: Parameter types string, comma separated
            parameter_values: Parameter values JSON string
            
        Returns:
            tuple: (processed parameter object, parameter types list)
        """
        # Normalize parameter values: convert empty string or whitespace-only string to None
        if parameter_values is not None and parameter_values.strip() == "":
            parameter_values = None
        
        # Normalize parameter types: convert empty string or whitespace-only string to None
        if parameter_types is not None and parameter_types.strip() == "":
            parameter_types = None
        
        # Handle no-parameter invocation
        if not parameter_types and not parameter_values:
            logging.info("Detected no-parameter invocation")
            return None, []
        
        # If only parameter_types is empty but parameter_values has value, use traditional invocation
        if not parameter_types and parameter_values:
            logging.info("Detected traditional parameter invocation (no type information)")
            try:
                values = json.loads(parameter_values)
                return values, None  # Return None to indicate traditional invocation
            except json.JSONDecodeError as e:
                logging.error(f"Traditional parameter value JSON parsing failed: {e}")
                raise ValueError(f"Parameter values must be in valid JSON format: {e}")
        
        # If only parameter_values is empty but parameter_types has value, this is also an error  
        if parameter_types and not parameter_values:
            raise ValueError("Parameter types provided but parameter values not provided")
        
        # Parse parameter types list - use smart parsing to handle generic types
        types_list = self._parse_parameter_types(parameter_types)
        
        # Parse parameter values
        try:
            values = json.loads(parameter_values)
        except json.JSONDecodeError as e:
            logging.error(f"Parameter value JSON parsing failed: {e}")
            raise ValueError(f"Parameter values must be in valid JSON format: {e}")
        
        # Determine how to handle parameter values based on number of types
        if len(types_list) == 1:
            # Single parameter type
            # Regardless of whether values is an array, treat it as one parameter
            return values, types_list
        else:
            # Multiple parameter types
            if not isinstance(values, list):
                raise ValueError(f"For multi-parameter invocation, parameter_values must be a JSON array")
            
            if len(values) != len(types_list):
                raise ValueError(f"Number of parameter values ({len(values)}) does not match number of parameter types ({len(types_list)})")
            
            return values, types_list
    
    def _parse_parameter_types(self, parameter_types: str) -> List[str]:
        """
        Intelligently parse parameter types string, correctly handle Java types with generics
        
        Args:
            parameter_types: Parameter types string, e.g., "int,Map<String,Integer>,List<User>"
            
        Returns:
            Parsed types list
        """
        if not parameter_types or not parameter_types.strip():
            return []
        
        types_list = []
        current_type = ""
        bracket_count = 0
        
        for char in parameter_types:
            if char == '<':
                bracket_count += 1
                current_type += char
            elif char == '>':
                bracket_count -= 1
                current_type += char
            elif char == ',' and bracket_count == 0:
                # Only when there are no nested angle brackets, comma is a parameter separator
                if current_type.strip():
                    types_list.append(current_type.strip())
                current_type = ""
            else:
                current_type += char
        
        # Add the last type
        if current_type.strip():
            types_list.append(current_type.strip())
        
        return types_list
    
    def _process_legacy_parameters(self, legacy_params: Optional[str]) -> Any:
        """
        Process legacy format parameters
        
        Args:
            legacy_params: Parameter string
            
        Returns:
            Processed parameter object
        """
        param_objects = None
        
        if legacy_params is not None:
            if legacy_params == "":
                # Empty string case
                param_objects = None
                logging.info("Detected empty string parameter")
            elif legacy_params.strip():
                params_str = legacy_params.strip()
                # Try to parse as JSON
                try:
                    param_objects = json.loads(params_str)
                    logging.info(f"Parsed as JSON parameter: {param_objects}")
                except json.JSONDecodeError:
                    # Not valid JSON, check if it's a quoted string
                    if ((params_str.startswith('"') and params_str.endswith('"')) or 
                        (params_str.startswith("'") and params_str.endswith("'"))):
                        # Remove outer quotes
                        param_objects = params_str[1:-1]
                        logging.info(f"Detected string parameter: {param_objects}")
                    else:
                        # Treat as plain string
                        param_objects = params_str
                        logging.info(f"Treated as plain string: {param_objects}")
        
        return param_objects