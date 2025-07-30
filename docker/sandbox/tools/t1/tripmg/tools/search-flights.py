import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.amadeus_api import AmadeusAPI
from amadeus import ResponseError
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SearchFlightsTool(Tool):
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
            adults = tool_parameters.get("adults", 1)

            response = self.api.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                max=3
            )

            offers = response.data
            if not offers:
                yield self.create_text_message("No flight offers found.")
                return

            msg = f"Found {len(offers)} flight(s) from {origin} to {destination} on {departure_date}:\n"
            for offer in offers:
                price = offer['price']['total']
                airline = offer['validatingAirlineCodes'][0] if offer.get('validatingAirlineCodes') else "Unknown"
                msg += f"- Airline: {airline}, Price: ${price}\n"

            yield self.create_text_message(msg)

        except ResponseError as re:
            raise ToolProviderCredentialValidationError(f"[Amadeus API Error] {str(re)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")


