from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import socket
import traceback

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from provider.sftp_provider import SftpProvider

class SftpManageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 提取参数
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 22))
        username = tool_parameters.get('username')
        auth_type = tool_parameters.get('auth_type')
        password = tool_parameters.get('password')
        private_key = tool_parameters.get('private_key')
        passphrase = tool_parameters.get('passphrase')
        action = tool_parameters.get('action')
        path = tool_parameters.get('path')
        new_path = tool_parameters.get('new_path')
        
        # 验证必要参数
        error_msg = SftpProvider.validate_connection_params(host, username, auth_type, password, private_key)
        if error_msg:
            yield self.create_json_message({
                "error": error_msg,
                "success": False
            })
            return
            
        if not path:
            yield self.create_json_message({
                "error": "Path is required for file/directory operations.",
                "success": False
            })
            return
            
        if action == 'rename' and not new_path:
            yield self.create_json_message({
                "error": "New path is required for rename operation.",
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
            
            result = {}
            
            # 执行相应的SFTP操作
            if action == 'mkdir':
                sftp.mkdir(path)
                result = {
                    "message": f"Directory {path} created successfully",
                    "success": True
                }
                
            elif action == 'rmdir':
                sftp.rmdir(path)
                result = {
                    "message": f"Directory {path} removed successfully",
                    "success": True
                }
                
            elif action == 'remove':
                sftp.remove(path)
                result = {
                    "message": f"File {path} removed successfully",
                    "success": True
                }
                
            elif action == 'rename':
                sftp.rename(path, new_path)
                result = {
                    "message": f"Renamed {path} to {new_path} successfully",
                    "success": True
                }
                
            elif action == 'exists':
                try:
                    sftp.stat(path)
                    result = {
                        "exists": True,
                        "success": True
                    }
                except IOError:
                    result = {
                        "exists": False,
                        "success": True
                    }
                    
            elif action == 'stat':
                stat = sftp.stat(path)
                result = {
                    "stat": {
                        "size": stat.st_size,
                        "uid": stat.st_uid,
                        "gid": stat.st_gid,
                        "mode": stat.st_mode,
                        "atime": stat.st_atime,
                        "mtime": stat.st_mtime,
                        "is_dir": bool(stat.st_mode & 0o40000)
                    },
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