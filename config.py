import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    MYSQL_HOST: str = os.environ.get('MYSQL_HOST', os.getenv('MYSQL_HOST'))
    MYSQL_PORT: int = int(os.environ.get('MYSQL_PORT', os.getenv('MYSQL_PORT', 3306)))
    MYSQL_USER: str = os.environ.get('MYSQL_USER', os.getenv('MYSQL_USER'))
    MYSQL_PASSWORD: str = os.environ.get('MYSQL_PASSWORD', os.getenv('MYSQL_PASSWORD'))
    MYSQL_DB: str = os.environ.get('MYSQL_DB', os.getenv('MYSQL_DB'))

    REDIS_HOST: str = os.environ.get('REDIS_HOST', os.getenv('REDIS_HOST'))
    REDIS_PORT: int = int(os.environ.get('REDIS_PORT', os.getenv('REDIS_PORT', 6379)))
    REDIS_DB: int = int(os.environ.get('REDIS_DB', os.getenv('REDIS_DB', 0)))
    REDIS_PASSWORD: str = os.environ.get('REDIS_PASSWORD', os.getenv('REDIS_PASSWORD'))
    WEBSOCKET_MESSAGE_QUEUE_KEY: str = os.environ.get('WEBSOCKET_MESSAGE_QUEUE_KEY',
                                                      os.getenv('WEBSOCKET_MESSAGE_QUEUE_KEY'))

    VDB_TYPE: str = os.environ.get('VDB_TYPE', os.getenv('VDB_TYPE'))
    VDB_HOST: str = os.environ.get('VDB_HOST', os.getenv('VDB_HOST'))
    VDB_PORT: int = int(os.environ.get('VDB_PORT', os.getenv('VDB_PORT', 19530)))
    VDB_USER: str = os.environ.get('VDB_USER', os.getenv('VDB_USER'))
    VDB_PASSWORD: str = os.environ.get('VDB_PASSWORD', os.getenv('VDB_PASSWORD'))

    RETRIEVER_TYPE: str = os.environ.get('RETRIEVER_TYPE', os.getenv('RETRIEVER_TYPE'))
    RETRIEVER_K: int = int(os.environ.get('RETRIEVER_K', os.getenv('RETRIEVER_K', 4)))
    RETRIEVER_SCORE_THRESHOLD: float = float(
        os.environ.get('RETRIEVER_SCORE_THRESHOLD', os.getenv('RETRIEVER_SCORE_THRESHOLD', 0.0)))

    ACCESS_TOKEN_SECRET_KEY: str = os.environ.get('ACCESS_TOKEN_SECRET_KEY', os.getenv('ACCESS_TOKEN_SECRET_KEY'))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES', os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60)))

    APP_API_TIMEOUT: int = int(os.environ.get('APP_API_TIMEOUT', os.getenv('APP_API_TIMEOUT', 60)))

    LOG_ROTATE_INTERVAL: int = int(os.environ.get('LOG_ROTATE_INTERVAL', os.getenv('LOG_ROTATE_INTERVAL', 6)))
    LOG_BACKUP_COUNT: int = int(os.environ.get('LOG_BACKUP_COUNT', os.getenv('LOG_BACKUP_COUNT', 40)))

    HTTP_CONNECT_TIMEOUT: int = int(os.environ.get('HTTP_CONNECT_TIMEOUT', os.getenv('HTTP_CONNECT_TIMEOUT', 300)))
    HTTP_READ_TIMEOUT: int = int(os.environ.get('HTTP_READ_TIMEOUT', os.getenv('HTTP_READ_TIMEOUT', 600)))
    HTTP_WRITE_TIMEOUT: int = int(os.environ.get('HTTP_WRITE_TIMEOUT', os.getenv('HTTP_WRITE_TIMEOUT', 600)))
    HTTP_RESPONSE_MAX_BINARY_SIZE: int = int(
        os.environ.get('HTTP_RESPONSE_MAX_BINARY_SIZE', os.getenv('HTTP_RESPONSE_MAX_BINARY_SIZE', 10485760)))
    HTTP_RESPONSE_MAX_TEXT_SIZE: int = int(
        os.environ.get('HTTP_RESPONSE_MAX_TEXT_SIZE', os.getenv('HTTP_RESPONSE_MAX_TEXT_SIZE', 1048576)))

    SANDBOX_HOST: str = os.environ.get('SANDBOX_HOST', os.getenv('SANDBOX_HOST'))
    SANDBOX_PORT: int = int(os.environ.get('SANDBOX_PORT', os.getenv('SANDBOX_PORT', 8001)))

    DEFAULT_LLM_SUPPLIER_CONFIG_ID: int = int(
        os.environ.get('DEFAULT_LLM_SUPPLIER_CONFIG_ID', os.getenv('DEFAULT_LLM_SUPPLIER_CONFIG_ID', 1)))
    DEFAULT_LLM_CONFIG_ID: int = int(os.environ.get('DEFAULT_LLM_CONFIG_ID', os.getenv('DEFAULT_LLM_CONFIG_ID', 3)))

    CHATROOM_WEBSOCKET_PORT: int = int(
        os.environ.get('CHATROOM_WEBSOCKET_PORT', os.getenv('CHATROOM_WEBSOCKET_PORT', 8765)))
    WEBSOCKET_PORT: int = int(os.environ.get('WEBSOCKET_PORT', os.getenv('WEBSOCKET_PORT', 9473)))
    MCP_SERVER_PORT: int = int(os.environ.get('MCP_SERVER_PORT', os.getenv('MCP_SERVER_PORT', 9478)))

    WEB_URL: str = os.environ.get('WEB_URL', os.getenv('WEB_URL'))
    ICON_URL: str = os.environ.get('ICON_URL', os.getenv('ICON_URL'))

    FASTAPI_WORKERS: int = int(os.environ.get('FASTAPI_WORKERS', os.getenv('FASTAPI_WORKERS', 10)))
    CELERY_WORKERS: int = int(os.environ.get('CELERY_WORKERS', os.getenv('CELERY_WORKERS', 20)))
    API_PORT: int = int(os.environ.get('API_PORT', os.getenv('API_PORT', 9472)))
    STORAGE_URL: str = str(os.environ.get('STORAGE_URL', os.getenv('STORAGE_URL', '')))


settings = Settings()

model_config = [
    {
        'supplier': 'OpenAI',
        'mode': 1,
        'config': [
            {
                "key": "api_key",
                "type": "str",
                "value": "",
                "secret": True,
                "options": None,
                "optional": False,
                "description": "Automatically inferred from env var `OPENAI_API_KEY` if not provided.",
                "default_value": ""
            }
        ],
        'models': {
            'text-generation': [
                {
                    'model_name': 'gpt-4o',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 128000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 16384
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "gpt-3.5-turbo"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'gpt-4o-mini',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 128000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 16384
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "gpt-3.5-turbo"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'gpt-4-turbo',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 128000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "gpt-3.5-turbo"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'gpt-4-1106-preview',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 128000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "gpt-3.5-turbo"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'gpt-3.5-turbo',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 16385
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "gpt-3.5-turbo"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'o3-mini',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 100000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "o3-mini-2025-01-31"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 1
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                }
            ],
            'embeddings': [
                {
                    'model_name': 'text-embedding-ada-002',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 0
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 0
                    },
                    'config': [
                        {
                            'description': None,
                            'type': 'str',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'default_value': 'OpenAIEmbeddings',
                            'value': 'OpenAIEmbeddings',
                            'key': 'type'
                        },
                        {
                            'description': None,
                            'type': 'str',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'default_value': 'text-embedding-ada-002',
                            'value': 'text-embedding-ada-002',
                            'key': 'model'
                        },
                        {
                            'description': 'Maximum number of retries to make when generating.',
                            'type': 'int',
                            'options': None,
                            'optional': True,
                            'default_value': 2,
                            'value': None,
                            'secret': False,
                            'key': 'max_retries'
                        },
                        {
                            'description': 'Timeout for requests to OpenAI completion API.',
                            'type': 'float',
                            'options': None,
                            'optional': True,
                            'default_value': None,
                            'value': None,
                            'secret': False,
                            'key': 'request_timeout'
                        },
                        {
                            'description': 'Pricing per input token.',
                            'type': 'float',
                            'options': None,
                            'optional': False,
                            'default_value': 0.000_000_1,
                            'value': 0.000_000_1,
                            'secret': False,
                            'key': 'input_pricing'
                        },
                        {
                            'description': 'Pricing currency.',
                            'type': 'str',
                            'options': None,
                            'optional': False,
                            'default_value': 'USD',
                            'value': 'USD',
                            'secret': False,
                            'key': 'pricing_currency'
                        }
                    ]
                }
            ],
            'reranking': [],
            'speech2text': [],
            'tts': [],
            'text2img': [],
            'moderation': []
        }
    },
    {
        'supplier': 'HuggingFace',
        'mode': 2,
        'config': [
            {
                "key": "api_key",
                "type": "str",
                "value": "",
                "secret": True,
                "options": None,
                "optional": False,
                "description": "Automatically inferred from env var `HuggingFace_API_KEY` if not provided.",
                "default_value": ""
            },
            {
                'key': 'keep_separator',
                'type': 'selectable',
                'value': False,
                'secret': False,
                'options': [{'display': 'False', 'value': False}, {'display': 'start', 'value': 'start'},
                            {'display': 'end', 'value': 'end'}],
                'optional': False,
                'description': 'Whether to keep the separator and where to place it in each '
                               'corresponding chunk',
                'default_value': False
            },
            {
                'key': 'keep_separa123tor',
                'type': 'int',
                'value': 0,
                'secret': False,
                'options': None,
                'optional': False,
                'description': 'Whether to keep the separator and where to place it in each '
                               'corresponding chunk',
                'default_value': 0
            }
            ,
            {
                'key': 'keep_separ321ator',
                'type': 'float',
                'value': 0.1,
                'secret': False,
                'options': None,
                'optional': False,
                'description': 'Whether to keep the separator and where to place it in each '
                               'corresponding chunk',
                'default_value': 0.1
            }
        ],
        'models': {
            'text-generation': [],
            'embeddings': [
                {
                    'model_name': 'text2vec-large-chinese',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 0
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 0
                    },
                    'config': [
                        {
                            'key': 'type',
                            'type': 'str',
                            'value': 'Text2vecEmbeddings',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'description': None,
                            'default_value': 'Text2vecEmbeddings'
                        },
                        {
                            'key': 'model_name_or_path',
                            'type': 'str',
                            'value': '/home/duketxl/text2vec-large-chinese',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'description': 'The name of the model to load from the huggingface models '
                                           'library,\n'
                                           'or the path of the model to load from local storage.',
                            'default_value': ''
                        }
                    ]
                }
            ],
            'reranking': [
                {
                    'model_name': 'bge-reranker-v2-m3',
                    'config': [
                        {
                            'key': 'type',
                            'type': 'str',
                            'value': 'CrossEncoderReranker',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'description': None,
                            'default_value': 'CrossEncoderReranker'
                        },
                        {
                            'key': 'model_type',
                            'type': 'str',
                            'value': 'HuggingFaceCrossEncoder',
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'description': 'Type of CrossEncoder model to use for scoring similarity '
                                           'between the query and documents.',
                            'default_value': ''
                        },
                        {
                            'key': 'model_name',
                            'type': 'str',
                            'value': '/home/duketxl/bge-reranker-v2-m3',
                            'secret': False,
                            'options': None,
                            'optional': True,
                            'description': 'Model name or path of HuggingFaceCrossEncoder model.',
                            'default_value': None
                        },
                        {
                            'key': 'top_n',
                            'type': 'int',
                            'value': 3,
                            'secret': False,
                            'options': None,
                            'optional': False,
                            'description': 'Number of documents to return.',
                            'default_value': 3
                        }
                    ]
                }
            ],
            'speech2text': [],
            'tts': [],
            'text2img': [],
            'moderation': []
        }
    },
    {
        'supplier': 'Anthropic',
        'mode': 1,
        'config': [
            {
                "key": "api_key",
                "type": "str",
                "value": "",
                "secret": True,
                "options": None,
                "optional": False,
                "description": "Automatically inferred from env var `ANTHROPIC_API_KEY` if not provided.",
                "default_value": ""
            }
        ],
        'models': {
            'text-generation': [
                {
                    'model_name': 'claude-3-5-sonnet-latest',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 8192
                    },
                    'config': [
                        {
                            "key": "model_name",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "claude-3-haiku-20240307"
                        },
                        {
                            "key": "max_tokens_to_sample",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Denotes the number of tokens to predict per generation.",
                            "default_value": 1024
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "A non-negative float that tunes the degree of randomness in generation.",
                            "default_value": None
                        },
                        {
                            "key": "top_k",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of most likely tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "top_p",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Total probability mass of tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Timeout for requests to Anthropic Completion API.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of retries allowed for requests sent to the Anthropic Completion API.",
                            "default_value": 2
                        },
                        {
                            "key": "anthropic_api_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Headers to pass to the Anthropic clients, will be used for every API call.",
                            "default_value": None
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to use streaming or not.",
                            "default_value": False
                        }
                    ]
                },
                {
                    'model_name': 'claude-3-5-haiku-latest',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 8192
                    },
                    'config': [
                        {
                            "key": "model_name",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "claude-3-haiku-20240307"
                        },
                        {
                            "key": "max_tokens_to_sample",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Denotes the number of tokens to predict per generation.",
                            "default_value": 1024
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "A non-negative float that tunes the degree of randomness in generation.",
                            "default_value": None
                        },
                        {
                            "key": "top_k",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of most likely tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "top_p",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Total probability mass of tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Timeout for requests to Anthropic Completion API.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of retries allowed for requests sent to the Anthropic Completion API.",
                            "default_value": 2
                        },
                        {
                            "key": "anthropic_api_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Headers to pass to the Anthropic clients, will be used for every API call.",
                            "default_value": None
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to use streaming or not.",
                            "default_value": False
                        }
                    ]
                },
                {
                    'model_name': 'claude-3-opus-latest',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model_name",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "claude-3-haiku-20240307"
                        },
                        {
                            "key": "max_tokens_to_sample",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Denotes the number of tokens to predict per generation.",
                            "default_value": 1024
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "A non-negative float that tunes the degree of randomness in generation.",
                            "default_value": None
                        },
                        {
                            "key": "top_k",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of most likely tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "top_p",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Total probability mass of tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Timeout for requests to Anthropic Completion API.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of retries allowed for requests sent to the Anthropic Completion API.",
                            "default_value": 2
                        },
                        {
                            "key": "anthropic_api_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Headers to pass to the Anthropic clients, will be used for every API call.",
                            "default_value": None
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to use streaming or not.",
                            "default_value": False
                        }
                    ]
                },
                {
                    'model_name': 'claude-3-sonnet-20240229',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model_name",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "claude-3-haiku-20240307"
                        },
                        {
                            "key": "max_tokens_to_sample",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Denotes the number of tokens to predict per generation.",
                            "default_value": 1024
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "A non-negative float that tunes the degree of randomness in generation.",
                            "default_value": None
                        },
                        {
                            "key": "top_k",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of most likely tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "top_p",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Total probability mass of tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Timeout for requests to Anthropic Completion API.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of retries allowed for requests sent to the Anthropic Completion API.",
                            "default_value": 2
                        },
                        {
                            "key": "anthropic_api_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Headers to pass to the Anthropic clients, will be used for every API call.",
                            "default_value": None
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to use streaming or not.",
                            "default_value": False
                        }
                    ]
                },
                {
                    'model_name': 'claude-3-haiku-20240307',
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 200000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4096
                    },
                    'config': [
                        {
                            "key": "model_name",
                            "type": "str",
                            "value": "",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "claude-3-haiku-20240307"
                        },
                        {
                            "key": "max_tokens_to_sample",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Denotes the number of tokens to predict per generation.",
                            "default_value": 1024
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "A non-negative float that tunes the degree of randomness in generation.",
                            "default_value": None
                        },
                        {
                            "key": "top_k",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of most likely tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "top_p",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Total probability mass of tokens to consider at each step.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Timeout for requests to Anthropic Completion API.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of retries allowed for requests sent to the Anthropic Completion API.",
                            "default_value": 2
                        },
                        {
                            "key": "anthropic_api_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Headers to pass to the Anthropic clients, will be used for every API call.",
                            "default_value": None
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to use streaming or not.",
                            "default_value": False
                        }
                    ]
                }
            ],
            'embeddings': [],
            'reranking': [],
            'speech2text': [],
            'tts': [],
            'text2img': [],
            'moderation': []
        }
    },
{
        'supplier': 'Doubao',
        'mode': 1,
        'config': [
            {
                "key": "api_key",
                "type": "str",
                "value": "",
                "secret": True,
                "options": None,
                "optional": False,
                "description": "The API Key is an important credential for you to request the Volcano Ark large model service.",
                "default_value": ""
            },
            {
                "key": "base_url",
                "type": "str",
                "value": "https://ark.cn-beijing.volces.com/api/v3",
                "secret": False,
                "options": None,
                "optional": False,
                "description": "Base URL for API requests",
                "default_value": "https://ark.cn-beijing.volces.com/api/v3"
            }
        ],
        'models': {
            'text-generation': [
                {
                    'model_name': 'Doubao-1.5-pro-256k',  # 1
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 256000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 12000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "ep-20250213164639-kgtq2",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "ep-20250213164639-kgtq2"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'Doubao-1.5-pro-32k',   # 2
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 32000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 12000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "ep-20250213145156-lgdnr",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "ep-20250213145156-lgdnr"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'Doubao-1.5-lite-32k',  # 3
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 32000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 12000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "ep-20250213164550-m586m",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "ep-20250213164550-m586m"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'Doubao-pro-256k',      # 4
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 256000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "ep-20250213164639-kgtq2",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "ep-20250213164639-kgtq2"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                },
                {
                    'model_name': 'Doubao-lite-128k',     # 5
                    'max_context_tokens': {
                        "key": "max_context_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum context length for model.",
                        "default_value": 128000
                    },
                    'max_output_tokens': {
                        "key": "max_output_tokens",
                        "type": "int",
                        "value": "",
                        "secret": False,
                        "options": None,
                        "optional": False,
                        "description": "Maximum output length for model.",
                        "default_value": 4000
                    },
                    'config': [
                        {
                            "key": "model",
                            "type": "str",
                            "value": "ep-20250213164724-95xlf",
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Model name to use.",
                            "default_value": "ep-20250213164724-95xlf"
                        },
                        {
                            "key": "temperature",
                            "type": "float",
                            "value": 0.7,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "What sampling temperature to use.",
                            "default_value": 0.7
                        },
                        {
                            "key": "model_kwargs",
                            "type": "str",
                            "value": {},
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Holds any model parameters valid for `create` call not explicitly specified.",
                            "default_value": {}
                        },
                        {
                            "key": "base_url",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Base URL path for API requests, leave blank if not using a proxy or service emulator.",
                            "default_value": None
                        },
                        {
                            "key": "organization",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Automatically inferred from env var `OPENAI_ORG_ID` if not provided.",
                            "default_value": None
                        },
                        {
                            "key": "openai_proxy",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Supports explicit proxy for OpenAI.",
                            "default_value": None
                        },
                        {
                            "key": "timeout",
                            "type": "float",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Timeout for requests to OpenAI completion API. Can be float, httpx.Timeout or None.",
                            "default_value": None
                        },
                        {
                            "key": "max_retries",
                            "type": "int",
                            "value": 2,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Maximum number of retries to make when generating.",
                            "default_value": 2
                        },
                        {
                            "key": "streaming",
                            "type": "bool",
                            "value": False,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Whether to stream the results or not.",
                            "default_value": False
                        },
                        {
                            "key": "n",
                            "type": "int",
                            "value": 1,
                            "secret": False,
                            "options": None,
                            "optional": False,
                            "description": "Number of chat completions to generate for each prompt.",
                            "default_value": 1
                        },
                        {
                            "key": "max_tokens",
                            "type": "int",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Maximum number of tokens to generate.",
                            "default_value": None
                        },
                        {
                            "key": "tiktoken_model_name",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "The model name to pass to tiktoken when using this class.",
                            "default_value": None
                        },
                        {
                            "key": "default_headers",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default headers.",
                            "default_value": None
                        },
                        {
                            "key": "default_query",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default query.",
                            "default_value": None
                        },
                        {
                            "key": "http_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.Client. Only used for sync invocations. Must specify http_async_client as well if you'd like a custom client for async invocations.",
                            "default_value": None
                        },
                        {
                            "key": "http_async_client",
                            "type": "Any",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Optional httpx.AsyncClient. Only used for async invocations. Must specify http_client as well if you'd like a custom client for sync invocations.",
                            "default_value": None
                        },
                        {
                            "key": "stop_sequences",
                            "type": "str",
                            "value": None,
                            "secret": False,
                            "options": None,
                            "optional": True,
                            "description": "Default stop sequences.",
                            "default_value": None
                        }
                    ]
                }
            ],
            'embeddings': [],
            'reranking': [],
            'speech2text': [],
            'tts': [],
            'text2img': [],
            'moderation': []
        }
    }
]

retriever_config = [
    {
        'key': 'type',
        'description': None,
        'type': 'str',
        'optional': False,
        'default_value': 'VectorStoreRetriever',
        'value': settings.RETRIEVER_TYPE,
        'options': None,
        'secret': False,
    },
    {
        'key': 'k',
        'description': 'Amount of documents to return',
        'type': 'int',
        'optional': False,
        'default_value': 4,
        'value': settings.RETRIEVER_K,
        'options': None,
        'secret': False,
    },
    {
        'key': 'score_threshold',
        'description': 'Document similarity score threshold',
        'type': 'float',
        'optional': True,
        'default_value': 0.5,
        'value': settings.RETRIEVER_SCORE_THRESHOLD,
        'options': None,
        'secret': False,
    }
]

process_rule_config = [
    {
        'key': 'type',
        'type': 'str',
        'value': 'RecursiveCharacterTextSplitter',
        'secret': False,
        'options': None,
        'optional': False,
        'description': None,
        'default_value': 'RecursiveCharacterTextSplitter'
    },
    {
        'key': 'chunk_size',
        'type': 'int',
        'value': 400,
        'secret': False,
        'options': None,
        'optional': False,
        'description': 'Maximum size of chunks to return',
        'default_value': 400
    },
    {
        'key': 'chunk_overlap',
        'type': 'int',
        'value': 200,
        'secret': False,
        'options': None,
        'optional': False,
        'description': 'Overlap in characters between chunks',
        'default_value': 200
    },
    {
        'key': 'keep_separator',
        'type': 'selectable',
        'value': False,
        'secret': False,
        'options': [{'display': 'False', 'value': False}, {'display': 'start', 'value': 'start'},
                    {'display': 'end', 'value': 'end'}],
        'optional': False,
        'description': 'Whether to keep the separator and where to place it in each '
                       'corresponding chunk',
        'default_value': False
    },
    {
        'key': 'strip_whitespace',
        'type': 'bool',
        'value': True,
        'secret': False,
        'options': None,
        'optional': False,
        'description': 'If `True`, strips whitespace from the start and end of every '
                       'document',
        'default_value': True
    }
]

# Model type 1: text-generation 2: embeddings 3: reranking 4: speech2text 5: tts 6: text2img 7: moderation
model_type = {
    1: {
        'type': 'LLM'
    },
    2: {
        'type': 'EMBEDDING'
    },
    3: {
        'type': 'RERANK'
    },
    4: {
        'type': 'SPEECH2TEXT'
    },
    5: {
        'type': 'TTS'
    },
    6: {
        'type': 'TEXT2IMG'
    },
    7: {
        'type': 'MODERATION'
    }
}
enable_reranking_on_single_retrival = False
