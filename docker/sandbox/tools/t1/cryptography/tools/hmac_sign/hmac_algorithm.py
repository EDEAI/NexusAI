from enum import StrEnum


class HmacAlgorithm(StrEnum):
    HMAC_SHA1="HMAC-SHA1"
    HMAC_SHA256="HMAC-SHA256"