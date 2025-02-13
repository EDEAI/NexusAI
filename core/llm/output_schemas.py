
LLM_OUTPUT_SCHEMAS = {
    # Anthropic output schemas
    "Anthropic": {
        "agent_system_prompt_with_auto_match_ability": {
            "name": "agent_system_prompt_with_auto_match_ability",
            "description": "Agent's response with ability ID and corresponding output",
            "input_schema": {
                "type": "object",
                "properties": {
                    "ability_id": {
                        "type": "integer",
                        "description": "The ID of the selected ability"
                    },
                    "output": {
                        "type": "string",
                        "description": "The content replied in the corresponding format of the ability"
                    }
                },
                "required": ["ability_id", "output"]
            }
        }
        # Add more Anthropic output schemas here as needed
    }
    # Add more LLM provider output schemas here as needed
}
