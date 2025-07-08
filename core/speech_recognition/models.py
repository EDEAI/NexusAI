import os
import uuid
import datetime
from typing import List, Optional, Union, Dict, Any, Tuple

from openai import OpenAI

class SpeechRecognition:
    """
    A class that handles AI-powered speech recognition using OpenAI's Whisper models.
    """

    def __init__(self, supplier: str, config: dict):
        """
        Initializes a SpeechRecognition object with a supplier and configuration dictionary.

        :param supplier: str, the name of the speech recognition service provider.
        :param config: dict, a dictionary of configuration options for the supplier.
        :raises ValueError: If the supplier is not supported.
        """
        self.supplier = supplier
        self.config = config
        
        if self.supplier == 'OpenAI':
            self.client = OpenAI(**config)
        else:
            raise ValueError(f"Unsupported supplier: {supplier}")

    def _process_openai_transcription_response(self, response, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes OpenAI API response data for speech recognition, extracting key information.
        
        :param response: The complete response object from OpenAI API
        :param model_config: Dict[str, Any], optional configuration for transcription processing
        :return: Dict[str, Any], processed result containing:
            - text: The transcribed text
            - input_audio_tokens: Audio tokens from input_token_details
            - prompt_tokens: Text tokens from input_token_details  
            - completion_tokens: Output tokens
            - total_tokens: Sum of all token counts
        """
        model_config = model_config or {}
        
        # Extract text content
        text = ""
        if hasattr(response, 'text'):
            text = response.text
        
        # Initialize token counts
        input_audio_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        
        # Extract usage information
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            
            # Handle both dict and object access patterns
            if isinstance(usage, dict):
                # Dict access
                total_tokens = usage.get("total_tokens", 0)
                input_tokens = usage.get("input_tokens", 0)
                completion_tokens = usage.get("output_tokens", 0)
                
                # Extract detailed input token information
                input_token_details = usage.get("input_token_details", {})
                if input_token_details:
                    input_audio_tokens = input_token_details.get("audio_tokens", 0)
                    prompt_tokens = input_token_details.get("text_tokens", 0)
                else:
                    input_audio_tokens = input_tokens
                    prompt_tokens = 0
            else:
                # Object access
                total_tokens = getattr(usage, "total_tokens", 0)
                input_tokens = getattr(usage, "input_tokens", 0)
                completion_tokens = getattr(usage, "output_tokens", 0)
                
                # Extract detailed input token information
                if hasattr(usage, 'input_token_details') and usage.input_token_details:
                    input_details = usage.input_token_details
                    input_audio_tokens = getattr(input_details, "audio_tokens", 0)
                    prompt_tokens = getattr(input_details, "text_tokens", 0)
                else:
                    input_audio_tokens = input_tokens
                    prompt_tokens = 0
        
        # Prepare final result
        result = {
            "text": text,
            "input_audio_tokens": input_audio_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
        
        return result

    def transcribe_audio(self, audio_file_path: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Transcribes audio from a file using OpenAI's Whisper models.
        
        :param audio_file_path: str, path to the audio file to be transcribed.
        :param model_config: Dict[str, Any], optional configuration for the transcription.
            Supports the following keys:
            - model: str, model to use for transcription (default: "whisper-1")
            - language: str, language of the input audio (ISO-639-1 format)
            - prompt: str, optional text to guide the model's style
            - response_format: str, format of the response ("json", "text", "srt", "verbose_json", "vtt")
            - temperature: float, sampling temperature (0 to 1)
            - timestamp_granularities: list, granularities for timestamps (["word", "segment"])
            - other model-specific parameters
        
        :return: Dict[str, Any], containing:
            - text: str, the transcribed text
            - input_audio_tokens: int, audio tokens from input_token_details
            - prompt_tokens: int, text tokens from input_token_details
            - completion_tokens: int, output tokens
            - total_tokens: int, sum of all token counts

        :raises ValueError: If the supplier is not supported.
        :raises FileNotFoundError: If the audio_file_path doesn't exist.
        """
        if self.supplier == 'OpenAI':
            model_config = model_config or {}
            
            # Set default model if not specified
            if 'model' not in model_config:
                model_config['model'] = 'whisper-1'
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
            try:
                with open(audio_file_path, "rb") as audio_file:
                    response = self.client.audio.transcriptions.create(
                        file=audio_file,
                        **model_config
                    )
                    print(response)
                return self._process_openai_transcription_response(response, model_config)
            except Exception as e:
                # Provide more detailed error information
                print(f"Error during audio transcription: {str(e)}")
                # Re-raise the exception after logging
                raise
        else:
            raise ValueError(f"Unsupported supplier: {self.supplier}")