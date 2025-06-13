"""
APP Converter

This module provides functions to convert skills and workflows to MCP (Model Context Protocol) tool format.
"""

from typing import Any, Dict, List


def skill_to_mcp_tool(skill_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a skill to MCP tool format.
    
    Args:
        skill_data: Dictionary containing skill information with format:
            {
                "id": skill_id,
                "name": skill_name,
                "description": skill_description,
                "input_variables": {
                    "name": "input_var",
                    "type": "object",
                    "properties": {
                        variable_name: {
                            "name": "Name of the variable",
                            "required": bool,
                            "display_name": "Display name",
                            "type": "number" or "string",
                            "value": ""
                        }
                    }
                }
            }
    
    Returns:
        Dictionary in MCP tool format
    """
    # Extract basic information
    skill_id = skill_data.get("id")
    skill_name = skill_data.get("name")
    skill_description = skill_data.get("description", f"Execute skill {skill_name}")
    
    # Build input schema properties
    properties = {
        "input_variables": {
            "type": "object",
            "description": "Input variables for the skill",
            "properties": {},
            "required": []
        }
    }
    
    # Required fields for the main schema
    required_fields = ["input_variables"]
    
    # Process input variables if they exist
    input_variables = skill_data.get("input_variables", {})
    if input_variables and "properties" in input_variables:
        var_properties = {}
        var_required = []
        
        for var_name, var_info in input_variables["properties"].items():
            # Map variable type to JSON Schema type
            var_type = var_info.get("type", "string")
            if var_type == "number":
                json_type = "number"
            else:
                json_type = "string"
            
            var_properties[var_name] = {
                "type": json_type,
                "description": var_info.get("display_name", var_info.get("name", f"Input variable {var_name}"))
            }
            
            # Add to required if necessary
            if var_info.get("required", False):
                var_required.append(var_name)
        
        properties["input_variables"]["properties"] = var_properties
        if var_required:
            properties["input_variables"]["required"] = var_required
    
    # Build MCP tool format
    mcp_tool = {
        "name": f'nexusai__skill-{skill_id}-{skill_name}',
        "description": skill_description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required_fields
        }
    }
    
    return mcp_tool


def workflow_to_mcp_tool(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a workflow to MCP tool format.
    
    Args:
        workflow_data: Dictionary containing workflow information with format:
            {
                "id": workflow_id,
                "name": workflow_name,
                "description": workflow_description,
                "need_confirm_nodes": [
                    {
                        "node_id": node_id,
                        "node_name": node_name,
                        "node_desc": node_description
                    }
                ],
                "input_variables": {
                    "name": "input_var",
                    "type": "object",
                    "properties": {
                        variable_name: {
                            "name": "Name of the variable",
                            "required": bool,
                            "display_name": "Display name",
                            "type": "number" or "string",
                            "value": ""
                        }
                    }
                }
            }
    
    Returns:
        Dictionary in MCP tool format
    """
    # Extract basic information
    workflow_id = workflow_data.get("id")
    workflow_name = workflow_data.get("name")
    workflow_description = workflow_data.get("description", f"Execute workflow {workflow_name}")
    
    # Build input schema properties
    properties = {
        "node_confirm_users": {
            "type": "object",
            "description": "Node confirmation user mapping, key is node ID, value is confirming user ID",
            "properties": {},
            "required": []
        },
        "input_variables": {
            "type": "object",
            "description": "Input variables for the workflow",
            "properties": {},
            "required": []
        }
    }
    
    # Required fields for the main schema
    required_fields = ["input_variables"]
    
    # Process need_confirm_nodes if they exist
    need_confirm_nodes = workflow_data.get("need_confirm_nodes", [])
    if need_confirm_nodes:
        node_properties = properties["node_confirm_users"]["properties"]
        node_required = properties["node_confirm_users"]["required"]
        for node in need_confirm_nodes:
            node_id = node.get("node_id")
            node_name = node.get("node_name", f"Node {node_id}")
            node_desc = node.get("node_desc", "")
            
            node_properties[str(node_id)] = {
                "type": "integer",
                "description": f"Confirming user ID for node '{node_name}'{': ' + node_desc if node_desc else ''}"
            }
            node_required.append(str(node_id))
        if node_properties:
            required_fields.append("node_confirm_users")
    
    # Process input variables if they exist
    input_variables = workflow_data.get("input_variables", {})
    if input_variables and "properties" in input_variables:
        var_properties = {}
        var_required = []
        
        for var_name, var_info in input_variables["properties"].items():
            # Map variable type to JSON Schema type
            var_type = var_info.get("type", "string")
            if var_type == "number":
                json_type = "number"
            else:
                json_type = "string"
            
            var_properties[var_name] = {
                "type": json_type,
                "description": var_info.get("display_name", var_info.get("name", f"Input variable {var_name}"))
            }
            
            # Add to required if necessary
            if var_info.get("required", False):
                var_required.append(var_name)
        
        properties["input_variables"]["properties"] = var_properties
        if var_required:
            properties["input_variables"]["required"] = var_required
    
    # Build MCP tool format
    mcp_tool = {
        "name": f'nexusai__workflow-{workflow_id}-{workflow_name}',
        "description": workflow_description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required_fields
        }
    }
    
    return mcp_tool


def convert_callable_items_to_mcp_tools(
    callable_skills: List[Dict[str, Any]], 
    callable_workflows: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convert lists of callable skills and workflows to MCP tools format.
    
    Args:
        callable_skills: List of skill dictionaries
        callable_workflows: List of workflow dictionaries
    
    Returns:
        List of MCP tools
    """
    mcp_tools = []
    
    # Convert skills
    for skill in callable_skills:
        mcp_tool = skill_to_mcp_tool(skill)
        mcp_tools.append(mcp_tool)
    
    # Convert workflows
    for workflow in callable_workflows:
        mcp_tool = workflow_to_mcp_tool(workflow)
        mcp_tools.append(mcp_tool)
    
    return mcp_tools
