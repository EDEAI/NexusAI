import base64


def encode_to_base64(plain_text: str, urlsafe_enabled: bool) -> str:
    plain_text_bytes = plain_text.encode("utf-8")
    if urlsafe_enabled:
        base64_encoded_bytes = base64.urlsafe_b64encode(plain_text_bytes)
    else:
        base64_encoded_bytes = base64.b64encode(plain_text_bytes)
    return base64_encoded_bytes.decode("utf-8")

def encode_bytes_to_base64(input_bytes: bytes, urlsafe_enabled: bool) -> str:
    if urlsafe_enabled:
        base64_encoded_bytes = base64.urlsafe_b64encode(input_bytes)
    else:
        base64_encoded_bytes = base64.b64encode(input_bytes)
    return base64_encoded_bytes.decode("utf-8")


def decode_base64_to_str(encoded_text: str, urlsafe_enabled: bool) -> str:
    decoded_bytes = decode_base64_to_bytes(encoded_text, urlsafe_enabled)
    return decoded_bytes.decode("utf-8")


def decode_base64_to_bytes(encoded_text: str, urlsafe_enabled: bool) -> bytes:
    encoded_text_bytes = encoded_text.encode("utf-8")
    if urlsafe_enabled:
        decoded_bytes = base64.urlsafe_b64decode(encoded_text_bytes)
    else:
        decoded_bytes = base64.b64decode(encoded_text_bytes)
    return decoded_bytes
