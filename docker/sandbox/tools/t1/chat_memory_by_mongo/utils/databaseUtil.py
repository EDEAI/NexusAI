from typing import Dict, Any
from pymongo import MongoClient
from datetime import datetime

def get_mongo_client(db_metadata: Dict[str, Any]) -> MongoClient:
    """
    Create a MongoDB client instance.
    """
    try:
        print(f"Connecting to MongoDB at {db_metadata.get('host')}:{db_metadata.get('port')}")
        client = MongoClient(host=db_metadata.get("host"), port=db_metadata.get("port"), username=db_metadata.get("username"), password=db_metadata.get("password"))
        return client
    except Exception as e:
        raise Exception(f"Failed to connect to MongoDB: {e}")

def create_conversation(conv_id: str, user_id: str, db_metadata: Dict[str, Any]) -> str:
    client = get_mongo_client(db_metadata)
    db = client["ai_chat"]
    # 先查询有没有，如果没有就创建
    existing_conv = db["conversation"].find_one({"_id": conv_id})
    if existing_conv:
        return str(existing_conv["_id"])
    """创建新对话"""
    conversation = {
        "convId": conv_id,
        "userId": user_id,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    }
    result = db["conversation"].insert_one(conversation)
    return str(result.inserted_id)

def create_message(conv_id: str, user_id: str, role: str, content: str, db_metadata: Dict[str, Any]) -> str:
    """创建新消息"""
    message = {
        "convId": conv_id,
        "userId": user_id,
        "role": role,
        "content": content,
        "createdAt": datetime.now()
    }
    client = get_mongo_client(db_metadata)
    db = client["ai_chat"]
    result = db["message"].insert_one(message)
    # 更新对话时间
    db["conversation"].update_one(
        {"convId": conv_id},
        {"$set": {"updatedAt": datetime.now()}}
    )
    return str(result.inserted_id)

def get_conversation_messages(conv_id: str, user_id: str, db_metadata: Dict[str, Any], limit: int):
    """获取对话中的所有消息"""
    client = get_mongo_client(db_metadata)
    db = client["ai_chat"]
    # 构建查询条件
    query = {"convId": conv_id}  # 必须匹配 conv_id
    if user_id:  # 如果 user_id 不为空（非 None、非空字符串等），则额外匹配 user_id
        query["userId"] = user_id
    # 查询并排序
    msgs = db["message"].find(query) \
                .sort("createdAt", -1) \
                .limit(limit)
    # 返回格式化后的消息列表
    print("limit"+str(limit));
    return [{
        "role": msg["role"],
        "content": msg["content"],
        "createdAt": msg["createdAt"].strftime("%Y-%m-%d %H:%M:%S"),
    } for msg in msgs]

def delete_conversation(conv_id: str, db_metadata: Dict[str, Any]):
    """删除对话及其所有消息"""
    # 删除对话
    client = get_mongo_client(db_metadata)
    
    db = client["ai_chat"]
    db["conversation"].delete_one({"_id": conv_id})
    # 删除关联消息
    db["message"].delete_many({"convId": conv_id})
