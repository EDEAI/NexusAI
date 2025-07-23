from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import io
import socket
import traceback

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SshTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 提取参数
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 22))
        username = tool_parameters.get('username')
        auth_type = tool_parameters.get('auth_type')
        password = tool_parameters.get('password')
        private_key = tool_parameters.get('private_key')
        passphrase = tool_parameters.get('passphrase')
        command = tool_parameters.get('command')
        
        # 验证必要参数
        if not host or not username or not command:
            yield self.create_json_message({
                "error": "Missing required parameters: host, username, and command are required."
            })
            return
            
        # 验证认证参数
        if auth_type == 'password' and not password:
            yield self.create_json_message({
                "error": "Password is required for password authentication."
            })
            return
        elif auth_type == 'key' and not private_key:
            yield self.create_json_message({
                "error": "Private key is required for key authentication."
            })
            return
            
        try:
            # 创建SSH客户端
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # 根据认证类型连接
            if auth_type == 'password':
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            else:  # key authentication
                key_file = io.StringIO(private_key)
                if passphrase:
                    pkey = paramiko.RSAKey.from_private_key(key_file, password=passphrase)
                else:
                    pkey = paramiko.RSAKey.from_private_key(key_file)
                
                client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    pkey=pkey,
                    timeout=10
                )
                
            # 执行命令
            stdin, stdout, stderr = client.exec_command(command)
            
            # 获取输出
            stdout_str = stdout.read().decode('utf-8')
            stderr_str = stderr.read().decode('utf-8')
            
            # 关闭连接
            client.close()
            
            # 返回结果
            result = {
                "stdout": stdout_str,
                "stderr": stderr_str,
                "success": True
            }
            
            yield self.create_json_message(result)
            
        except paramiko.AuthenticationException:
            yield self.create_json_message({
                "error": "Authentication failed. Please check your credentials.",
                "success": False
            })
        except paramiko.SSHException as e:
            yield self.create_json_message({
                "error": f"SSH error: {str(e)}",
                "success": False
            })
        except socket.error as e:
            yield self.create_json_message({
                "error": f"Connection error: {str(e)}",
                "success": False
            })
        except Exception as e:
            yield self.create_json_message({
                "error": f"Error: {str(e)}",
                "traceback": traceback.format_exc(),
                "success": False
            })
