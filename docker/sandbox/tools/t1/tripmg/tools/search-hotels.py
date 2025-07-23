import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.amadeus_api import AmadeusAPI
from amadeus import ResponseError
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SearchHotelsTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api_secret = self.runtime.credentials.get("api_secret")
        self.api = AmadeusAPI(self.api_key, self.api_secret)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            city_code = tool_parameters["city_code"]
            limit = int(tool_parameters.get("limit", 5))
            response = self.api.client.reference_data.locations.hotels.by_city.get(
                cityCode=city_code,
            )

            hotels = response.data
            if not hotels:
                yield self.create_text_message("No hotels found.")
                return

            msg = f"Found {len(hotels)} hotel(s) in {city_code}:\n"
            for hotel in hotels[:limit]:  # limit to first 5 results
                name = hotel.get("name", "Unnamed Hotel")
                hotel_id = hotel.get("hotelId", "N/A")
                geo = hotel.get("geoCode", {})
                lat = geo.get("latitude", "N/A")
                lon = geo.get("longitude", "N/A")
                msg += f"- {name} (ID: {hotel_id}) at [Lat: {lat}, Lon: {lon}]\n"

            yield self.create_text_message(msg)

        except ResponseError as re:
            try:
                error_body = re.response.body  # raw error from API
            except Exception:
                error_body = "Could not retrieve error details"
            raise ToolProviderCredentialValidationError(f"[Amadeus API Error] {str(re)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
