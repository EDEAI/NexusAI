import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.amadeus_api import AmadeusAPI
from amadeus import ResponseError
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GetPointsOfInterestTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api_secret = self.runtime.credentials.get("api_secret")
        self.api = AmadeusAPI(self.api_key, self.api_secret)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            city_code = tool_parameters["city_code"]  # e.g., "PAR"
            traveler_country = tool_parameters["traveler_country_code"]  # e.g., "FR"
            limit = tool_parameters.get("limit",5)
            response = self.api.client.reference_data.recommended_locations.get(
                cityCodes=city_code,
                travelerCountryCode=traveler_country
            )

            recommendations = response.data
            if not recommendations:
                yield self.create_text_message("No recommended locations found.")
                return

            msg = f"Recommended locations in {city_code} for travelers from {traveler_country}:\n"
            for loc in recommendations[:limit]:  # limit to 5 results
                name = loc.get("name", "Unnamed Location")
                category = loc.get("category", "Unknown")
                relevance = loc.get("relevance", "N/A")
                msg += f"- {name} ({category}, Relevance: {relevance})\n"

            yield self.create_text_message(msg)

        except ResponseError as re:
            raise ToolProviderCredentialValidationError(f"[Amadeus API Error] {str(re)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
