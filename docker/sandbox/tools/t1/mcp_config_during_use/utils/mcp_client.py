import json
import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from queue import Queue, Empty
from threading import Event, Thread
from typing import Any, Optional, Union
from urllib.parse import urljoin, urlparse

import httpx
from httpx_sse import connect_sse, EventSource


class TransportType(Enum):
    """transport type enum"""
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"
    AUTO_DETECT = "auto_detect"

class TransportStrategy(ABC):
    """Transport Strategy Abstract Base Class"""
    
    def __init__(self, url: str, headers: dict[str, Any] | None = None, 
                 timeout: float = 60, max_retries: int = 3, retry_interval: float = 2.0):
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.client = httpx.Client(headers=headers, follow_redirects=True, max_redirects=3)
        self._request_id = 0
        self.connect()
    
    @abstractmethod
    def connect(self) -> None:
        """connect to the transport"""
        pass
    
    @abstractmethod
    def send_message(self, data: dict) -> dict:
        """send message and return response"""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """close the transport"""
        pass
    
    def _get_next_request_id(self) -> int:
        """get the next request id"""
        self._request_id += 1
        return self._request_id

    @staticmethod
    def create_initialize_data(request_id: int = 1) -> dict:
        """create the initialize data"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-27",
                "capabilities": {},
                "clientInfo": {
                    "name": "MCP CONFIG DURING USE",
                    "version": "1.10.1"
                }
            }
        }

    @staticmethod
    def create_initialized_notification() -> dict:
        """create the initialized notification data"""
        return {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }


def remove_request_params(url: str) -> str:
    return urljoin(url, urlparse(url).path)


class McpClient:
    """MCP Client Main Class, using strategy pattern to support multiple transport types"""
    
    def __init__(self, url: str,
                 headers: dict[str, Any] | None = None,
                 timeout: float = 60,
                 sse_read_timeout: float = 300,
                 max_retries: int = 3,
                 retry_interval: float = 2.0,
                 transport_type: TransportType = TransportType.AUTO_DETECT):
        """
        initialize the MCP client
        
        Args:
            url: MCP server URL
            headers: request headers
            timeout: timeout
            sse_read_timeout: SSE read timeout
            max_retries: maximum retry count
            retry_interval: retry interval
            transport_type: transport type, default auto detect
        """
        self.transport = TransportFactory.create_transport(
            url=url,
            transport_type=transport_type,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            max_retries=max_retries,
            retry_interval=retry_interval
        )
        self.connect()
    
    def connect(self) -> None:
        """connect to the transport"""
        self.transport.connect()
    
    def close(self) -> None:
        """close the transport"""
        self.transport.close()
    
    def send_message(self, data: dict) -> dict:
        """send message"""
        return self.transport.send_message(data)

    def initialize(self):
        """initialize the MCP connection"""
        self.transport.initialize()

    def list_tools(self):
        """list the available tools"""
        tools_data = {
            "jsonrpc": "2.0",
            "id": self.transport._get_next_request_id(),
            "method": "tools/list",
            "params": {}
        }
        return self.send_message(tools_data).get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, tool_args: dict):
        """call the tool"""
        call_data = {
            "jsonrpc": "2.0",
            "id": self.transport._get_next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        return self.send_message(call_data).get("result", {}).get("content", [])


class McpClientsUtil:
    """MCP Client Utility Class"""

    @staticmethod
    def fetch_tools(server_url: str, 
                    headers: Optional[dict] = None, 
                    timeout: float = 60, 
                    sse_read_timeout: float = 300,
                    transport_type: TransportType = TransportType.AUTO_DETECT) -> list[dict]:
        """fetch the tools from the MCP server"""
        client = McpClient(
            url=server_url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            transport_type=transport_type
        )
        try:
            client.initialize()
            return client.list_tools()
        finally:
            client.close()

    @staticmethod
    def execute_tool(server_url: str,
                     tool_name: str, 
                     tool_args: dict[str, Any],
                     headers: Optional[dict] = None, 
                     timeout: float = 60, 
                     sse_read_timeout: float = 300,
                     transport_type: TransportType = TransportType.AUTO_DETECT) -> str:
        """execute the tool on the MCP server"""
        client = McpClient(
            url=server_url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            transport_type=transport_type
        )
        try:
            client.initialize()
            return client.call_tool(tool_name, tool_args)
        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            logging.error(error_msg)
            return error_msg
        finally:
            client.close()


class SseTransportStrategy(TransportStrategy):
    """SSE transport strategy implementation"""
    
    def __init__(self, url: str, headers: dict[str, Any] | None = None, 
                 timeout: float = 60, sse_read_timeout: float = 60 * 5,
                 max_retries: int = 3, retry_interval: float = 2.0):
        self.sse_read_timeout = sse_read_timeout
        self.endpoint_url = None
        self.message_queue = Queue()
        self.response_ready = Event()
        self.should_stop = Event()
        self._listen_thread = None
        self._connected = Event()
        super().__init__(url, headers, timeout, max_retries, retry_interval)
    
    def connect(self) -> None:
        """connect to the SSE endpoint"""
        self._listen_thread = Thread(target=self._listen_messages, daemon=True)
        self._listen_thread.start()
        if not self._connected.wait(timeout=self.timeout):
            raise TimeoutError("MCP Server connection timeout!")
    
    def initialize(self):
        """initialize the SSE connection"""
        self.send_message(self.create_initialize_data())
        self.send_message(self.create_initialized_notification())

    def _listen_messages(self) -> None:
        """listen to the SSE messages"""
        logging.debug(f"Connecting to SSE endpoint: {remove_request_params(self.url)}")
        retry_count = 0
        
        while not self.should_stop.is_set() and retry_count <= self.max_retries:
            try:
                with connect_sse(
                        client=self.client,
                        method="GET",
                        url=self.url,
                        timeout=httpx.Timeout(self.timeout, read=self.sse_read_timeout),
                ) as event_source:
                    event_source.response.raise_for_status()
                    logging.debug("SSE connection established")
                    retry_count = 0
                    
                    for sse in event_source.iter_sse():
                        if self.should_stop.is_set():
                            logging.info("Stopping SSE listener due to stop signal")
                            break
                            
                        logging.debug(f"Received SSE event: {sse.event}")
                        match sse.event:
                            case "endpoint":
                                self.endpoint_url = urljoin(self.url, sse.data)
                                logging.info(f"Received endpoint URL: {self.endpoint_url}")
                                self._connected.set()
                                url_parsed = urlparse(self.url)
                                endpoint_parsed = urlparse(self.endpoint_url)
                                if (url_parsed.netloc != endpoint_parsed.netloc
                                        or url_parsed.scheme != endpoint_parsed.scheme):
                                    error_msg = f"Endpoint origin does not match connection origin: {self.endpoint_url}"
                                    logging.error(error_msg)
                                    raise ValueError(error_msg)
                            case "message":
                                message = json.loads(sse.data)
                                logging.debug(f"Received server message: {message}")
                                self.message_queue.put(message)
                                self.response_ready.set()
                            case _:
                                logging.warning(f"Unknown SSE event: {sse.event}")
                                
            except httpx.ReadError as e:
                if self.should_stop.is_set():
                    logging.debug(f"Ignoring SSE connection read error due to stop signal: {str(e)}")
                    break
                
                logging.warning(f"SSE connection read error: {str(e)}")
                if retry_count < self.max_retries:
                    retry_count += 1
                    logging.info(f"Retrying SSE connection ({retry_count}/{self.max_retries}) in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    logging.error(f"Max retries ({self.max_retries}) exceeded for SSE connection")
                    break
            except Exception as e:
                logging.error(f"Error in SSE connection: {str(e)}")
                if retry_count < self.max_retries:
                    retry_count += 1
                    logging.info(f"Retrying SSE connection ({retry_count}/{self.max_retries}) in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    logging.error(f"Max retries ({self.max_retries}) exceeded for SSE connection")
                    break
    
    def send_message(self, data: dict) -> dict:
        """send message to the SSE endpoint"""
        if not self.endpoint_url:
            raise RuntimeError("please call connect() first")
        
        logging.debug(f"Sending client message: {data}")
        response = self.client.post(
            url=self.endpoint_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        if (response.url != self.endpoint_url):
            logging.debug(f"SSE redirected url: {response.url}")
            self.endpoint_url = str(response.url)

        response.raise_for_status()
        logging.debug(f"Client message sent successfully: {response.status_code}")
        
        if "id" in data:
            message_id = data["id"]
            while True:
                self.response_ready.wait()
                self.response_ready.clear()
                try:
                    while True:
                        message = self.message_queue.get_nowait()
                        if "id" in message and message["id"] == message_id:
                            self._request_id += 1
                            return message
                        self.message_queue.put(message)
                except Empty:
                    pass
        return {}
    
    def close(self) -> None:
        """close the SSE connection"""
        self.should_stop.set()
        self.client.close()
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=10)
    

class StreamableHttpTransportStrategy(TransportStrategy):
    """Streamable HTTP transport strategy implementation"""
    
    def __init__(self, url: str, headers: dict[str, Any] | None = None, 
                 timeout: float = 60, max_retries: int = 3, retry_interval: float = 2.0, 
                 session_id: str | None = None):
        super().__init__(url, headers, timeout, max_retries, retry_interval)
        self.mcp_endpoint = url
        self.pre_initialized = False
        self.session_id = session_id

    def connect(self) -> None:
        """connect to the Streamable HTTP endpoint (no additional operation)"""
        pass

    def initialize(self):
        """initialize the Streamable HTTP connection"""

        if not self.pre_initialized:
            self.pre_initialize()

        self.send_message(self.create_initialized_notification())

    def pre_initialize(self):
        """pre-initialize the Streamable HTTP connection"""
        self.send_message(self.create_initialize_data())

        self.pre_initialized = True

    def send_message(self, data: dict) -> dict:
        """send message to the MCP endpoint"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'
        }
        
        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id
        
        logging.debug(f"Sending message to MCP endpoint: {data}")
        
        try:
            response = self.client.post(
                url=self.mcp_endpoint,
                json=data,
                headers=headers,
                timeout=self.timeout
            )
            if (response.url != self.mcp_endpoint):
                logging.debug(f"Streamable HTTP redirected url: {response.url}")
                self.mcp_endpoint = str(response.url)

            response.raise_for_status()
            
            if 'Mcp-Session-Id' in response.headers:
                self.session_id = response.headers['Mcp-Session-Id']
                logging.debug(f"Received session ID: {self.session_id}")

            logging.debug(f"response content: {response.content}")
            if not response.content:
                return {}
            
            content_type = response.headers.get('Content-Type', '')

            if 'application/json' in content_type:
                result = response.json()
                logging.debug(f"Received JSON response: {result}")
                return result
                
            elif 'text/event-stream' in content_type:
                logging.debug("Handling SSE stream response")
                for sse in EventSource(response).iter_sse():
                    if sse.event != "message":
                        raise Exception(f"StreamableHttpTransportStrategy - Unknown Server-Sent Event: {sse.event}")
                    message = json.loads(sse.data)
                return message
            else:
                logging.warning(f"Unexpected content type: {content_type}")
                return {}
                
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            raise
    
    def close(self) -> None:
        """close the Streamable HTTP connection"""
        self.client.close()
        logging.debug("Streamable HTTP transport closed")
    

class TransportFactory:
    """Transport Strategy Factory Class"""
    
    @staticmethod
    def create_transport(url: str, 
                        transport_type: TransportType = TransportType.AUTO_DETECT,
                        headers: dict[str, Any] | None = None,
                        timeout: float = 60,
                        sse_read_timeout: float = 300,
                        max_retries: int = 3,
                        retry_interval: float = 2.0) -> TransportStrategy:
        """create the transport strategy instance"""
        
        if transport_type == TransportType.SSE:
            return SseTransportStrategy(
                url=url,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
        elif transport_type == TransportType.STREAMABLE_HTTP:
            return StreamableHttpTransportStrategy(
                url=url,
                headers=headers,
                timeout=timeout,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
        elif transport_type == TransportType.AUTO_DETECT:
            return TransportFactory._auto_detect_transport(
                url=url,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout,
                max_retries=max_retries,
                retry_interval=retry_interval
            )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")
    
    @staticmethod
    def _auto_detect_transport(url: str,
                              headers: dict[str, Any] | None = None,
                              timeout: float = 60,
                              sse_read_timeout: float = 300,
                              max_retries: int = 3,
                              retry_interval: float = 2.0) -> TransportStrategy:
        """auto detect and create the appropriate transport strategy"""
        
        logging.debug(f"Auto-detecting transport type for: {url}")
        try:
            streamable_http_transport = StreamableHttpTransportStrategy(
                url=url,
                headers=headers,
                timeout=timeout,
                max_retries=max_retries,
                retry_interval=retry_interval,
            )
            streamable_http_transport.pre_initialize()
            logging.debug(f"Streamable HTTP detection success")
            return streamable_http_transport
        except Exception as e:
            logging.debug(f"Streamable HTTP detection failed: {e}")
        
        # if Streamable HTTP detection fails, fall back to SSE
        logging.debug("Falling back to SSE transport")
        return SseTransportStrategy(
            url=url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            max_retries=max_retries,
            retry_interval=retry_interval
        )


