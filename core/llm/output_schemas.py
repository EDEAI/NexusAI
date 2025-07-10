LLM_OUTPUT_SCHEMAS = {
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
    },
    "recursive_task_generation": {
        "name": "recursive_task_generation",
        "description": "Task data with hierarchical recursive structure",
        "input_schema": {
            "type": "object",
            "$defs": {
                "task": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Task ID with format 'task-{parent_ids}-{current_id}'"
                        },
                        "name": {
                            "type": "string",
                            "description": "Task name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "keywords": {
                            "type": "string",
                            "description": "Task keywords separated by commas"
                        },
                        "task": {
                            "type": "string",
                            "description": "Specific task content"
                        },
                        "subcategories": {
                            "type": "array",
                            "items": {
                                "$ref": "#/$defs/task"
                            },
                            "description": "Sub-task list with same structure as parent"
                        }
                    },
                    "required": ["id", "name", "description", "keywords", "task", "subcategories"],
                }
            },
            "$ref": "#/$defs/task"
        }
    },
    "chatroom_manager_system": {
        "name": "chatroom_manager_system",
        "description": "Meeting room manager's summary and next agent selection",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Summary of the user's message content"
                },
                "id": {
                    "type": "integer",
                    "description": "The ID of the selected agent for the next response"
                }
            },
            "required": ["summary", "id"]
        }
    },
    "chatroom_manager_system_with_optional_selection": {
        "name": "chatroom_manager_system_with_optional_selection",
        "description": "Meeting room manager's agent selection or conversation end decision",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "description": "The ID of the selected agent (or 0 to end conversation)"
                },
                "message": {
                    "type": "string",
                    "description": "Reason for ending conversation (only required when id is 0)"
                }
            },
            "required": ["id"]
        }
    },
    "generate_agent_system_prompt": {
        "name": "generate_agent_system_prompt",
        "description": "Agent generation assistant's output format",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Agent name"
                },
                "description": {
                    "type": "string",
                    "description": "Agent description"
                },
                "obligations": {
                    "type": "string",
                    "description": "Agent functional information (including identity, responsibilities, skills, etc)"
                },
                "abilities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Ability name"
                            },
                            "content": {
                                "type": "string",
                                "description": "Specific content of the ability"
                            },
                            "output_format": {
                                "type": "integer",
                                "description": "Output format: 1-text, 2-json, 3-code"
                            }
                        },
                        "required": ["name", "content", "output_format"]
                    },
                    "description": "List of agent abilities"
                }
            },
            "required": ["name", "description", "obligations", "abilities"]
        }
    },
    "chatroom_conference_orientation_system": {
        "name": "chatroom_conference_orientation_system",
        "description": "Convert meeting summary to oriented data structure",
        "input_schema": {
            "type": "object",
            "properties": {
                "variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name corresponding to the split item"
                            },
                            "required": {
                                "type": "integer",
                                "description": "Whether the variable is required"
                            },
                            "display_name": {
                                "type": "string",
                                "description": "Variable display name for the split item"
                            },
                            "type": {
                                "type": "string",
                                "description": "Variable type: number or string"
                            },
                            "value": {
                                "type": "string",
                                "description": "Content of the work-oriented split item"
                            }
                        },
                        "required": ["name", "required", "display_name", "type", "value"]
                    },
                    "description": "List of oriented data variables"
                }
            },
            "required": ["variables"]
        }
    },
    "generate_skill_system_prompt": {
        "name": "generate_skill_system_prompt",
        "description": "Python tool generation assistant's output format",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Tool name"
                },
                "description": {
                    "type": "string",
                    "description": "Tool description"
                },
                "input_variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name that follows code naming conventions"
                            },
                            "type": {
                                "type": "string",
                                "description": "Variable type: 'string' or 'number'"
                            },
                            "required": {
                                "type": "boolean",
                                "description": "Whether the variable is required"
                            },
                            "display_name": {
                                "type": "string",
                                "description": "Variable display name describing its function"
                            }
                        },
                        "required": ["name", "type", "required", "display_name"]
                    },
                    "description": "List of input variables"
                },
                "dependencies": {
                    "type": "object",
                    "properties": {
                        "python3": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of Python package dependencies"
                        }
                    }
                },
                "code": {
                    "type": "object",
                    "properties": {
                        "python3": {
                            "type": "string",
                            "description": "Python 3 implementation code"
                        }
                    }
                },
                "output_type": {
                    "type": "integer",
                    "description": "Output type: 1-text/variable, 2-database, 3-code, 4-file"
                },
                "output_variables": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Variable name that follows code naming conventions"
                            },
                            "type": {
                                "type": "string",
                                "description": "Variable type: 'string', 'number', or 'json'"
                            },
                            "display_name": {
                                "type": "string",
                                "description": "Variable display name describing its function"
                            }
                        },
                        "required": ["name", "type", "display_name"]
                    },
                    "description": "List of output variables"
                }
            },
            "required": ["name", "description", "input_variables", "dependencies", "code", "output_type", "output_variables"]
        }
    }
}
