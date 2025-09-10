import os
import requests
from amadeus import Client, ResponseError


class AmadeusApiException(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


def grant_token(api_key: str, api_secret: str) -> Client:
    try:
        client = Client(
            client_id=api_key,
            client_secret=api_secret
        )
        # Trigger a simple call to validate credentials
        client.reference_data.locations.get(keyword='PAR', subType='CITY')
        return client
    except ResponseError as e:
        raise AmadeusApiException(str(e))


class AmadeusAPI:
    def __init__(self, api_key: str, api_secret: str):
        self.client = grant_token(api_key, api_secret)

    def search_flights(self, origin: str, destination: str, departure_date: str, adults: int = 1) -> dict:
        try:
            response = self.client.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=adults,
                max=3
            )
            return response.data
        except ResponseError as re:
            raise AmadeusApiException(str(re))
        except Exception as e:
            raise AmadeusApiException(f"[Unexpected Error] {str(e)}")
