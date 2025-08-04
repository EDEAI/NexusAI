import json
from copy import deepcopy

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatBaichuan
from langchain_aws import ChatBedrock
from langchain_community.llms.chatglm3 import ChatGLM3
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_community.llms import HuggingFaceHub
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain_community.chat_models import JinaChat
from langchain_community.chat_models import MiniMaxChat
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.chat_models.moonshot import MoonshotChat
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_models import ChatSparkLLM
from langchain_together import ChatTogether
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_google_vertexai import ChatVertexAI
from langchain_community.chat_models import VolcEngineMaasChat
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.chat_models import ChatZhipuAI
from .output_schemas import LLM_OUTPUT_SCHEMAS


class LLMPipeline:
    """
    Represents a pipeline for generating text using a language model.
    """

    def __init__(self, supplier: str, config: dict, schema_key: str = None):
        """
        Initializes an LLMPipeline object with a supplier and configuration dictionary.

        :param supplier: str, the name of the supplier to use for the pipeline.
        :param config: dict, a dictionary of configuration options for the supplier.
        :param schema_key: str, optional key to use specific schema from output_schemas.py.
        """
        self.supplier = supplier
        if self.supplier == 'Anthropic':
            # Get schema if schema_key is provided
            schema = None
            if schema_key:
                schema = LLM_OUTPUT_SCHEMAS[schema_key]

            # Check if model_kwargs contains JSON response format configuration
            if config.get('model_kwargs', {}).get('response_format') == {"type": "json_object"}:
                config['model_kwargs'].pop('response_format', None)

            # Initialize Anthropic with schema if available
            if schema:
                self.llm = ChatAnthropic(**config).with_structured_output(schema=schema, include_raw=True)
            else:
                self.llm = ChatAnthropic(**config)

        elif self.supplier == 'Azure_OpenAI':
            '''
           config = {
            "azure_endpoint": "https://example-resource.azure.openai.com/",  # Your Azure endpoint, including the resource
            # Automatically inferred from env var `AZURE_OPENAI_ENDPOINT` if not provided.
            # Example: `https://example-resource.azure.openai.com/`

            "azure_deployment": "your_deployment_name",  # A model deployment
            # If given sets the base client URL to include `/deployments/{azure_deployment}`.
            # Note: this means you won't be able to use non-deployment endpoints.

            "api_version": "2023-05-15",  # Automatically inferred from env var `OPENAI_API_VERSION` if not provided.
            "api_key": "your_api_key_here",  # Automatically inferred from env var `AZURE_OPENAI_API_KEY` if not provided.
            "azure_ad_token": "your_ad_token_here",  # Your Azure Active Directory token
            # Automatically inferred from env var `AZURE_OPENAI_AD_TOKEN` if not provided.
            # For more: https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id

            "azure_ad_token_provider": lambda: "your_token",  # A function that returns an Azure Active Directory token
            # Will be invoked on every request.

            "model_version": "1.0.0",    # Legacy, for openai<1.0.0 support
            "openai_api_type": "azure",  # Legacy, for openai<1.0.0 support
            "validate_base_url": True    # Whether to validate the base URL
        }
            '''
            self.llm = AzureChatOpenAI(**config)
        elif self.supplier == 'Baichuan':
            '''
            config = {
                "api_key": "your_api_key_here",  # Baichuan API Key
                "baichuan_secret_key": None,  # [DEPRECATED, keeping it for backward compatibility] Baichuan Secret Key
                "streaming": False,  # Whether to stream the results or not
                "timeout": 60,  # Request timeout for chat HTTP requests
                "model": "Baichuan2-Turbo-192K",  # Model name of Baichuan, default is `Baichuan2-Turbo-192K`, other options include `Baichuan2-Turbo`
                "temperature": 0.3,  # What sampling temperature to use
                "top_k": 5,  # What search sampling control to use
                "top_p": 0.85,  # What probability mass to use
                "with_search_enhance": False,  # Whether to use search enhance, default is False
                "model_kwargs":  # Holds any model parameters valid for API call not explicitly specified
            }
            '''
            self.llm = ChatBaichuan(**config)
        elif self.supplier == 'Bedrock':
            '''
            config = {
                "region_name": None,  # The AWS region e.g., `us-west-2`
                # Falls back to `AWS_DEFAULT_REGION` env variable or region specified in `~/.aws/config` if not provided here.

                "credentials_profile_name": None,  # The name of the profile in the ~/.aws/credentials or ~/.aws/config files
                # If not specified, the default credential profile or credentials from IMDS will be used. See:
                # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

                "config": None,  # An optional botocore.config.Config instance to pass to the client

                "provider": None,  # The model provider, e.g., amazon, cohere, ai21, etc.
                # When not supplied, provider is extracted from the first part of the model_id

                "model_id": "your_model_id",  # Id of the model to call, e.g., amazon.titan-text-express-v1

                "model_kwargs": {},  # Keyword arguments to pass to the model, initialized to an empty dictionary

                "endpoint_url": None,  # Needed if you don't want to default to us-east-1 endpoint

                "streaming": False,  # Whether to stream the results

                "provider_stop_sequence_key_name_map": {
                    "anthropic": "stop_sequences",
                    "amazon": "stopSequences",
                    "ai21": "stop_sequences",
                    "cohere": "stop_sequences",
                    "mistral": "stop_sequences",
                },  # Maps provider to stop sequence key name

                "provider_stop_reason_key_map": {
                    "anthropic": "stop_reason",
                    "amazon": "completionReason",
                    "ai21": "finishReason",
                    "cohere": "finish_reason",
                    "mistral": "stop_reason",
                },  # Maps provider to stop reason key name

                "guardrails": {
                    "trace": None,
                    "guardrailIdentifier": None,
                    "guardrailVersion": None,
                }  # Configuration dictionary for guardrails in Bedrock
            }
             '''
            self.llm = ChatBedrock(**config)
        elif self.supplier == 'ChatGLM':

            '''
           config = {
                "model": "chatglm3-6b",  # Model name, default is "chatglm3-6b"
                "endpoint_url": "http://127.0.0.1:8000/v1/chat/completions",  # Endpoint URL to use
                "model_kwargs": {},  # Keyword arguments to pass to the model, default is an empty dictionary
                "max_tokens": 20000,  # Max tokens allowed to pass to the model
                "temperature": 0.1,  # LLM model temperature from 0 to 10
                "top_p": 0.7,  # Top P for nucleus sampling from 0 to 1
                "prefix_messages": [],  # Series of messages for Chat input, default is an empty list
                "streaming": False,  # Whether to stream the results or not
                "http_client": None,  # HTTP client to use, default is None
                "timeout": DEFAULT_TIMEOUT  # Timeout for requests, default is 60 seconds
            } 
            '''
            self.llm = ChatGLM3(**config)
        elif self.supplier == 'Cohere':
            '''
            config = {
                "model": None,  # Model name to use
                "temperature": None,  # A non-negative float that tunes the degree of randomness in generation
                "cohere_api_key": None,  # Cohere API key. If not provided, will be read from the environment variable
                "stop": None,  # List of stop sequences
                "streaming": False,  # Whether to stream the results
                "user_agent": "langchain:partner",  # Identifier for the application making the request
                "timeout_seconds": 300,  # Timeout in seconds for the Cohere API request
                "base_url": None  # Override the default Cohere API URL
            }
            '''
            self.llm = ChatCohere(**config)
        elif self.supplier == 'Google':
            # Get schema if schema_key is provided
            schema = None
            if schema_key:
                schema = LLM_OUTPUT_SCHEMAS[schema_key]

            # Check if model_kwargs contains JSON response format configuration
            if config.get('model_kwargs', {}).get('response_format') == {"type": "json_object"}:
                config.pop('model_kwargs', None)

            # Initialize Google with schema if available
            if schema:
                self.llm = ChatGoogleGenerativeAI(**config).with_structured_output(schema=schema, include_raw=True)
            else:
                self.llm = ChatGoogleGenerativeAI(**config)
        elif self.supplier == 'Groq':
            '''
             config = {
                "model": "mixtral-8x7b-32768",  # The name of the model to use, default is "mixtral-8x7b-32768"
                "temperature": 0.7,  # Sampling temperature to use
                "model_kwargs": {},  # Holds any model parameters valid for `create` call not explicitly specified
                "api_key": None,  # Automatically inferred from env var `groq_API_KEY` if not provided
                "base_url": None,  # Base URL path for API requests, leave blank if not using a proxy or service emulator
                "groq_proxy": None,  # Explicit proxy for Groq
                "timeout": None,  # Timeout for requests to Groq completion API. Can be float, httpx.Timeout, or None
                "max_retries": 2,  # Maximum number of retries to make when generating
                "streaming": False,  # Whether to stream the results or not
                "n": 1,  # Number of chat completions to generate for each prompt
                "max_tokens": None,  # Maximum number of tokens to generate
                "default_headers": None,  # Default headers for HTTP requests, if any
                "default_query": None,  # Default query parameters for HTTP requests, if any
                "http_client": None,  # Optional httpx.Client
                "http_async_client": None  # Optional httpx.AsyncClient. Only used for async invocations
            }
            '''
            self.llm = ChatGroq(**config)
        elif self.supplier == 'Hugging_Face':

            '''
            config = {
                "llm": "your_llm_instance",  # LLM instance, must be of type HuggingFaceTextGenInference, HuggingFaceEndpoint, or HuggingFaceHub
                "system_message": SystemMessage(content=DEFAULT_SYSTEM_PROMPT),  # System message with default content
                "tokenizer": None,  # Tokenizer to use, if any
                "model_id": None,  # Optional model ID
                "streaming": False,  # Whether to stream the results or not
                 "repo_id": None,  # Model name to use. If not provided, the default model for the chosen task will be used.
                "task": None,  # Task to call the model with. Should be a task that returns `generated_text`, `summary_text`, or `translation_text`.
                "model_kwargs": None,  # Keyword arguments to pass to the model.
                "huggingfacehub_api_token": None  # API token for Hugging Face Hub.
            }
            ChatHuggingFce:
                {
                    "llm": "your_llm_instance",  # LLM instance, must be of type HuggingFaceTextGenInference, HuggingFaceEndpoint, or HuggingFaceHub
                    "system_message": SystemMessage(content=DEFAULT_SYSTEM_PROMPT),  # System message with default content
                    "tokenizer": None,  # Tokenizer to use, if any
                    "model_id": None,  # Optional model ID
                    "streaming": False  # Whether to stream the results or not
                }
            HuggingFaceHub :
                {
                    "repo_id": None,  # Model name to use. If not provided, the default model for the chosen task will be used.
                    "task": None,  # Task to call the model with. Should be a task that returns `generated_text`, `summary_text`, or `translation_text`.
                    "model_kwargs": None,  # Keyword arguments to pass to the model.
                    "huggingfacehub_api_token": None  # API token for Hugging Face Hub.
                }
            '''
            self.llm = ChatHuggingFace(system_message=config.get('system_message', None),
                                       tokenizer=config.get('tokenizer', None), model_id=config.get('model_id', None),
                                       streaming=config.get('streaming', None),
                                       llm=HuggingFaceHub(repo_id=config.get('repo_id', None),
                                                          task=config.get('task', None),
                                                          model_kwargs=config.get('model_kwargs', None),
                                                          huggingfacehub_api_token=config.get(
                                                              'huggingfacehub_api_token', None)))
        elif self.supplier == 'Jina':
            '''
            config = {
                "temperature": 0.7,  # What sampling temperature to use.
                "model_kwargs": {},  # Holds any model parameters valid for `create` call not explicitly specified.
                "jinachat_api_key": None,  # Base URL path for API requests, leave blank if not using a proxy or service emulator.
                "request_timeout": None,  # Timeout for requests to JinaChat completion API. Default is 600 seconds.
                "max_retries": 6,  # Maximum number of retries to make when generating.
                "streaming": False,  # Whether to stream the results or not.
                "max_tokens": None  # Maximum number of tokens to generate.
            }
            '''
            self.llm = JinaChat(**config)
        elif self.supplier == 'MiniMax':
            '''
            config = {
                "model": "abab6.5-chat",  # Model name to use.
                "max_tokens": 256,  # Denotes the number of tokens to predict per generation.
                "temperature": 0.7,  # A non-negative float that tunes the degree of randomness in generation.
                "top_p": 0.95,  # Total probability mass of tokens to consider at each step.
                "model_kwargs": {},  # Holds any model parameters valid for `create` call not explicitly specified.
                "base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",  # Minimax API host.
                "group_id": None,  # [DEPRECATED, keeping it for backward compatibility] Group Id.
                "api_key": "your_minimax_api_key",  # Minimax API Key (replace with your actual API key).
                "streaming": False  # Whether to stream the results or not.
            }
            '''
            self.llm = MiniMaxChat(**config)
        elif self.supplier == 'MistralAI':
            '''
            config = {
                "api_key": None,  # Mistral API Key.
                "endpoint": "https://api.mistral.ai/v1",  # API endpoint for Mistral.
                "max_retries": 5,  # Maximum number of retries for requests.
                "timeout": 120,  # Timeout for requests in seconds.
                "max_concurrent_requests": 64,  # Maximum number of concurrent requests.
                "model_name": "mistral-small",  # Model name to use.
                "temperature": 0.7,  # A non-negative float that tunes the degree of randomness in generation.
                "max_tokens": None,  # Maximum number of tokens to generate.
                "top_p": 1.0,  # Decode using nucleus sampling: consider the smallest set of tokens whose probability sum is at least top_p.
                "random_seed": None,  # Optional random seed for reproducibility.
                "safe_mode": False,  # Whether to enable safe mode.
                "streaming": False  # Whether to stream the results or not.
            }
            '''
            self.llm = ChatMistralAI(**config)
        elif self.supplier == 'Moonshot':
            '''
            config = {
                "base_url": "https://api.moonshot.cn/v1",
                "api_key": SecretStr("your_moonshot_api_key"),  # Replace with your actual API key
                "model": "moonshot-v1-8k",
                "max_tokens": 1024,
                "temperature": 0.5  # Adjust temperature for more or less creativity
            }
            '''
            self.llm = MoonshotChat(**config)
        elif self.supplier == 'NVIDIA':
            '''
           config = {
                "base_url": "https://integrate.api.nvidia.com/v1",  # Base URL for model listing and invocation.
                "model": _default_model,  # Name of the model to invoke.
                "temperature": None,  # Sampling temperature in [0, 1].
                "max_tokens": 1024,  # Maximum number of tokens to generate.
                "top_p": None,  # Top-p for distribution sampling.
                "seed": None,  # The seed for deterministic results.
                "stop": None  # Stop words (cased).
            }
            '''
            self.llm = ChatNVIDIA(**config)
        elif self.supplier == 'Ollama':
            '''
            config = {
                "mirostat": None,  # Enable Mirostat sampling for controlling perplexity. (default: 0, 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0)
                "mirostat_eta": None,  # Influences how quickly the algorithm responds to feedback from the generated text. (Default: 0.1)
                "mirostat_tau": None,  # Controls the balance between coherence and diversity of the output. (Default: 5.0)
                "num_ctx": None,  # Sets the size of the context window used to generate the next token. (Default: 2048)
                "num_gpu": None,  # The number of GPUs to use. On macOS it defaults to 1 to enable metal support, 0 to disable.
                "num_thread": None,  # Sets the number of threads to use during computation. It is recommended to set this value to the number of physical CPU cores your system has.
                "num_predict": None,  # Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context)
                "repeat_last_n": None,  # Sets how far back for the model to look back to prevent repetition. (Default: 64, 0 = disabled, -1 = num_ctx)
                "repeat_penalty": None,  # Sets how strongly to penalize repetitions. (Default: 1.1)
                "temperature": None,  # The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)
                "stop": None,  # Sets the stop tokens to use.
                "tfs_z": None,  # Tail free sampling is used to reduce the impact of less probable tokens from the output. (default: 1)
                "top_k": None,  # Reduces the probability of generating nonsense. (Default: 40)
                "top_p": None,  # Works together with top-k. (Default: 0.9)
                "system": None,  # System prompt (overrides what is defined in the Modelfile).
                "template": None,  # Full prompt or prompt template (overrides what is defined in the Modelfile).
                "format": None,  # Specify the format of the output (e.g., json).
                "timeout": None,  # Timeout for the request stream.
                "keep_alive": None,  # How long the model will stay loaded into memory.
                "raw": None,  # Raw or not. (Default: 5 minutes)
                "headers": None  # Additional headers to pass to endpoint.
            }
            '''
            self.llm = ChatOllama(**config)
        elif self.supplier in ['OpenAI', 'Doubao']:
            self.llm = ChatOpenAI(**config)
        elif self.supplier == 'Spark':
            '''
            config = {
                "app_id": "your_iflytek_spark_app_id",  # Automatically inferred from env var `IFLYTEK_SPARK_APP_ID` if not provided.
                "api_key": "your_iflytek_spark_api_key",  # Automatically inferred from env var `IFLYTEK_SPARK_API_KEY` if not provided.
                "api_secret": "your_iflytek_spark_api_secret",  # Automatically inferred from env var `IFLYTEK_SPARK_API_SECRET` if not provided.
                "api_url": "https://api.iflytek.com/v1",  # Base URL path for API requests, leave blank if not using a proxy or service emulator.
                "model": "your_model_name",  # Model name to use.
                "spark_user_id": "lc_user",  # Spark user identifier.
                "streaming": False,  # Whether to stream the results or not.
                "timeout": 30,  # Request timeout for chat HTTP requests (example value: 30 seconds).
                "temperature": 0.5,  # What sampling temperature to use (example value: 0.5).
                "top_k": 4,  # What search sampling control to use (example value: 4).
                "model_kwargs": {"param1": "value1", "param2": "value2"}  # Holds any model parameters valid for API call not explicitly specified.
            }
            '''
            self.llm = ChatSparkLLM(**config)
        elif self.supplier == 'Together_AI':
            '''
            config = {
                "model": "meta-llama/Llama-3-8b-chat-hf",  # Model name to use.
                "api_key": "your_together_api_key",  # Automatically inferred from env var `TOGETHER_API_KEY` if not provided.
                "base_url": "https://api.together.ai/v1/",  # Base URL path for API requests, leave blank if not using a proxy or service emulator.
            }
            '''
            self.llm = ChatTogether(**config)
        elif self.supplier == 'Tongyi':
            '''
               config = {
                "model": "qwen-turbo",  # Model name to use.
                "model_kwargs": {},  # Additional keyword arguments for the model.
                "top_p": 0.8,  # Total probability mass of tokens to consider at each step.
                "api_key": None,  # Dashscope API key provided by Alibaba Cloud.
                "streaming": False,  # Whether to stream the results or not.
                "max_retries": 10,  # Maximum number of retries to make when generating.
            }
            '''
            self.llm = ChatTongyi(**config)
        elif self.supplier == 'VertexAI':
            '''
            config = {
                "model": "chat-bison",  # Underlying model name.
                "examples": None,  # Optional. List of example messages.
                "convert_system_message_to_human": False,  # Deprecated. Setting this parameter to True is discouraged since new Gemini models support System Messages.
                "response_mime_type": None,  # Optional. Output response mimetype of the generated candidate text. Supported in Gemini 1.5 and later models.
            }
            '''
            self.llm = ChatVertexAI(**config)
        elif self.supplier == 'VolcEngineMaas':
            '''
            config = {
                "volc_engine_maas_ak": None,  # Access key for Volc Engine.
                "volc_engine_maas_sk": None,  # Secret key for Volc Engine.
                "endpoint": "maas-api.ml-platform-cn-beijing.volces.com",  # Endpoint of the VolcEngineMaas LLM.
                "region": "Region",  # Region of the VolcEngineMaas LLM.
                "model": "skylark-lite-public",  # Model name. More details at https://www.volcengine.com/docs/82379/1133187.
                "model_version": None,  # Model version. Relevant for moonshot large language model. Details at https://www.volcengine.com/docs/82379/1158281.
                "top_p": 0.8,  # Total probability mass of tokens to consider at each step.
                "temperature": 0.95,  # Degree of randomness in generation.
                "model_kwargs": {},  # Model special arguments, detailed on the model page.
                "streaming": False,  # Whether to stream the results.
                "connect_timeout": 60,  # Timeout for connecting to the Volc Engine Maas endpoint. Default is 60 seconds.
                "read_timeout": 60,  # Timeout for reading response from the Volc Engine Maas endpoint. Default is 60 seconds.
            }
            '''
            self.llm = VolcEngineMaasChat(**config)
        elif self.supplier == 'Qianfan':
            '''
            config = {
                "init_kwargs": {},  # Initialization kwargs for Qianfan client, such as 'query_per_second' to limit QPS.
                "model_kwargs": {},  # Extra parameters for model invocation using 'do'.
                "api_key": None,  # Qianfan API KEY.
                "secret_key": None,  # Qianfan SECRET KEY.
                "streaming": False,  # Whether to stream the results or not.
                "timeout": 60,  # Request timeout for chat HTTP requests.
                "top_p": 0.8,  # Total probability mass to consider.
                "temperature": 0.95,  # Degree of randomness in generation.
                "penalty_score": 1,  # Model parameter, supported in ERNIE-Bot and ERNIE-Bot-turbo.
                "model": "ERNIE-Bot-turbo",  # Model name. Preset models map to an endpoint. Default is ERNIE-Bot-turbo.
                "endpoint": None,  # Endpoint of the Qianfan LLM, required if a custom model is used.
            }
            '''
            self.llm = QianfanChatEndpoint(**config)
        elif self.supplier == 'ZhipuAI':
            '''
            config = {
                "api_key": None,  # Automatically inferred from env var `ZHIPUAI_API_KEY` if not provided.
                "api_base": None,  # Base URL path for API requests. Leave blank if not using a proxy or service emulator.
                "model": "glm-4",  # Model name to use. See https://open.bigmodel.cn/dev/api#language. Can use any fine-tuned model from the GLM series.
                "temperature": 0.95,  # Sampling temperature. Ranges from 0.0 to 1.0, cannot be 0. Larger values yield more randomness and creativity.
                "top_p": 0.7,  # Nuclear sampling. Ranges from 0.0 to 1.0, cannot be 0 or 1. The model considers tokens from the top_p probability quality.
                "streaming": False,  # Whether to stream the results or not.
                "max_tokens": None,  # Maximum number of tokens to generate.
            }
            '''
            self.llm = ChatZhipuAI(**config)
        else:
            raise ValueError(f"Unsupported supplier: {supplier}")

    def chain(self, messages):
        """
        Create a pipeline chain based on the type of messages provided.

        :param messages: str or list, the messages to use for the pipeline chain.
        :return: the pipeline chain.
        """
        if isinstance(messages, str):
            return self.create_llm_chain(messages)
        elif isinstance(messages, list):
            return self.create_chat_chain(messages)
        else:
            # Handle other types or raise an error if necessary
            raise TypeError("Unsupported type for prompt")

    def create_llm_chain(self, message: str):
        """
        Create a pipeline chain for a language model prompt.

        :param message: str, the message to use for the pipeline chain.
        :return: the pipeline chain.
        """
        prompt_template = PromptTemplate.from_template(message)
        llm_chain = prompt_template | self.llm
        return llm_chain

    def create_chat_chain(self, messages: list):
        """
        Create a pipeline chain for a chat prompt.

        :param messages: list, the message to use for the pipeline chain.
        :return: the pipeline chain.
        """
        prompt_template = ChatPromptTemplate.from_messages(messages)
        llm_chain = prompt_template | self.llm
        return llm_chain

    def _convert_messages_for_tongyi(self, messages):
        """
        Convert standard message format to Tongyi vision format.
        Transforms image_url format to Tongyi's expected format.
        
        Args:
            messages: List of messages or single message to convert
            
        Returns:
            Converted messages compatible with Tongyi vision models
        """
        if not isinstance(messages, list):
            return messages
            
        converted_messages = []
        
        for message in messages:
            # Only convert HumanMessage with content list that contains images
            if hasattr(message, 'content') and isinstance(message.content, list):
                converted_content = []
                
                for item in message.content:
                    if isinstance(item, dict):
                        # Convert standard image_url format to Tongyi format
                        if item.get('type') == 'image_url' and 'image_url' in item:
                            image_url = item['image_url']['url']
                            converted_content.append({"image": image_url})
                        # Convert standard text format to Tongyi format
                        elif item.get('type') == 'text' and 'text' in item:
                            converted_content.append({"text": item['text']})
                        # Keep other formats as-is
                        else:
                            converted_content.append(item)
                    else:
                        converted_content.append(item)
                
                # Create new message with converted content
                converted_message = deepcopy(message)
                converted_message.content = converted_content
                converted_messages.append(converted_message)
            else:
                # Keep non-list content messages as-is
                converted_messages.append(message)
                
        return converted_messages

    def standardize_response(self, response):
        """
        Standardize the response format to match OpenAI's structure.
        Handles different types of responses:
        1. Anthropic responses (structured/unstructured output)
        2. Google responses (structured output with tool calls)
        3. Tongyi responses (with token usage from response metadata)
        Other suppliers' responses are returned as-is.

        Args:
            response: The response from the LLM model.

        Returns:
            A standardized response with content and token usage information.
        """
        if self.supplier == 'Anthropic':
            # Handle structured output when schema is defined (include_raw=True format)
            if isinstance(response, dict) and 'raw' in response:
                raw_response = response['raw']
                usage_metadata = raw_response.usage_metadata

                # Create standardized response
                standardized_response = type('StandardizedResponse', (), {
                    'content': json.dumps(response['parsed'], ensure_ascii=False),
                    'response_metadata': {
                        'token_usage': {
                            'prompt_tokens': usage_metadata.get('input_tokens', 0),
                            'completion_tokens': usage_metadata.get('output_tokens', 0),
                            'total_tokens': usage_metadata.get('total_tokens', 0)
                        }
                    }
                })
                return standardized_response

            # Handle regular unstructured output
            content = response.content
            usage_metadata = response.usage_metadata
            
            standardized_response = type('StandardizedResponse', (), {
                'content': content,
                'response_metadata': {
                    'token_usage': {
                        'prompt_tokens': usage_metadata.get('input_tokens', 0),
                        'completion_tokens': usage_metadata.get('output_tokens', 0),
                        'total_tokens': usage_metadata.get('total_tokens', 0)
                    }
                }
            })
            return standardized_response

        elif self.supplier == 'Google':
            # Handle structured output when schema is defined (include_raw=True format)
            if isinstance(response, dict) and 'raw' in response:
                raw_response = response['raw']
                usage_metadata = raw_response.usage_metadata
                
                # Extract content from raw response
                content = ""
                if hasattr(raw_response, 'additional_kwargs') and raw_response.additional_kwargs:
                    function_call = raw_response.additional_kwargs.get('function_call')
                    if function_call and 'arguments' in function_call:
                        content = function_call['arguments']
                
                # Create standardized response
                standardized_response = type('StandardizedResponse', (), {
                    'content': content,
                    'response_metadata': {
                        'token_usage': {
                            'prompt_tokens': usage_metadata.get('input_tokens', 0),
                            'completion_tokens': usage_metadata.get('output_tokens', 0),
                            'total_tokens': usage_metadata.get('total_tokens', 0)
                        }
                    }
                })
                return standardized_response
            
            # Handle regular unstructured output
            content = response.content
            usage_metadata = response.usage_metadata
            
            standardized_response = type('StandardizedResponse', (), {
                'content': content,
                'response_metadata': {
                    'token_usage': {
                        'prompt_tokens': usage_metadata.get('input_tokens', 0),
                        'completion_tokens': usage_metadata.get('output_tokens', 0),
                        'total_tokens': usage_metadata.get('total_tokens', 0)
                    }
                }
            })
            return standardized_response

        elif self.supplier == 'Tongyi':
            # Handle Tongyi responses
            content = response.content
            
            # Extract token usage from response metadata
            token_usage = {}
            if hasattr(response, 'response_metadata') and response.response_metadata:
                metadata_token_usage = response.response_metadata.get('token_usage', {})
                token_usage = {
                    'prompt_tokens': metadata_token_usage.get('input_tokens', 0),
                    'completion_tokens': metadata_token_usage.get('output_tokens', 0),
                    'total_tokens': metadata_token_usage.get('total_tokens', 0)
                }
            
            standardized_response = type('StandardizedResponse', (), {
                'content': content,
                'response_metadata': {
                    'token_usage': token_usage
                }
            })
            return standardized_response

        return response

    def invoke(self, messages, input={}):
        """
        Invoke the pipeline chain with the provided prompt.

        Args:
            messages: str or list, the messages to use for the pipeline chain.
            input: dict, optional input parameters for the chain.

        Returns:
            The standardized output of the pipeline chain.
        """
        # Convert messages for Tongyi if needed
        if self.supplier == 'Tongyi':
            messages = self._convert_messages_for_tongyi(messages)
            
        response = self.chain(messages).invoke(input)
        return self.standardize_response(response)
    
    def invoke_llm(self, messages, **kwargs):
        """
        Invoke the LLM model with the provided prompt.
        """
        # Convert messages for Tongyi if needed
        if self.supplier == 'Tongyi':
            messages = self._convert_messages_for_tongyi(messages)
            
        response = self.llm.invoke(messages, **kwargs)
        return self.standardize_response(response)

    def astream_llm(self, messages, **kwargs):
        """
        Stream the LLM model with the provided prompt.
        """
        # Convert messages for Tongyi if needed
        if self.supplier == 'Tongyi':
            messages = self._convert_messages_for_tongyi(messages)
            
        # Handle Google/Gemini supplier streaming issue
        if self.supplier == 'Google':
            # For Google, create async wrapper for synchronous streaming
            async def async_stream_wrapper():
                try:
                    # Use synchronous streaming to avoid astream bug
                    for chunk in self.llm.stream(messages, **kwargs):
                        yield chunk
                except Exception as e:
                    # If streaming fails, fallback to regular invoke
                    print(f"Google streaming error: {e}. Falling back to regular invoke.")
                    result = self.llm.invoke(messages, **kwargs)
                    yield result
            
            return async_stream_wrapper()
        else:
            response = self.llm.astream(messages, **kwargs)
            return response

