import sys, json, uuid, base64, random, string
from hashlib import md5
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from datetime import datetime
from decimal import Decimal

from Crypto.Cipher import AES

from config import settings
from core.database import redis

def convert_json_to_basic_types(data):
    """
    Recursively convert objects in JSON data to basic types.
    This includes converting datetime objects to strings and Decimal objects to floats.
    """
    if isinstance(data, dict):
        return {k: convert_json_to_basic_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_json_to_basic_types(v) for v in data]
    elif isinstance(data, datetime):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data

def push_to_websocket_queue(message: dict):
    """
    Push a message to the WebSocket message queue in Redis.

    Args:
        message (str): The message to be pushed to the queue.
    """
    redis.rpush(settings.WEBSOCKET_MESSAGE_QUEUE_KEY, json.dumps(convert_json_to_basic_types(message)))
    
def pop_from_websocket_queue() -> dict:
    """
    Pop a message from the WebSocket message queue in Redis.

    Returns:
        str: The message popped from the queue.
    """
    data = redis.lpop(settings.WEBSOCKET_MESSAGE_QUEUE_KEY)
    if data:
        return json.loads(data)
    return {}
    
def get_websocket_queue_length():
    """
    Get the length of the WebSocket message queue in Redis.

    Returns:
        int: The length of the WebSocket message queue.
    """
    return redis.llen(settings.WEBSOCKET_MESSAGE_QUEUE_KEY)

def generate_api_token() -> str:
    """
    Generate an API authentication token using uuid4 and base64 encoding.
    Replace all non-alphanumeric characters and insert 10-20 random characters at random positions.

    Returns:
        str: The generated API token.
    """
    # Generate a base64 encoded UUID
    token = uuid.uuid4().bytes
    base64_token = base64.b64encode(token).decode('utf-8')
    
    # Replace all non-alphanumeric characters
    alphanumeric_token = ''.join(c for c in base64_token if c.isalnum())
    
    # Generate random characters to insert
    num_random_chars = random.randint(10, 20)
    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=num_random_chars))
    
    # Insert random characters at random positions
    token_list = list(alphanumeric_token)
    for char in random_chars:
        position = random.randint(0, len(token_list))
        token_list.insert(position, char)
    
    # Join the list back into a string
    final_token = 'app-' + ''.join(token_list)
    
    return final_token

_nexus_ai_md5 = md5(b'NEXUSAI')
_aes = AES.new(_nexus_ai_md5.digest(), AES.MODE_ECB)

def encrypt_id(id_: int):
    return _aes.encrypt(id_.to_bytes(16, 'big')).hex()

def decrypt_id(encrypted_id: str):
    return int.from_bytes(_aes.decrypt(bytes.fromhex(encrypted_id)), 'big')