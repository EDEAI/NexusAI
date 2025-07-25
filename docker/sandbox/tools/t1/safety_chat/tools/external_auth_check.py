from typing import Any, Dict, Generator
import base64
import json
import re
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

class ExternalAuthCheckTool(Tool):
    """外部认证检查工具
    
    检查用户是否通过外部认证服务认证。
    支持多种认证方式和配置选项。
    """
    
    def __init__(self, runtime, session):
        """初始化工具
        
        Args:
            runtime: 运行时环境
            session: 会话信息
        """
        super().__init__(runtime=runtime, session=session)
        
    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """验证参数
        
        Args:
            parameters: 参数字典
            
        Raises:
            ValueError: 参数验证失败
        """
        required_fields = [
            "auth_url", "request_method",
            "response_type", "success_check", "success_pattern",
            "success_value"
        ]
        for field in required_fields:
            if not parameters.get(field):
                raise ValueError(f"Missing required parameter: {field}")
                
        if parameters["request_method"] not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError("Unsupported request method")
            
        if parameters["response_type"] not in ["json", "text"]:
            raise ValueError("Unsupported response type")
            
        if parameters["success_check"] not in ["json_path", "regex"]:
            raise ValueError("Unsupported success check method")
            
        # 验证用户信息提取参数
        if "user_info_extract" in parameters:
            if parameters["user_info_extract"] not in ["json_path", "regex"]:
                raise ValueError("Unsupported user info extract method")
            if not parameters.get("user_info_pattern"):
                raise ValueError("Missing user info pattern when user_info_extract is specified")
            
        # 验证JSON参数格式
        for param_field in ["header_params", "query_params", "body_params"]:
            if parameters.get(param_field):
                param_value = parameters[param_field]
                if isinstance(param_value, str):
                    try:
                        # 清理字符串中的特殊字符和空白
                        cleaned_value = ''.join(c for c in param_value if c.isprintable())
                        cleaned_value = cleaned_value.strip()
                        
                        # 确保字符串是有效的JSON格式
                        if not (cleaned_value.startswith('{') and cleaned_value.endswith('}')):
                            raise ValueError(f"{param_field} must be a valid JSON object")
                            
                        # 解析JSON
                        parsed_json = json.loads(cleaned_value)
                        # 更新参数为解析后的JSON对象
                        parameters[param_field] = parsed_json
                        
                    except json.JSONDecodeError as e:
                        raise ValueError(f"{param_field} must be a valid JSON object: {str(e)}")
                elif not isinstance(param_value, dict):
                    raise ValueError(f"{param_field} must be a dictionary or JSON string")
                    
    def _prepare_headers(self, header_params: Dict[str, Any]) -> Dict[str, str]:
        """准备请求头
        
        Args:
            header_params: 请求头参数
            
        Returns:
            Dict[str, str]: 请求头
        """
        # 默认添加Content-Type
        headers = {
            "Content-Type": "application/json"
        }
        
        # 添加用户自定义的请求头
        if header_params:
            headers.update(header_params)
            
        return headers
        
    def _prepare_query_params(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """准备查询参数
        
        Args:
            query_params: 查询参数
            
        Returns:
            Dict[str, Any]: 查询参数
        """
        return query_params if query_params else {}
        
    def _prepare_body_params(self, body_params: Dict[str, Any]) -> Dict[str, Any]:
        """准备请求体参数
        
        Args:
            body_params: 请求体参数
            
        Returns:
            Dict[str, Any]: 请求体参数
        """
        return body_params if body_params else {}
        
    def _get_json_value(self, data: Any, path: str) -> Any:
        """从JSON数据中获取指定路径的值
        
        Args:
            data: JSON数据
            path: JSON路径(例如: data.user.name 或 data[0].name)
            
        Returns:
            Any: 找到的值,如果路径不存在则返回None
        """
        try:
            # 移除开头的$和.
            path = path.lstrip('$.')
            
            # 分割路径
            parts = re.split(r'\.|\[|\]', path)
            parts = [p for p in parts if p]
            
            # 遍历路径
            current = data
            for part in parts:
                if part.isdigit():  # 数组索引
                    current = current[int(part)]
                else:  # 对象属性
                    current = current[part]
            return current
            
        except (KeyError, IndexError, TypeError):
            return None
            
    def _check_success_json(self, response_data: Dict[str, Any], success_pattern: str, success_value: str) -> str:
        """使用JSON路径检查认证是否成功
        
        Args:
            response_data: 响应数据
            success_pattern: 成功模式(JSON路径)
            success_value: 成功值
            
        Returns:
            str: 是否认证成功("true"/"false")
        """
        try:
            # 获取JSON路径的值
            actual_value = self._get_json_value(response_data, success_pattern)
            if actual_value is None:
                return "false"
                
            # 检查值是否匹配
            if isinstance(actual_value, bool):
                return "true" if actual_value == (success_value.lower() == "true") else "false"
            elif isinstance(actual_value, (int, float)):
                try:
                    expected_value = float(success_value)
                    return "true" if actual_value == expected_value else "false"
                except ValueError:
                    return "false"
            else:
                return "true" if str(actual_value) == success_value else "false"
                
        except Exception:
            return "false"
            
    def _check_success_regex(self, response_text: str, success_pattern: str, success_value: str) -> str:
        """使用正则表达式检查认证是否成功
        
        Args:
            response_text: 响应文本
            success_pattern: 成功模式(正则表达式)
            success_value: 成功值
            
        Returns:
            str: 是否认证成功("true"/"false")
        """
        try:
            # 使用正则表达式匹配
            match = re.search(success_pattern, response_text)
            if not match:
                return "false"
                
            # 如果有捕获组,使用第一个捕获组的值
            matched_value = match.group(1) if match.groups() else match.group(0)
            return "true" if matched_value == success_value else "false"
            
        except Exception:
            return "false"
            
    def _extract_user_info(self, response_data: Any, extract_method: str, pattern: str) -> str:
        """提取用户信息
        
        Args:
            response_data: 响应数据
            extract_method: 提取方法(json_path/regex)
            pattern: 提取模式
            
        Returns:
            str: 提取的用户信息(字符串形式)
        """
        try:
            if extract_method == "json_path":
                if isinstance(response_data, str):
                    response_data = json.loads(response_data)
                extracted_value = self._get_json_value(response_data, pattern)
            else:  # regex
                if isinstance(response_data, (dict, list)):
                    response_text = json.dumps(response_data)
                else:
                    response_text = str(response_data)
                match = re.search(pattern, response_text)
                extracted_value = match.group(1) if match and match.groups() else match.group(0) if match else None
            
            # 将提取的值转换为字符串
            if extracted_value is None:
                return ""
            elif isinstance(extracted_value, (dict, list)):
                return json.dumps(extracted_value, ensure_ascii=False)
            else:
                return str(extracted_value)
                
        except Exception:
            return ""
            
    def _invoke(self, parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行工具调用
        
        Args:
            parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 调用结果
        """
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 准备请求参数
            header_params = json.loads(parameters.get("header_params", "{}")) if isinstance(parameters.get("header_params"), str) else parameters.get("header_params", {})
            query_params = json.loads(parameters.get("query_params", "{}")) if isinstance(parameters.get("query_params"), str) else parameters.get("query_params", {})
            body_params = json.loads(parameters.get("body_params", "{}")) if isinstance(parameters.get("body_params"), str) else parameters.get("body_params", {})
            
            headers = self._prepare_headers(header_params)
            params = self._prepare_query_params(query_params)
            data = self._prepare_body_params(body_params)
            
            # 发送请求
            if parameters["request_method"] == "GET":
                response = requests.get(parameters["auth_url"], headers=headers, params=params)
            elif parameters["request_method"] == "POST":
                response = requests.post(parameters["auth_url"], headers=headers, params=params, json=data)
            elif parameters["request_method"] == "PUT":
                response = requests.put(parameters["auth_url"], headers=headers, params=params, json=data)
            elif parameters["request_method"] == "DELETE":
                response = requests.delete(parameters["auth_url"], headers=headers, params=params)
                
            # 获取响应数据
            if parameters["response_type"] == "json":
                response_data = response.json()
            else:
                response_data = response.text
                
            # 检查认证结果
            if parameters["success_check"] == "json_path":
                if parameters["response_type"] != "json":
                    raise ValueError("When using JSON path check, the response type must be JSON")
                authenticated = self._check_success_json(response_data, parameters["success_pattern"], parameters["success_value"])
            else:  # regex
                if parameters["response_type"] == "json":
                    response_text = json.dumps(response_data)
                else:
                    response_text = response_data
                authenticated = self._check_success_regex(response_text, parameters["success_pattern"], parameters["success_value"])
                
            # 提取用户信息
            user_info = None
            if "user_info_extract" in parameters and "user_info_pattern" in parameters:
                user_info = self._extract_user_info(
                    response_data,
                    parameters["user_info_extract"],
                    parameters["user_info_pattern"]
                )
                
            # 返回结果
            yield self.create_variable_message("authenticated", authenticated)
            yield self.create_variable_message("user_info", user_info)
            
            
        except Exception as e:
            yield self.create_text_message(f"Execution failed: {str(e)}") 