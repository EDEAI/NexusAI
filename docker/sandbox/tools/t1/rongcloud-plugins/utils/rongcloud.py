"""
MIT License

Copyright (c) 2024 RongCloud Dify Plugin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import json
import logging
import time
from typing import Dict, Any, Optional

import requests

from provider.rongcloud_plugins import RC_PLUGIN_VERSION

logger = logging.getLogger(__name__)

class RongCloudAPI:
    """RongCloud API Client
    """

    def __init__(self, runtime):
        """Init RongCloud API Client
        
        Args:
            app_key: RongCloud AppKey
            app_secret: RongCloud AppSecret
            base_url: API base URL
        """
        self.app_key = runtime.credentials.get("app_key")
        self.app_secret = runtime.credentials.get("app_secret")

        if not self.app_key or not self.app_secret:
            error_msg = "No app_key or app_secret"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        self.base_url = runtime.credentials.get("host")
        if not self.base_url:
            error_msg = "No host"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info(f"Init RongCloud API Client: {runtime.credentials.get('host')}")
        self.session = requests.Session()

    def _get_nonce(self) -> str:
        """Generate random number
        
        Returns:
            str: Second-level timestamp
        """
        return str(int(time.time()))
        
    def _get_timestamp(self) -> str:
        """Get current timestamp
        
        Returns:
            str: Millisecond-level timestamp
        """
        return str(int(time.time() * 1000))
       
        
    def _get_signature(self, nonce: str, timestamp: str) -> str:
        """Generate signature
        
        Args:
            nonce: Random number
            timestamp: Timestamp
            
        Returns:
            str: SHA1 signature
        """
        sign_str = f"{self.app_secret}{nonce}{timestamp}"
        return hashlib.sha1(sign_str.encode()).hexdigest()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, is_json: bool = False, timeout: int = 30) -> requests.Response:
        """Send API request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
            is_json: Whether to send data in JSON format, default is False
            
        Returns:
            Dict[str, Any]: API response data
            
        Raises:
            Exception: When request fails or API returns error
        """
        url = f"{self.base_url}/{endpoint}"
        nonce = self._get_nonce()
        timestamp = self._get_timestamp()
        signature = self._get_signature(nonce, timestamp)
        
        headers = {
            "App-Key": self.app_key,
            "Nonce": nonce,
            "Timestamp": timestamp,
            "Signature": signature,
            "User-Agent": f'rc-dify-tool/{RC_PLUGIN_VERSION}',
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        if is_json:
            headers["Content-Type"] = "application/json"
        
        try:
            result = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if is_json else None,
                data=None if is_json else data,
                timeout=timeout
            )
            
            # Check HTTP status code
            if result.status_code != 200:
                error_msg = f"HTTP {result.status_code}: {result.text}"
                logger.error(f"Request failed: endpoint={endpoint}, {error_msg}")
                raise Exception(f"Request failed: {error_msg}")
            
            # Check if response is valid JSON
            try:
                response_data = result.json()
                if not response_data:
                    raise Exception("Empty response from server")
            except ValueError as e:
                error_msg = f"Invalid JSON response: {str(e)}"
                logger.error(f"JSON parse error: endpoint={endpoint}, {error_msg}")
                raise Exception(error_msg)
            
            return result
        except requests.RequestException as e:
            error_msg = f"Request Exception: endpoint={endpoint}\n{str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)