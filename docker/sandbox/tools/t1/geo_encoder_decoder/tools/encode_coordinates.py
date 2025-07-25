import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.geo_encoder_decoder_api import OpenCageAPI, OpenCageApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class EncodeCoordinatesTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api = OpenCageAPI(self.api_key)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            location = tool_parameters["location"]
            result = self.api.forward_geocode(location)

            if not result.get("results"):
                yield self.create_text_message("No coordinates found for the given location.")
                return

            best_match = result["results"][0]
            geometry = best_match.get("geometry", {})
            lat = geometry.get("lat", "N/A")
            lng = geometry.get("lng", "N/A")

            formatted = best_match.get("formatted", location)

            msg = (
                f"Geocoding result for \"{location}\":\n"
                f"- Latitude: {lat}\n"
                f"- Longitude: {lng}\n"
                f"- Formatted Location: {formatted}"
            )

            yield self.create_text_message(msg)

        except OpenCageApiException as oce:
            raise ToolProviderCredentialValidationError(f"[OpenCage API Error] {str(oce)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
