import requests


def send_flomo_note(api_url: str, content: str) -> None:
    """
    Send a note to Flomo via the API URL. Raises requests.RequestException on network errors,
    and ValueError on invalid status codes or input.
    """
    api_url = api_url.strip()
    if not api_url:
        raise ValueError("API URL is required and cannot be empty.")
    if not api_url.startswith('https://flomoapp.com/iwh/'):
        raise ValueError(
            "API URL should be in the format: https://flomoapp.com/iwh/{token}/{secret}/"
        )
    if not content:
        raise ValueError("Content cannot be empty.")
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, json={"content": content}, headers=headers, timeout=10)
    if response.status_code != 200:
        raise ValueError(f"API URL is not valid. Received status code: {response.status_code}")
