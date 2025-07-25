from collections.abc import Generator
from typing import Any
import json

import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class KnowledgeTool(Tool):
    def _validate_pre_processing_rules(self, pre_processing_rules: list | None):
        if pre_processing_rules is None:
            raise ValueError("Process rule pre_processing_rules is required")
        for rule in pre_processing_rules:
            if not rule.get("id"):
                raise ValueError("Process rule pre_processing_rules id is required")
            if not isinstance(rule.get("enabled"), bool):
                raise ValueError("Process rule pre_processing_rules enabled is invalid, must be a boolean")

    def _validate_segmentation_rules(self, segmentation: dict | None, mode: str, parent_mode: str | None):
        if segmentation is None:
            raise ValueError("Process rule segmentation is required")

        separator = segmentation.get("separator")
        if separator is None:
            raise ValueError("Process rule segmentation separator is required")
        if not isinstance(separator, str):
            raise ValueError("Process rule segmentation separator is invalid, must be a string")

        # max_tokens is required unless mode is hierarchical and parent_mode is full-doc
        if not (mode == "hierarchical" and parent_mode == "full-doc"):
            max_tokens = segmentation.get("max_tokens")
            if max_tokens is None:
                raise ValueError("Process rule segmentation max_tokens is required")
            if not isinstance(max_tokens, int):
                raise ValueError("Process rule segmentation max_tokens is invalid, must be an integer")

    def _validate_process_rule_structure(self, process_rule: dict[str, Any]):
        mode = process_rule.get("mode")
        if mode not in ["automatic", "custom", "hierarchical"]:
            raise ValueError(f"Invalid process_rule mode: {mode}")

        if mode in ["custom", "hierarchical"]:
            rules = process_rule.get("rules")
            if not rules:
                raise ValueError("Process rule rules is required for custom or hierarchical mode")

            self._validate_pre_processing_rules(rules.get("pre_processing_rules"))
            self._validate_segmentation_rules(rules.get("segmentation"), mode, rules.get("parent_mode"))

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        base_url = self.runtime.credentials.get("api_uri")
        headers = {"Authorization": f"Bearer {self.runtime.credentials.get("api_secret")}", "Content-Type": "application/json"}
        url = f"{base_url}/datasets/{tool_parameters.get("dataset_id")}/document/create-by-text"

        data = {
            "text": tool_parameters.get("text"),
            "name": tool_parameters.get("name"),
            "indexing_technique": tool_parameters.get("indexing_technique"),
            "doc_form": tool_parameters.get("doc_form"),
            "doc_language": tool_parameters.get("doc_language"),
        }

        process_rule_str = tool_parameters.get("process_rule")
        try:
            process_rule = json.loads(process_rule_str)
            self._validate_process_rule_structure(process_rule)
            data["process_rule"] = process_rule
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format for process_rule: {e}")
        except Exception as e:
            raise ValueError(f"Invalid process_rule: {e}")

        response = httpx.post(url, headers=headers, json=data)

        yield self.create_json_message(response.json())
