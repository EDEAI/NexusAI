from typing import Optional, Dict, Any
import uuid
import json
from datetime import datetime
from utils.connector import cloudflare_d1_query
from .conversation_storage_dataclasses import Message, Conversation


def conversation_storage_put_message(
    db_brand: str,
    db_metadata: Dict[str, Any],
    conversation_id: str,
    role: str,
    text: str,
    parent_message_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Add a new message to a specific conversation.
    If the conversation doesn't exist, create it first.

    Args:
        conversation_id: Target conversation ID
        role: Message sender role ('user', 'assistant', 'system', etc.)
        text: Message content text
        parent_message_id: Optional parent message ID for replies or edits
        metadata: Optional metadata dictionary

    Returns:
        {"message_id": message_id, "conversation_id": conversation_id}
    """
    # Check if conversation exists
    sql_check = "SELECT conversation_id FROM Conversation WHERE conversation_id = ?;"
    if db_brand == "cloudflare_d1_lite":
        account_id = db_metadata.get("account_id")
        database_id = db_metadata.get("database_id")
        api_token = db_metadata.get("api_token")
        check_result = cloudflare_d1_query(
            account_id=account_id,
            database_id=database_id,
            api_token=api_token,
            sql_query=sql_check,
            params=f'["{conversation_id}"]',
        )
    else:
        raise ValueError("Unsupported database brand")
    # check_result = d1_executor(sql_check, f'["{conversation_id}"]')
    check_data = (
        check_result.get("metadata", {}).get("result", [{}])[0].get("results", [])
    )

    # If conversation doesn't exist, create it
    if not check_data:
        conversation = Conversation(conversation_id=conversation_id)
        sql_create_conv = """
        INSERT INTO Conversation (conversation_id, sequence, status, created_at)
        VALUES (?, ?, ?, ?);
        """
        conv_values = f'["{conversation.conversation_id}", "{conversation.sequence}", "{conversation.status}", "{conversation.created_at.isoformat()}"]'
        cloudflare_d1_query(
            account_id=account_id,
            database_id=database_id,
            api_token=api_token,
            sql_query=sql_create_conv,
            params=conv_values,
        )

    # Now create the message
    message_id = str(uuid.uuid4())
    timestamp = datetime.now()
    message = Message(
        conversation_id=conversation_id,
        role=role,
        text=text,
        message_id=message_id,
        parent_message_id=parent_message_id,
        timestamp=timestamp,
        metadata=metadata,
    )

    sql_message = """
    INSERT INTO Message (message_id, conversation_id, role, text, parent_message_id, timestamp, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    message_values = f'["{message.message_id}", "{message.conversation_id}", "{message.role}", "{message.text}", {json.dumps(message.parent_message_id)}, "{message.timestamp.isoformat()}", {json.dumps(json.dumps(message.metadata) if message.metadata else None)}]'
    cloudflare_d1_query(
        account_id=account_id,
        database_id=database_id,
        api_token=api_token,
        sql_query=sql_message,
        params=message_values,
    )

    sql_conversation = """
    UPDATE Conversation
    SET latest_message_id = ?
    WHERE conversation_id = ?;
    """
    conversation_values = f'["{message.message_id}", "{message.conversation_id}"]'
    cloudflare_d1_query(
        account_id=account_id,
        database_id=database_id,
        api_token=api_token,
        sql_query=sql_conversation,
        params=conversation_values,
    )

    return {"message_id": message_id, "conversation_id": conversation_id}