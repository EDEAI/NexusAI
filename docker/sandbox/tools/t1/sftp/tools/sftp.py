from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import io
import socket
import traceback
import os
import base64

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SftpTool(Tool):
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
        remote_path = tool_parameters.get('remote_path')
        local_path = tool_parameters.get('local_path')
        
        # 验证必要参数
        if not host or not username or not action or not remote_path:
            yield self.create_json_message({
                "error": "Missing required parameters: host, username, action and remote_path are required.",
                "success": False
            })
            return
            
        # 验证认证参数
        if auth_type == 'password' and not password:
            yield self.create_json_message({
                "error": "Password is required for password authentication.",
                "success": False
            })
            return
        elif auth_type == 'key' and not private_key:
            yield self.create_json_message({
                "error": "Private key is required for key authentication.",
                "success": False
            })
            return
            
        # 验证上传/下载操作的本地路径
        if action in ['get', 'put'] and not local_path:
            yield self.create_json_message({
                "error": f"Local path is required for {action} operation.",
                "success": False
            })
            return
            
        try:
            # 创建Transport
            transport = paramiko.Transport((host, port))
            
            # 根据认证类型连接
            if auth_type == 'password':
                transport.connect(username=username, password=password)
            else:  # key authentication
                key_file = io.StringIO(private_key)
                if passphrase:
                    pkey = paramiko.RSAKey.from_private_key(key_file, password=passphrase)
                else:
                    pkey = paramiko.RSAKey.from_private_key(key_file)
                transport.connect(username=username, pkey=pkey)
                
            # 创建SFTP客户端
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            try:
                result = {}
                
                # 执行相应的SFTP操作
                if action == 'list':
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
                    
                elif action == 'get':
                    # 下载文件
                    sftp.get(remote_path, local_path)
                    result = {
                        "message": f"File downloaded successfully from {remote_path} to {local_path}",
                        "success": True
                    }
                    
                elif action == 'put':
                    # 上传文件
                    sftp.put(local_path, remote_path)
                    result = {
                        "message": f"File uploaded successfully from {local_path} to {remote_path}",
                        "success": True
                    }
                    
                elif action == 'mkdir':
                    # 创建目录
                    sftp.mkdir(remote_path)
                    result = {
                        "message": f"Directory {remote_path} created successfully",
                        "success": True
                    }
                    
                elif action == 'rmdir':
                    # 删除目录
                    sftp.rmdir(remote_path)
                    result = {
                        "message": f"Directory {remote_path} removed successfully",
                        "success": True
                    }
                    
                elif action == 'remove':
                    # 删除文件
                    sftp.remove(remote_path)
                    result = {
                        "message": f"File {remote_path} removed successfully",
                        "success": True
                    }
                    
                yield self.create_json_message(result)
                
            finally:
                sftp.close()
                transport.close()
                
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
