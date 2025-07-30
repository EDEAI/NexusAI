import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.amadeus_api import AmadeusAPI
from amadeus import ResponseError
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GetItineraryPriceMetricsTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api_secret = self.runtime.credentials.get("api_secret")
        self.api = AmadeusAPI(self.api_key, self.api_secret)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            origin = tool_parameters["origin"]
            destination = tool_parameters["destination"]
            departure_date = tool_parameters["departure_date"]

            response = self.api.client.analytics.itinerary_price_metrics.get(
                originIataCode=origin,
                destinationIataCode=destination,
                departureDate=departure_date
            )

            metrics = response.data
            if not metrics:
                yield self.create_text_message("No itinerary price data found.")
                return

            msg = f"Itinerary price metrics from {origin} to {destination} on {departure_date}:\n"
            for entry in metrics[:5]:
                min_fare = entry.get("minFare", "N/A")
                max_fare = entry.get("maxFare", "N/A")
                avg_fare = entry.get("averageFare", "N/A")
                currency = entry.get("currencyCode", "")
                msg += (
                    f"- Min: {min_fare} {currency}, Max: {max_fare} {currency}, "
                    f"Average: {avg_fare} {currency}\n"
                )

            yield self.create_text_message(msg)

        except ResponseError as re:
            raise ToolProviderCredentialValidationError(f"[Amadeus API Error] {str(re)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
