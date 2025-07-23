import json
from typing import Any

import httpx
from khl.card import Card, CardMessage

from tools.model import KOOK_API_URL


def send_to_kook(card: Card, credentials: dict[str, Any]) -> None:
    """Send card message to Kook."""

    data = {
        "type": 10,
        "target_id": credentials.get("kook_channel_id", ""),
        "content": json.dumps(CardMessage(card)),
    }

    with httpx.Client(timeout=15) as client:
        res = client.post(
            f"{KOOK_API_URL}/message/create",
            json=data,
            headers={"Authorization": f"Bot {credentials.get('kook_token', '')}"},
        )

        res.raise_for_status()


def get_me(credentials: dict[str, Any]) -> None:
    """Get user info from Kook."""

    with httpx.Client(timeout=15) as client:
        res = client.post(
            f"{KOOK_API_URL}/user/me",
            headers={"Authorization": f"Bot {credentials.get('kook_token', '')}"},
        )
        res.raise_for_status()

