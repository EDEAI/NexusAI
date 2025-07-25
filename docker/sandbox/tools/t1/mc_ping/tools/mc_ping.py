from collections.abc import Generator
from typing import Any
import socket
import struct
import json
import time
import dns.resolver
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class MinecraftPingError(Exception):
    """Minecraft server query error"""
    pass

class MinecraftPing:
    def __init__(self):
        self.socket = None
        self.max_retries = 2
        self.server_port = 25565

    def resolve_mc_srv(self, address):
        """Resolve Minecraft SRV record"""
        # If it's an IP address, return directly
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', address):
            return address, self.server_port
        
        try:
            # Try to resolve SRV record
            answers = dns.resolver.resolve(f'_minecraft._tcp.{address}', 'SRV')
            if answers:
                record = answers[0]
                return str(record.target).rstrip('.'), record.port
        except Exception as e:
            # SRV resolution failed, use original address
            print(f"SRV resolution failed: {str(e)}")
        
        return address, self.server_port

    def connect(self, address, port=25565, timeout=5):
        """Connect to Minecraft server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        try:
            self.socket.connect((address, port))
            return True
        except socket.error as e:
            self.close()
            raise MinecraftPingError(f"Connection failed: {str(e)}")

    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            self.socket = None

    def write_varint(self, value):
        """Write VarInt format data"""
        data = bytearray()
        while True:
            if (value & ~0x7F) == 0:
                data.append(value)
                break
            data.append((value & 0x7F) | 0x80)
            value >>= 7
        return data

    def query(self, address, port=25565):
        """Query Minecraft server information"""
        self.server_port = port
        try:
            # Resolve SRV record
            resolved_address, resolved_port = self.resolve_mc_srv(address)
            print(f"Resolution result: {resolved_address}:{resolved_port}")
        except Exception as e:
            print(f"DNS resolution error: {str(e)}")
            resolved_address, resolved_port = address, port

        last_error = None
        for retry in range(self.max_retries + 1):
            try:
                if retry > 0:
                    print(f"Retry {retry} connecting to {resolved_address}:{resolved_port}")
                    time.sleep(1)  # Wait 1 second before retry

                self.connect(resolved_address, resolved_port)

                # Build handshake packet
                handshake = bytearray()
                handshake.append(0x00)  # Packet ID
                handshake.extend(b'\xff\xff\xff\xff\x0f')  # Protocol version
                handshake.append(len(address))  # Address length
                handshake.extend(address.encode('utf-8'))  # Address
                handshake.extend(struct.pack('>H', port))  # Port
                handshake.append(0x01)  # Status

                # Build complete packet
                packet = bytearray()
                packet.extend(self.write_varint(len(handshake)))
                packet.extend(handshake)
                packet.extend(b'\x01\x00')  # Request status

                # Send packet
                self.socket.send(packet)

                # Receive response
                data = bytearray()
                while True:
                    chunk = self.socket.recv(4096)
                    if len(chunk) == 0:
                        break
                    data.extend(chunk)
                    try:
                        # Try to parse JSON
                        json_start = data.find(b'{')
                        if json_start != -1:
                            json_data = data[json_start:].decode('utf-8')
                            response = json.loads(json_data)
                            self.close()
                            return response
                    except:
                        # Continue reading data
                        pass
                
                raise MinecraftPingError("Invalid response")
            except Exception as e:
                self.close()
                last_error = e
                if retry == self.max_retries:
                    raise MinecraftPingError(f"Server not responding (retried {retry} times): {str(e)}")

class McPingTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        host = tool_parameters.get('host')
        port = int(tool_parameters.get('port', 25565))
        
        if not host:
            yield self.create_json_message({
                "status": "error",
                "message": "Missing server address parameter"
            })
            return
        
        try:
            ping = MinecraftPing()
            result = ping.query(host, port)
            
            # Process return result
            description = (
                result.get('description', {}).get('text') if isinstance(result.get('description'), dict) 
                else result.get('description') if isinstance(result.get('description'), str) 
                else 'No description'
            )
            
            yield self.create_json_message({
                "status": "success",
                "data": {
                    "version": result.get('version', {}).get('name', 'Unknown'),
                    "online": result.get('players', {}).get('online', 0),
                    "max": result.get('players', {}).get('max', 0),
                    "description": description,
                    "queryTime": time.strftime("%Y-%m-%d %H:%M:%S")
                },
            })
        except Exception as e:
            error_message = str(e) if isinstance(e, MinecraftPingError) else "Error occurred during query"
            yield self.create_json_message({
                "status": "error",
                "message": error_message,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            })
