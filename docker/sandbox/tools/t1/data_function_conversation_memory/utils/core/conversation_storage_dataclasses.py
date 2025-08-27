from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class Conversation:
    """
    表示一个对话会话的类。

    Attributes:
        conversation_id (str): 对话ID，作为唯一标识符 (主键).  类型为 TEXT 在数据库中。
                                 如果未提供，则自动生成 UUID。
        project (Optional[str]): 项目标识符，用于区分不同项目的对话。 类型为 TEXT 在数据库中。
                                 可选字段。
        brand (Optional[str]): 品牌标识符，用于进一步区分，例如区分 Dify 或其他品牌。 类型为 TEXT 在数据库中。
                                 可选字段，用途由具体使用者定义，例如用作标签或分类。
        sequence (str): 对话序列类型，默认为 'sequential' (顺序对话)。 类型为 TEXT 在数据库中，默认值为 'sequential'，非空约束。
                        可以设置为 'sequential' (顺序对话，消息线性排列，按时间倒序检索) 或 'tree' (树状对话，支持编辑/重试等)。
                        当为 'tree' 时，消息通过 parent_message_id 形成树状结构，支持消息编辑和重试功能。
        status (str): 对话状态，默认为 'active'。类型为 TEXT 在数据库中，默认值为 'active'，非空约束。
                      例如，可以是 'active' (活跃)。 'archived' (已存档) 等状态是未来扩展方向，目前仅需考虑 'active' 状态。
                      未来 'archived' 状态的对话数据可能会移动到更低成本的存储服务。
        created_at (datetime): 对话创建的时间戳，默认为当前时间。 类型为 DATETIME 在数据库中，默认为当前时间戳。
        latest_message_id (Optional[str]): 最新消息的ID，用于快速访问最新消息。 类型为 TEXT 在数据库中。
                                            可选字段，通常在对话中有新消息时更新。
        metadata (Optional[Dict[str, Any]]):  与对话相关的元数据，可以存储任何额外的信息，以字典形式存储。
                                            类型为 TEXT 在数据库中，以 JSON 格式存储。
                                            这是一个灵活的字段，具体用途由开发者根据实际需求定义。
                                            例如，可以存储对话的摘要、用户偏好、会话标签、使用的模型配置等。
    """

    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project: Optional[str] = None
    brand: Optional[str] = None
    sequence: str = field(default="sequential")
    status: str = field(default="active")
    created_at: datetime = field(default_factory=datetime.now)
    latest_message_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Message:
    """
    表示对话中的一条消息的类。

    Attributes:
        conversation_id (str):  所属对话的ID，外键，关联到 Conversation 表的 conversation_id。 类型为 TEXT 在数据库中，非空约束。
        role (str): 消息发送者的角色，例如 'user' (用户), 'assistant' (助手), 'system' (系统) 等。 类型为 TEXT 在数据库中。
                    当用户编辑消息时，新的消息角色仍然是 'user'，但会通过 parent_message_id 关联到被编辑的消息。
        text (str): 消息的文本内容，不能为空。 类型为 TEXT 在数据库中，非空约束。
        message_id (str): 消息ID，作为唯一标识符 (主键)。 类型为 TEXT 在数据库中。
                             如果未提供，则自动生成 UUID。
        parent_message_id (Optional[str]): 父消息ID，用于表示消息的层级关系，例如回复消息或编辑/重试的消息。 可以为空。
                                        类型为 TEXT 在数据库中，这里使用 Optional[str] 表示可以为空。
                                        关联到 Message 表自身的 message_id (自引用外键关系).
                                        在 sequence='tree' 的对话中，用于构建消息树，实现消息编辑和重试功能。
                                        当消息是编辑或重试后的新消息时，此字段指向被编辑或重试的原始消息的 message_id。
        timestamp (datetime): 消息创建的时间戳，默认为当前时间。 类型为 DATETIME 在数据库中，默认为当前时间戳。
        metadata (Optional[Dict[str, Any]]): 与消息相关的元数据，可以存储任何额外的信息，以字典形式存储。
                                            类型为 TEXT 在数据库中，以 JSON 格式存储。
                                            这是一个灵活的字段，具体用途由开发者根据实际需求定义。
                                            例如，可以存储消息的发送/接收状态、tokens 消耗统计、外部引用链接、模型生成参数等。
    """

    conversation_id: str
    role: str
    text: str
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_message_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
