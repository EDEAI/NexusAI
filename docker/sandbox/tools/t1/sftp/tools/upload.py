from collections.abc import Generator
from typing import Any, Dict, Optional
import paramiko
import socket
import traceback
import os
import tempfile

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from provider.sftp_provider import SftpProvider

class SftpUploadTool(Tool):
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
        files = tool_parameters.get('files', [])
        
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
                "error": "Remote path is required for uploading files.",
                "success": False
            })
            return
            
        if not files:
            yield self.create_json_message({
                "error": "No files provided for upload.",
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
            
            # 处理文件上传
            success_files = []
            
            for file in files:
                try:
                    file_temp = tempfile.NamedTemporaryFile(delete=False)
                    file_temp.write(file.blob)
                    file_temp.close()
                    
                    # 构建远程文件路径
                    remote_file_path = remote_path
                    if not remote_path.endswith('/'):
                        # 如果远程路径看起来像目录，则将文件名附加到路径后
                        try:
                            # 检查远程路径是否是目录
                            sftp.stat(remote_path)
                            is_dir = True
                        except:
                            is_dir = False
                            
                        if is_dir:
                            remote_file_path = os.path.join(remote_path, file.filename)
                    
                    # 上传文件
                    sftp.put(file_temp.name, remote_file_path)
                    
                    success_files.append({
                        "filename": file.filename,
                        "remote_path": remote_file_path,
                        "status": "success"
                    })
                    
                    # 删除临时文件
                    try:
                        os.unlink(file_temp.name)
                    except:
                        pass
                except Exception as e:
                    success_files.append({
                        "filename": file.filename,
                        "error": str(e),
                        "status": "failed"
                    })
            
            result = {
                "message": f"Files uploaded successfully to remote server",
                "details": success_files,
                "success": True
            }
            
            yield self.create_json_message(result)
            yield self.create_text_message(f"成功上传 {len([f for f in success_files if f['status'] == 'success'])} 个文件到远程服务器")
                
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