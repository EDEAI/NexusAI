from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import socket
import traceback
import os
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from provider.sftp_provider import SftpProvider

class SftpDownloadTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
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
                "error": "Remote path is required for downloading files.",
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
            
            # 确保文件存在
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                yield self.create_json_message({
                    "error": f"Remote file not found: {remote_path}",
                    "success": False
                })
                return
            
            filename = os.path.basename(remote_path)
            
            # 下载文件
            with sftp.open(remote_path, 'rb') as remote_file:
                file_data = remote_file.read()
                
                # 返回文件内容作为blob
                mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                
                # 创建文件响应
                yield self.create_blob_message(
                    blob=file_data,
                    meta={
                        "mime_type": mime_type,
                        "filename": filename
                    }
                )
                
                # 发送成功消息
                yield self.create_text_message(f" '{filename}' download complete")
                
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