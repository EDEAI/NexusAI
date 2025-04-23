import sys, json, uuid, base64, random, string
from collections import deque
from hashlib import md5
from pathlib import Path
from datetime import datetime
from typing import Union

sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from datetime import datetime
from decimal import Decimal

from Crypto.Cipher import AES

from config import settings
from core.database import redis

import tiktoken
from markitdown import MarkItDown
from typing import List, Dict, Any, Callable, Union
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

project_root = Path(__file__).absolute().parent.parent.parent
md = MarkItDown(enable_plugins=False)

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

def get_tags_mode_by_app_modes(app_mode_ids_str):
    """
    Get corresponding tags_mode_list based on app_mode_ids string

    Args:
        app_mode_ids_str (str): String of application mode IDs, can be single number or comma separated numbers

    Returns:
        list: Returns unique tags_mode list for given app_mode_ids,
              returns complete tags_mode_list if input is invalid
    """
    if isinstance(app_mode_ids_str, int):
        app_mode_ids_str = str(app_mode_ids_str)
        # Split input string into list of app_mode_ids
        app_mode_ids = [x.strip() for x in app_mode_ids_str.split(',')]
    elif isinstance(app_mode_ids_str, list):
        app_mode_ids =  app_mode_ids_str
    else:
        return [1, 2]
    # Define mapping relationship between app_mode and tags_mode
    app_to_tags_mode_mapping = {
        "1": [1],  # agent -> app
        "2": [1],  # workflow -> app
        "3": [2],  # dataset -> dataset
        "4": [1]  # custom tool -> app
    }
    # Collect all tags modes for given app_mode_ids
    result_tags = set()
    for app_mode_id in app_mode_ids:
        if app_mode_id in app_to_tags_mode_mapping:
            result_tags.update(app_to_tags_mode_mapping[app_mode_id])

    # If no valid app_mode_ids found, return complete tags_mode_list
    return list(result_tags) if result_tags else [1, 2]

_nexus_ai_md5 = md5(b'NEXUSAI')
_aes = AES.new(_nexus_ai_md5.digest(), AES.MODE_ECB)

def encrypt_id(id_: int):
    return _aes.encrypt(id_.to_bytes(16, 'big')).hex()

def decrypt_id(encrypted_id: str):
    return int.from_bytes(_aes.decrypt(bytes.fromhex(encrypted_id)), 'big')

def get_tokenizer(model_name: str, api_key: str) -> Union[tiktoken.Encoding, Anthropic]:
    """
    Get the appropriate tokenizer based on the model name
    
    Args:
        model_name (str): Model name, e.g., 'gpt-3.5-turbo', 'gpt-4', 'claude-3-opus'
        
    Returns:
        Union[tiktoken.Encoding, Anthropic]: Tokenizer object
    """
    if model_name.startswith('claude') and ANTHROPIC_AVAILABLE:
        anthropic = Anthropic(api_key=api_key)
        def anthropic_token_counter(text: str) -> int:
            return anthropic.messages.count_tokens(
                model=model_name,
                messages=[{'role': 'user', 'content': text}],
            ).input_tokens
        return anthropic_token_counter
    else:
        # Use cl100k_base encoder as default
        return tiktoken.encoding_for_model(model_name)

def count_tokens(tokenizer: Union[tiktoken.Encoding, Callable[[str], int]], text: str) -> int:
    """
    Count tokens in text using the appropriate tokenizer
    
    Args:
        tokenizer: Tokenizer object
        text: Text to count tokens for
        
    Returns:
        int: Number of tokens
    """
    if isinstance(tokenizer, tiktoken.Encoding):
        return len(tokenizer.encode(text))
    elif ANTHROPIC_AVAILABLE and isinstance(tokenizer, Callable):
        return tokenizer(text)
    return 0

def truncate_messages_by_token_limit(messages: List[Dict[str, Any]], model_config: dict) -> List[Dict[str, Any]]:
    """
    Traverse messages from newest to oldest and ensure total token count doesn't exceed 90% of model's context window.
    Uses official tokenizers for accurate token counting.
    
    Args:
        messages (list): List of message history
        model_config (dict): Model configuration containing model_name and context_length
        
    Returns:
        list: Truncated message list
    """
    if not messages:
        return messages
        
    # Get model information
    model_name = model_config['model_name']
    api_key = model_config['supplier_config']['api_key']
    max_context_tokens = model_config['max_context_tokens']
    max_output_tokens = model_config['max_output_tokens']
    token_limit = int((max_context_tokens - max_output_tokens) * 0.9)  # Use 90% of context length as limit
    
    # Get appropriate tokenizer
    tokenizer = get_tokenizer(model_name, api_key)
    
    truncated_messages = deque()
    current_tokens = 0
    
    # Traverse messages from newest to oldest
    for i, message in enumerate(reversed(messages)):
        # Convert message to JSON string and count tokens
        message_json = json.dumps(message, ensure_ascii=False)
        message_tokens = count_tokens(tokenizer, message_json)
        
        # Ensure at least ONE message will be reserved
        # Check if adding this message would exceed the token limit
        if i > 0 and current_tokens + message_tokens > token_limit:
            break
            
        current_tokens += message_tokens
        truncated_messages.appendleft(message)  # Insert message at beginning to maintain order
    
    return list(truncated_messages)


def truncate_agent_messages_by_token_limit(messages: List[Dict[str, Any]], model_config: dict) -> List[Dict[str, Any]]:
    """
    Traverse messages from newest to oldest and ensure total token count doesn't exceed 90% of model's context window.
    Uses official tokenizers for accurate token counting.

    Args:
        messages (list): List of message history
        model_config (dict): Model configuration containing model_name and context_length

    Returns:
        list: Truncated message list
    """
    if not messages:
        return messages

    # Get model information
    model_name = model_config['model_name']
    api_key = model_config['supplier_config']['api_key']
    max_context_tokens = model_config['max_context_tokens']
    max_output_tokens = model_config['max_output_tokens']
    token_limit = int((max_context_tokens - max_output_tokens) * 0.9)  # Use 90% of context length as limit

    # Get appropriate tokenizer
    tokenizer = get_tokenizer(model_name, api_key)

    truncated_messages = deque()
    current_tokens = 0

    # Traverse messages from newest to oldest
    for i, message in enumerate(reversed(messages)):
        # Convert message to JSON string and count tokens
        message_json = json.dumps(message['message'], ensure_ascii=False)
        message_tokens = count_tokens(tokenizer, message_json)

        # Ensure at least ONE message will be reserved
        # Check if adding this message would exceed the token limit
        if i > 0 and current_tokens + message_tokens > token_limit:
            break

        current_tokens += message_tokens
        truncated_messages.appendleft(message)  # Insert message at beginning to maintain order
    return list(truncated_messages)


def format_iso_time(dt: Union[datetime, None]) -> str:
    """
    Format a datetime object into a string in 'yyyy-mm-dd HH:MM:SS' format.

    :param dt: A datetime object, can be None
    :return: Formatted string, returns an empty string if input is None
    """
    if dt is None:
        return ""
    try:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return ""
    
def get_file_content_list(file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from core.database.models import UploadFiles
    from core.document import DocumentLoader
    
    file_content_list = []
    for file_var_value in file_list:
        if file_var_value:
            if isinstance(file_var_value, int):
                # Upload file ID
                file_id = file_var_value
                file_data = UploadFiles().get_file_by_id(file_var_value)
                file_path = project_root.joinpath(file_data['path'])
                file_name = file_data['name'] + file_data['extension']
            elif isinstance(file_var_value, str):
                file_id = 0
                if file_var_value[0] == '/':
                    file_var_value = file_var_value[1:]
                file_path = project_root.joinpath('storage').joinpath(file_var_value)
                file_name = file_path.name
            else:
                # This should never happen
                raise Exception('Unsupported value type!')
            if file_path.suffix in ['.jpg', 'jpeg', '.png', '.gif', '.webp']:
                # Use OCR for image files
                file_type = 'image'
                dl = DocumentLoader(file_path=str(file_path))
                file_content = '\n'.join([doc.page_content for doc in dl.load()])
            else:
                # Use Markdown for document files
                file_type = 'document'
                file_content = md.convert(file_path).text_content
            file_content_list.append({
                'id': file_id,
                'name': file_name,
                'type': file_type,
                'path': str(file_path),
                'content': file_content
            })
    return file_content_list
