from typing import Optional, List, Dict, Any
import json
from utils.connector import cloudflare_d1_query
from .conversation_storage_dataclasses import Conversation, Message
from datetime import datetime


def conversation_storage_get_conversation(
    db_brand: str,
    db_metadata: Dict[str, Any],
    conversation_id: str,
    message_id: Optional[str] = "latest",
    max_round: int = 10,
) -> Optional[Conversation]:
    """
    Retrieve message history for a specific conversation.

    Args:
        db_brand: Database brand, should be "cloudflare_d1_lite"
        db_metadata: Metadata for database connection
        conversation_id: Target conversation ID
        message_id: Optional starting message ID. Default 'latest' gets the most recent messages.
                   Can be used to trace history from a specific message.
        max_round: Maximum number of message rounds to return (for lazy loading optimization)

    Returns:
        Conversation object containing message history (Message list).
        Message list structure depends on Conversation sequence type ('sequential' or 'tree').
        Returns None if conversation not found.
    """
    if db_brand != "cloudflare_d1_lite":
        raise ValueError("Unsupported database brand")

    account_id = db_metadata.get("account_id")
    database_id = db_metadata.get("database_id")
    api_token = db_metadata.get("api_token")

    sql_conversation = "SELECT * FROM Conversation WHERE conversation_id = ?;"
    conversation_result = cloudflare_d1_query(
        account_id=account_id,
        database_id=database_id,
        api_token=api_token,
        sql_query=sql_conversation,
        params=f'["{conversation_id}"]',
    )

    # Extract result from D1 response
    if not conversation_result.get("success"):
        return None

    results = (
        conversation_result.get("metadata", {})
        .get("result", [{}])[0]
        .get("results", [])
    )
    if not results:
        return None

    conversation_row = results[0]

    conversation = Conversation(
        conversation_id=conversation_row["conversation_id"],
        project=conversation_row["project"],
        brand=conversation_row["brand"],
        sequence=conversation_row["sequence"],
        status=conversation_row["status"],
        created_at=datetime.fromisoformat(conversation_row["created_at"]),
        latest_message_id=conversation_row["latest_message_id"],
        metadata=(
            json.loads(conversation_row["metadata"])
            if conversation_row["metadata"]
            else None
        ),
    )

    message_list: List[Message] = []
    if conversation.sequence == "sequential":
        sql_messages = """
        SELECT * FROM Message
        WHERE conversation_id = ?
        ORDER BY timestamp DESC
        LIMIT ?;
        """
        messages_result = cloudflare_d1_query(
            account_id=account_id,
            database_id=database_id,
            api_token=api_token,
            sql_query=sql_messages,
            params=f'["{conversation_id}", {max_round}]',
        )

        # Extract messages from D1 response
        if messages_result.get("success"):
            message_rows = (
                messages_result.get("metadata", {})
                .get("result", [{}])[0]
                .get("results", [])
            )

            for row in message_rows:
                message = Message(
                    message_id=row["message_id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    text=row["text"],
                    parent_message_id=row["parent_message_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                )
                message_list.append(message)
        conversation.messages = list(reversed(message_list))

    elif conversation.sequence == "tree":
        sql_messages = """
        SELECT * FROM Message
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
        LIMIT ?;
        """
        messages_result = cloudflare_d1_query(
            account_id=account_id,
            database_id=database_id,
            api_token=api_token,
            sql_query=sql_messages,
            params=f'["{conversation_id}", {max_round}]',
        )

        # Extract messages from D1 response
        if messages_result.get("success"):
            message_rows = (
                messages_result.get("metadata", {})
                .get("result", [{}])[0]
                .get("results", [])
            )

            for row in message_rows:
                message = Message(
                    message_id=row["message_id"],
                    conversation_id=row["conversation_id"],
                    role=row["role"],
                    text=row["text"],
                    parent_message_id=row["parent_message_id"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                )
                message_list.append(message)
        conversation.messages = message_list

    else:
        conversation.messages = []

    return conversation
