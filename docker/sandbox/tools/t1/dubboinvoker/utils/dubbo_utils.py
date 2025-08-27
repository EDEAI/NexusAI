"""
Dubbo 客户端工具类 - 用于调用 Dubbo 服务

优化点：
1. 移除了未使用的导入 (json, urllib.parse, random, time, asyncio)
2. 将重复的类型集合提取为类常量，提高性能和可维护性
3. 预编译正则表达式，避免重复编译
4. 添加通用的类型提取方法，减少代码重复
5. 重构参数转换逻辑，通过 _convert_single_param 方法消除重复代码
6. 改进错误处理，支持 IPv6 地址和端口范围验证
7. 添加协议处理器缓存，避免重复创建对象
8. 完善文档和类型注解
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dubbo.client import DubboClient
from dubbo.codec.encoder import Object

from utils.registry_strategy import RegistryFactory

class ProtocolHandler:
    """Protocol handler base class, defines interface specification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def invoke(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]] = None,
        dubbo_version: str = "2.4.10",
        timeout: int = 60000
    ) -> Dict[str, Any]:
        """
        Invoke service method
        
        Parameters:
            service_uri: Service URI, including protocol, host and port
            interface: Interface name
            method: Method name
            params: Parameters
            param_types: Parameter types list (optional)
            dubbo_version: Dubbo version (optional)
            timeout: Timeout in milliseconds (optional)
            
        Returns:
            Invocation result
        """
        raise NotImplementedError("Subclasses must implement this method")


class DubboProtocolHandler(ProtocolHandler):
    """Dubbo native protocol (based on Hessian serialization) handler"""
    
    # 类常量：基础类型集合
    BASIC_TYPES = frozenset({
        'java.lang.String', 'java.lang.Integer', 'java.lang.Long', 
        'java.lang.Float', 'java.lang.Double', 'java.lang.Boolean',
        'java.lang.Byte', 'java.lang.Short', 'java.lang.Character',
        'int', 'long', 'float', 'double', 'boolean', 'byte', 'short', 'char'
    })
    
    # 类常量：集合类型集合
    COLLECTION_TYPES = frozenset({
        'java.util.List', 'java.util.ArrayList', 'java.util.LinkedList',
        'java.util.Map', 'java.util.HashMap', 'java.util.LinkedHashMap',
        'java.util.Set', 'java.util.HashSet', 'java.util.LinkedHashSet'
    })
    
    # 类常量：Map类型集合
    MAP_TYPES = frozenset({
        'java.util.Map', 'java.util.HashMap', 'java.util.LinkedHashMap',
        'java.util.TreeMap', 'java.util.ConcurrentHashMap'
    })
    
    # 类常量：List类型集合
    LIST_TYPES = frozenset({
        'java.util.List', 'java.util.ArrayList', 'java.util.LinkedList',
        'java.util.Vector', 'java.util.Stack'
    })
    
    # 编译一次的正则表达式
    URI_PATTERN = re.compile(r'^(?:dubbo:\/\/)?([^\/]+)(?:\/.*)?$')
    
    def invoke(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]] = None,
        dubbo_version: str = "2.4.10",
        timeout: int = 60000
    ) -> Dict[str, Any]:
        """
        Invoke service using Dubbo native protocol
        
        Parameters:
            service_uri: Dubbo service URI, format: dubbo://host:port
            interface: Interface name
            method: Method name
            params: Parameters
            param_types: Parameter types list (optional)
            dubbo_version: Dubbo version (optional)
            timeout: Timeout in milliseconds (optional)
            
        Returns:
            Invocation result
        """
        try:
            # Parse URI, extract host:port
            match = self.URI_PATTERN.match(service_uri)
            if not match:
                return {
                    "success": False, 
                    "result": None, 
                    "message": f"Service URI format error: {service_uri}, should be dubbo://host:port or host:port"
                }
            
            host_port = match.group(1)
            
            # Validate host:port format
            try:
                if ':' not in host_port:
                    raise ValueError("Missing port separator")
                host, port_str = host_port.rsplit(":", 1)  # Use rsplit to handle IPv6
                port = int(port_str)
                if not (1 <= port <= 65535):
                    raise ValueError("Port out of valid range")
            except ValueError as ve:
                return {
                    "success": False, 
                    "result": None, 
                    "message": f"Service address format error: {host_port}, should be host:port format. Details: {ve}"
                }
            
            # Create DubboClient and invoke service with configured version
            dubbo_client = DubboClient(interface, version='', dubbo_version=dubbo_version, host=host_port)
            
            # Convert timeout from milliseconds to seconds for DubboClient
            timeout_seconds = timeout / 1000.0
            
            # Call different methods based on parameter types and values
            if param_types is None:
                # Compatible with old invocation method - use correct dubbo-python2 API
                if params is None:
                    result = dubbo_client.call(method, timeout=timeout_seconds)
                else:
                    # For compatibility mode, params are passed as args parameter
                    result = dubbo_client.call(method, params, timeout=timeout_seconds)
            else:
                # Use typed parameter invocation
                result = self._call_with_types(dubbo_client, method, params, param_types, timeout_seconds)
            
            self.logger.debug(f"Dubbo protocol service invocation successful: {interface}.{method}")
            return {"success": True, "result": result, "message": "Invocation successful"}
            
        except Exception as e:
            self.logger.error(f"Dubbo protocol service invocation exception: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"Invocation exception: {str(e)}"}
    
    def _extract_clean_type(self, param_type: str) -> str:
        """
        Extract clean type name without generic information
        
        Args:
            param_type: Parameter type string
            
        Returns:
            Clean type name
        """
        return param_type.split('<')[0].strip()
    
    def _is_object_type(self, param_type: str) -> bool:
        """
        Determine if parameter type is object type
        
        Args:
            param_type: Parameter type string
            
        Returns:
            Whether it is object type
        """
        clean_type = self._extract_clean_type(param_type)
        
        return (clean_type not in self.BASIC_TYPES and 
                clean_type not in self.COLLECTION_TYPES and
                not clean_type.startswith('['))  # Array types
    
    def _is_map_type(self, param_type: str) -> bool:
        """
        Determine if parameter type is Map type
        
        Args:
            param_type: Parameter type string
            
        Returns:
            Whether it is Map type
        """
        clean_type = self._extract_clean_type(param_type)
        return clean_type in self.MAP_TYPES
    
    def _is_list_type(self, param_type: str) -> bool:
        """
        Determine if parameter type is List type
        
        Args:
            param_type: Parameter type string
            
        Returns:
            Whether it is List type
        """
        clean_type = self._extract_clean_type(param_type)
        return clean_type in self.LIST_TYPES
    
    def _convert_dict_to_object(self, value: dict, param_type: str) -> Object:
        """
        Convert Python dictionary to dubbo Object, recursively handle nested dictionaries and lists
        
        Args:
            value: Python dictionary
            param_type: Java type name
            
        Returns:
            Object instance
        """
        # Clean generic information, get pure class name
        clean_type = self._extract_clean_type(param_type)
        
        # Create Object instance
        obj = Object(clean_type)
        
        # Recursively handle all key-value pairs in dictionary
        for key, val in value.items():
            converted_val = self._convert_nested_value(val)
            obj[key] = converted_val
        
        self.logger.debug(f"Convert dictionary to Object: {clean_type} -> {obj}")
        return obj
    
    def _convert_nested_value(self, value):
        """
        Recursively convert nested values, convert Python dictionaries to Object, keep other types unchanged
        
        Args:
            value: Value to convert
            
        Returns:
            Converted value
        """
        if isinstance(value, dict):
            # For nested dictionaries, convert to generic Object type
            return self._convert_dict_to_object(value, "java.lang.Object")
        elif isinstance(value, list):
            # For lists, recursively process each element
            return [self._convert_nested_value(item) for item in value]
        else:
            # Other types (basic types) remain unchanged
            return value
    
    def _convert_list_to_arraylist(self, value: list, param_type: str) -> list:
        """
        Keep Python list unchanged, return directly (deprecated method, kept for compatibility)
        
        Args:
            value: Python list
            param_type: Java type name, e.g., "java.util.List<java.lang.String>"
            
        Returns:
            Original Python list
            
        Note:
            This method is deprecated and may be removed in future versions.
            Use _convert_list_to_java_collection instead.
        """
        # Ensure list elements are of correct type
        if 'java.lang.String' in param_type:
            # Ensure all elements are string type
            converted_list = [str(item) for item in value]
        else:
            converted_list = value
        
        self.logger.debug(f"List parameter kept as is: {param_type} -> contains {len(converted_list)} elements: {converted_list}")
        return converted_list
    
    def _convert_list_to_java_collection(self, value: list, param_type: str) -> Object:
        """
        Convert Python list to Java Collection object, correctly handle complex element types
        
        Args:
            value: Python list
            param_type: Java List type name (e.g., java.util.List, java.util.ArrayList, etc.)
            
        Returns:
            Object instance representing Java Collection object
        """
        # Clean generic information, get pure class name
        clean_type = self._extract_clean_type(param_type)
        
        # For List interface, use ArrayList as implementation class
        if clean_type == "java.util.List":
            clean_type = "java.util.ArrayList"
        
        # Extract generic type information
        element_type = None
        if '<' in param_type and '>' in param_type:
            start = param_type.find('<') + 1
            end = param_type.rfind('>')
            element_type = param_type[start:end].strip()
        
        # Convert elements in list
        converted_elements = []
        for item in value:
            if isinstance(item, dict) and element_type:
                # If it's a dictionary and has explicit element type, convert to Object
                converted_item = self._convert_dict_to_object(item, element_type)
                converted_elements.append(converted_item)
            else:
                # Other types remain unchanged
                converted_elements.append(item)
        
        # Create a standard Java ArrayList object
        collection_obj = Object(clean_type)
        
        # Use standard ArrayList field structure
        # elementData is the field name for ArrayList's internal storage array
        collection_obj['elementData'] = converted_elements
        collection_obj['size'] = len(converted_elements)
        
        self.logger.debug(f"Convert Python list to Java Collection: {param_type} -> {clean_type} object ({len(converted_elements)} elements, element type: {element_type})")
        return collection_obj
    
    def _convert_single_param(self, param: Any, param_type: str, index: Optional[int] = None) -> Any:
        """
        Convert single parameter based on its type
        
        Args:
            param: Parameter value
            param_type: Parameter type
            index: Parameter index for logging (optional)
            
        Returns:
            Converted parameter
        """
        if isinstance(param, dict):
            if self._is_object_type(param_type) or self._is_map_type(param_type):
                # Object type or Map type: convert to Object
                converted_param = self._convert_dict_to_object(param, param_type)
                log_prefix = f"Parameter[{index}]" if index is not None else "Single parameter"
                type_desc = "Map" if self._is_map_type(param_type) else "object"
                self.logger.debug(f"{log_prefix} {type_desc} conversion: {param_type} -> {type(converted_param)}")
                return converted_param
        elif isinstance(param, list):
            if self._is_list_type(param_type):
                # List type: convert to Java Collection object
                converted_param = self._convert_list_to_java_collection(param, param_type)
                log_prefix = f"Parameter[{index}]" if index is not None else "Single parameter"
                self.logger.debug(f"{log_prefix} List type: {param_type} -> converted to Java Collection object")
                return converted_param
        
        # Other types remain unchanged
        return param
    
    def _call_with_types(
        self, 
        client: DubboClient, 
        method: str, 
        params: Any, 
        param_types: Optional[List[str]],
        timeout: float = 60.0
    ) -> Any:
        """
        Call Dubbo service based on parameter types
        
        Args:
            client: Dubbo client instance
            method: Method name
            params: Parameter values (single value or array)
            param_types: Parameter types list (can be None for traditional invocation)
            timeout: Timeout in seconds (optional)
            
        Returns:
            Invocation result
        """
        # Handle traditional invocation (no type information)
        if param_types is None:
            self.logger.debug("Using traditional invocation method (no type information)")
            if params is None:
                return client.call(method, timeout=timeout)
            else:
                return client.call(method, params, timeout=timeout)
        
        # Handle no-parameter invocation
        if len(param_types) == 0:
            return client.call(method, [], param_types, timeout=timeout)
        elif len(param_types) == 1:
            # Single parameter invocation
            converted_params = self._convert_single_param(params, param_types[0])
            return client.call(method, converted_params, param_types, timeout=timeout)
        else:
            # Multi-parameter invocation - params must be list
            if not isinstance(params, (list, tuple)):
                raise ValueError(f"For multi-parameter invocation, params must be list or tuple type")
            
            if len(params) != len(param_types):
                raise ValueError(f"Number of parameters ({len(params)}) does not match number of parameter types ({len(param_types)})")
            
            # Convert object type parameters in parameter list
            converted_params = [
                self._convert_single_param(param, param_type, i) 
                for i, (param, param_type) in enumerate(zip(params, param_types))
            ]
            
            return client.call(method, converted_params, param_types, timeout=timeout)


class ProtocolFactory:
    """Protocol factory, creates corresponding protocol handler based on URI"""
    
    @staticmethod
    def create_protocol_handler(service_uri: str) -> ProtocolHandler:
        """
        Create protocol handler
        
        Parameters:
            service_uri: Service URI, including protocol prefix
            
        Returns:
            Protocol handler instance
        """
        # Check if service_uri is None
        if service_uri is None:
            raise ValueError("Service URI cannot be empty")
        
        # If no protocol is specified, use dubbo by default
        if "://" not in service_uri:
            service_uri = f"dubbo://{service_uri}"
        
        protocol = service_uri.split("://")[0].lower()
        
        if protocol == "dubbo":
            return DubboProtocolHandler()
        # Can add other protocol handlers here in the future
        # elif protocol == "triple":
        #    return TripleProtocolHandler()
        # elif protocol == "rest":
        #    return RestProtocolHandler()
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")


class DubboClientUtils:
    """Dubbo client util, call dubbo service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 缓存已创建的protocol handler以避免重复创建
        self._protocol_handler_cache = {}

    def invoke_with_registry(
        self, 
        registry_address: str, 
        interface: str, 
        method: str, 
        params: Optional[Any] = None,
        param_types: Optional[List[str]] = None,
        dubbo_version: str = "2.4.10",
        timeout: int = 60000
    ) -> Dict[str, Any]:
        """
        Invoke Dubbo service through registry
        
        Parameters:
            registry_address: registry address, format: zookeeper://host:port or nacos://host:port
            interface: interface name
            method: method name
            params: parameters
            param_types: parameter types (optional)
            dubbo_version: Dubbo version (optional)
            timeout: Timeout in milliseconds (optional)
            
        Returns:
            call result
        """
        self.logger.debug(f"Invoke Dubbo service through registry: {registry_address}, {interface}, {method}, {params}, types={param_types}")
        
        # Parse registry address
        registry_type, address = self._parse_registry_address(registry_address)
        
        try:
            # Create registry strategy using factory method
            registry_strategy = RegistryFactory.create_registry(registry_type)
            
            # Get provider address from registry
            provider_uri = registry_strategy.get_provider(address, interface)
                
            self.logger.debug(f"Get provider from registry: {provider_uri}")
            
            # Use obtained provider URI to invoke service
            return self.invoke_service(provider_uri, interface, method, params, param_types, dubbo_version, timeout)
        except Exception as e:
            self.logger.error(f"Failed to get provider from registry: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"Failed to get service provider from registry: {str(e)}"}

    def invoke_service(
        self, 
        service_uri: str, 
        interface: str, 
        method: str, 
        params: Optional[Any] = None,
        param_types: Optional[List[str]] = None,
        dubbo_version: str = "2.4.10",
        timeout: int = 60000
    ) -> Dict[str, Any]:
        """
        Invoke service method, supports multiple protocols
        
        Parameters:
            service_uri: Service URI, including protocol prefix, e.g., dubbo://host:port
            interface: Interface name
            method: Method name
            params: Parameters
            param_types: Parameter types list (optional)
            dubbo_version: Dubbo version (optional)
            timeout: Timeout in milliseconds (optional)
            
        Returns:
            Invocation result
        """
        self.logger.debug(f"Invoke service: {service_uri}, {interface}.{method}, params: {params}, types={param_types}")
        
        try:
            # Get protocol type for caching
            if "://" not in service_uri:
                protocol = "dubbo"
            else:
                protocol = service_uri.split("://")[0].lower()
            
            # Use cached protocol handler or create new one
            if protocol not in self._protocol_handler_cache:
                self._protocol_handler_cache[protocol] = ProtocolFactory.create_protocol_handler(service_uri)
            
            protocol_handler = self._protocol_handler_cache[protocol]
            
            # Invoke service
            return protocol_handler.invoke(service_uri, interface, method, params, param_types, dubbo_version, timeout)
        except Exception as e:
            self.logger.error(f"Service invocation exception: {str(e)}", exc_info=True)
            return {"success": False, "result": None, "message": f"Service invocation exception: {str(e)}"}

    def _parse_registry_address(self, registry_address: str) -> Tuple[str, str]:
        """Parse registry address, return (type, address) tuple"""
        match = re.match(r'^([a-z]+)://(.+)$', registry_address)
        if not match:
            raise ValueError(f"Registry address format error: {registry_address}")
        
        registry_type = match.group(1)
        address = match.group(2)
        
        return registry_type, address

# Singleton instance
dubbo_client_utils = DubboClientUtils() 