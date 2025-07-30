import json
from typing import Any


def parse_valid_json(json_str: str, param_name: str = "") -> dict[str, Any]:
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string for parameter {param_name}: {e}")


def check_valid_algorithm(algorithm):
    supported_algorithms = ["HS256", "RS256", "PS256", "EdDSA", "ES256"]
    if algorithm not in supported_algorithms:
        raise ValueError(
            f"Unsupported algorithm: {algorithm},"
            f" which should be one of supported algorithm names: {supported_algorithms}."
            f" Please refer to doc: https://pyjwt.readthedocs.io/en/stable/usage.html")


def check_key_length(key, algorithm):
    if algorithm == "HS256":
        if len(bytes(key, "utf-8")) < 32:
            raise ValueError("Key length should be at least 32 bytes for algorithm HS256.")
