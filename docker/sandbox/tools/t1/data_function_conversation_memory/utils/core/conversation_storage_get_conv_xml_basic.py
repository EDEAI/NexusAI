from typing import Dict, Any, Optional
from . import conversation_storage_get_conversation


def conversation_storage_get_conv_xml_basic(
    db_brand: str,
    db_metadata: Dict[str, Any],
    conversation_id: str,
    message_id: Optional[str] = "latest",
    max_round: int = 10,
) -> str:
    """
    获取对话历史并转换为基础XML格式

    Args:
        db_brand: 数据库类型
        db_metadata: 数据库连接元数据
        conversation_id: 对话ID
        message_id: 可选的起始消息ID
        max_round: 最大返回的消息轮数

    Returns:
        str: XML格式的消息历史
    """
    conversation = conversation_storage_get_conversation(
        db_brand=db_brand,
        db_metadata=db_metadata,
        conversation_id=conversation_id,
        message_id=message_id,
        max_round=max_round,
    )

    if not conversation or not hasattr(conversation, "messages"):
        return "<error>Conversation not found or this is the first message</error>"
    result = []
    for msg in conversation.messages:
        message_xml = f"""<message>
    <role>{msg.role}</role>
    <content>{msg.text}</content>
</message>"""
        result.append(message_xml)

    return "\n".join(result)
