import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.geo_encoder_decoder_api import OpenCageAPI, OpenCageApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DecodeCoordinatesTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api = OpenCageAPI(self.api_key)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            lat = tool_parameters["latitude"]
            lng = tool_parameters["longitude"]
            result = self.api.reverse_geocode(lat, lng)

            if not result.get("results"):
                yield self.create_text_message("No location found for the given coordinates.")
                return

            best_match = result["results"][0]
            formatted = best_match.get("formatted", "Unknown Location")

            msg = (
                f"Reverse geocoding result:\n"
                f"- Latitude: {lat}\n"
                f"- Longitude: {lng}\n"
                f"- Location: {formatted}"
            )

            yield self.create_text_message(msg)

        except OpenCageApiException as oce:
            raise ToolProviderCredentialValidationError(f"[OpenCage API Error] {str(oce)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
