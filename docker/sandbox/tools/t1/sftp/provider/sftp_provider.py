import paramiko
import io
import socket
import traceback

class SftpProvider:
    @staticmethod
    def create_sftp_client(host, port, username, auth_type, password=None, private_key=None, passphrase=None):
        """
        创建并返回SFTP客户端和Transport连接
        """
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
            
            return sftp, transport
            
        except Exception as e:
            raise e
    
    @staticmethod
    def close_connection(sftp, transport):
        """
        关闭SFTP连接和Transport
        """
        if sftp:
            sftp.close()
        if transport:
            transport.close()
            
    @staticmethod
    def validate_connection_params(host, username, auth_type, password, private_key):
        """
        验证连接参数
        """
        if not host or not username:
            return "Missing required parameters: host and username are required."
            
        if auth_type == 'password' and not password:
            return "Password is required for password authentication."
        elif auth_type == 'key' and not private_key:
            return "Private key is required for key authentication."
            
        return None 