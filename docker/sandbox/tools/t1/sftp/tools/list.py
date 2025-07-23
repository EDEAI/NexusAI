from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import socket
import traceback

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from provider.sftp_provider import SftpProvider

class SftpListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 提取参数
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 22))
        username = tool_parameters.get('username')
        auth_type = tool_parameters.get('auth_type')
        password = tool_parameters.get('password')
        private_key = tool_parameters.get('private_key')
        passphrase = tool_parameters.get('passphrase')
        remote_path = tool_parameters.get('remote_path')
        
        # 验证必要参数
        error_msg = SftpProvider.validate_connection_params(host, username, auth_type, password, private_key)
        if error_msg:
            yield self.create_json_message({
                "error": error_msg,
                "success": False
            })
            return
            
        if not remote_path:
            yield self.create_json_message({
                "error": "Remote path is required for listing directories.",
                "success": False
            })
            return
            
        sftp = None
        transport = None
        try:
            # 创建SFTP客户端
            sftp, transport = SftpProvider.create_sftp_client(
                host, port, username, auth_type, password, private_key, passphrase
            )
            
            # 列出目录内容
            file_list = sftp.listdir_attr(remote_path)
            files = []
            for file_attr in file_list:
                file_info = {
                    'filename': file_attr.filename,
                    'size': file_attr.st_size,
                    'mtime': file_attr.st_mtime,
                    'mode': file_attr.st_mode,
                    'type': 'directory' if file_attr.st_mode & 0o40000 else 'file'
                }
                files.append(file_info)
            
            result = {
                "files": files,
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
        except IOError as e:
            yield self.create_json_message({
                "error": f"I/O error: {str(e)}",
                "success": False
            })
        except Exception as e:
            yield self.create_json_message({
                "error": f"Error: {str(e)}",
                "traceback": traceback.format_exc(),
                "success": False
            })
        finally:
            # 关闭连接
            SftpProvider.close_connection(sftp, transport) 