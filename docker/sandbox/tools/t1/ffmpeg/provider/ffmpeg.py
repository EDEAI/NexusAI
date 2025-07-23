from typing import Any
import subprocess

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class FfmpegProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证FFmpeg是否已安装并可用
            result = subprocess.run(['ffmpeg', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True)
            if result.returncode != 0:
                raise ToolProviderCredentialValidationError("FFmpeg is not installed or not available. Please install FFmpeg and try again.")
                
        except FileNotFoundError:
            raise ToolProviderCredentialValidationError("FFmpeg command not found. Please install FFmpeg and ensure it's in your PATH.")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to validate FFmpeg: {str(e)}")
