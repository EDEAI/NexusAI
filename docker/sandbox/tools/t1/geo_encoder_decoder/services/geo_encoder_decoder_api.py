import os
import requests


class OpenCageApiException(Exception):
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


class OpenCageAPI:
    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise OpenCageApiException("Missing or invalid OpenCage API Key.")
        self.api_key = api_key
        self.endpoint = "https://api.opencagedata.com/geocode/v1/json"

    def reverse_geocode(self, latitude: float, longitude: float) -> dict:
        """Coordinates → Location (Reverse Geocoding)"""
        try:
            params = {
                'q': f'{latitude},{longitude}',
                'key': self.api_key
            }
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise OpenCageApiException("Failed to reverse geocode coordinates.", code=response.status_code)
        except Exception as e:
            raise OpenCageApiException(f"[Unexpected Error] {str(e)}")

    def forward_geocode(self, location: str) -> dict:
        """Location → Coordinates (Forward Geocoding)"""
        try:
            params = {
                'q': location,
                'key': self.api_key
            }
            response = requests.get(self.endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise OpenCageApiException("Failed to forward geocode location.", code=response.status_code)
        except Exception as e:
            raise OpenCageApiException(f"[Unexpected Error] {str(e)}")
