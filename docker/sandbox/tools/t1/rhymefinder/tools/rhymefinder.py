from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
from dify_plugin.entities.tool import ToolInvokeMessage

class RhymefinderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get input parameters
        word = tool_parameters.get("word", "")
        match_type = tool_parameters.get("match_type", "full")
        syllable_filter = tool_parameters.get("syllable_filter", "all")
        result_count = tool_parameters.get("result_count", 10)
        model_config = tool_parameters.get("model", {})
        
        # Ensure result_count is within limits
        result_count = max(5, min(500, result_count))
        
        # Skip debug information in production
        
        if not word:
            yield self.create_text_message("Please provide an English word to find rhymes for.")
            return
        
        # Skip intermediate progress messages, wait for final results only
        # Comment out the original progress message code
        # yield self.create_text_message(f"Finding rhyming words for '{word}'... This may take a moment.")
        
        # Construct the prompt prefix
        prompt_prefix = """You are a rhyming word expert. Your task is to find words that rhyme with a given English word.

For each rhyming word, provide:
1. The rhyming word itself
2. The number of syllables in the word
3. A song example where this rhyming word is used (in the format "Song Title - Artist")

IMPORTANT: You must provide a comprehensive variety of rhyming words with different syllable counts. For each syllable count, provide as many good options as possible.

Return your response as a JSON array with the following structure:
[
  {
    "word": "example",
    "syllables": 3,
    "song_example": "Song Title - Artist"
  }
]

Only include words that genuinely rhyme with the input word. For each word, try to provide a real song example where possible.
Ensure your response is valid JSON with no additional text or explanations."""

        # Add syllable filter instruction
        syllable_instruction = ""
        if syllable_filter != "all":
            try:
                syllable_count = int(syllable_filter)
                syllable_instruction = f"\nOnly include words with EXACTLY {syllable_count} syllable(s)."
                prompt_prefix += syllable_instruction
            except ValueError:
                pass
        
        # Add result count instruction
        prompt_prefix += f"\n\nProvide at least {result_count} rhyming words if possible."
        
        match_type_instruction = ""
        if match_type == "full":
            match_type_instruction = "Find words that fully rhyme with the input word (matching all syllables)."
        elif match_type == "partial":
            match_type_instruction = "Find words that partially rhyme with the input word (matching only the last syllables)."
        
        # Combine prefix and user input into a single prompt
        combined_prompt = f"{prompt_prefix}\n\nFind rhyming words for: {word}\n{match_type_instruction}"
        
        try:
            # Use the selected model from the model-selector with streaming enabled
            
            # Skip intermediate progress messages, wait for final results only
            # Comment out the original progress message code
            # yield self.create_text_message(f"Generating rhyming words for '{word}'...")
            
            # Use streaming for better user experience
            response_stream = self.session.model.llm.invoke(
                model_config=model_config,
                prompt_messages=[
                    UserPromptMessage(content=combined_prompt)
                ],
                stream=True  # Enable streaming for better user experience
            )
            
            # Collect the full response
            full_response = ""
            for chunk in response_stream:
                if chunk.delta and chunk.delta.message and chunk.delta.message.content:
                    full_response += chunk.delta.message.content
            
            # Parse LLM response
            rhyming_words_text = full_response
            
            # Create table format output
            table_data = {
                "rhyming_words": []
            }
            
            # Parse JSON response
            try:
                # Clean up the response if needed
                clean_json = rhyming_words_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                clean_json = clean_json.strip()
                
                rhyme_list = json.loads(clean_json)
                
                for item in rhyme_list:
                    table_data["rhyming_words"].append({
                        "word": item.get("word", ""),
                        "syllables": item.get("syllables", 0),
                        "song_example": item.get("song_example", "")
                    })
                
                # Filter by syllable count if specified
                if syllable_filter != "all":
                    try:
                        target_syllable = int(syllable_filter)
                        table_data["rhyming_words"] = [
                            item for item in table_data["rhyming_words"]
                            if item["syllables"] == target_syllable
                        ]
                    except ValueError:
                        pass
                
                # Return JSON format result
                yield self.create_json_message(table_data)
                
                # Create a variable for use in workflows
                yield self.create_variable_message("rhyming_words", table_data["rhyming_words"])
                
                # Create a text message for direct display in chat
                text_result = f"Found {len(table_data['rhyming_words'])} rhyming words for '{word}':\n\n"
                
                # Group words by syllable count
                words_by_syllables = {}
                for item in table_data["rhyming_words"]:
                    syllable_count = item['syllables']
                    if syllable_count not in words_by_syllables:
                        words_by_syllables[syllable_count] = []
                    words_by_syllables[syllable_count].append(item)
                
                # Display words grouped by syllable count
                for syllable_count in sorted(words_by_syllables.keys()):
                    words = words_by_syllables[syllable_count]
                    text_result += f"### {syllable_count} Syllable Words ({len(words)})\n\n"
                    text_result += "| Rhyming Word | Song Example |\n"
                    text_result += "|-------------|-------------|\n"
                    
                    for item in words:
                        text_result += f"| {item['word']} | {item['song_example']} |\n"
                    
                    text_result += "\n"
                
                yield self.create_text_message(text_result)
                
            except json.JSONDecodeError as json_err:
                # If JSON parsing fails, try to extract text content
                error_msg = f"Could not parse LLM response as JSON: {str(json_err)}\nRaw response:\n{rhyming_words_text[:500]}..."
                yield self.create_text_message(error_msg)
                
        except Exception as e:
            error_msg = f"Error processing rhyming words: {str(e)}"
            yield self.create_text_message(error_msg)
