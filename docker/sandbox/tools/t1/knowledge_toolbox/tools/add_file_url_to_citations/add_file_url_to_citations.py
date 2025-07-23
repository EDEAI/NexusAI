from collections.abc import Generator
from typing import Any
import requests
import ast
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AddFileURLToCitationsTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_base_url = tool_parameters.get("api_base_url")
        api_key = tool_parameters.get("api_key")
        context = tool_parameters.get("context")
        format = tool_parameters.get("format", "full")

        # convert str to list of dictionaries
        try:
            context = ast.literal_eval(context)
        except Exception as e:
            yield self.create_text_message("Invalid context format. Please provide a valid context.")
            return

        # gather all documents in context
        documents = []
        for citation in context:
            documents.append({
                "dataset_id": citation.get("metadata").get("dataset_id"),
                "document_id": citation.get("metadata").get("document_id"),
            })
        documents = [dict(t) for t in {tuple(d.items()) for d in documents}]

        # get the download url for each document
        headers = {
            "authorization": f"bearer {api_key}",
            "content-type": "application/json",
        }
        for document in documents:
            url = f"{api_base_url.rstrip('/')}/datasets/{document['dataset_id']}/documents/{document['document_id']}/upload-file"
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                pass

            document["download_url"] = data.get("download_url", "")
            document['name'] = data.get("name", "")
            document['size'] = data.get("size", 0)
            document['mime_type'] = data.get("mime_type", "")

        # full: inject download urls into original context
        if format == "full":
            for citation in context:
                for document in documents:
                    if (citation.get("metadata").get("dataset_id") == document.get("dataset_id") and
                            citation.get("metadata").get("document_id") == document.get("document_id")):
                        citation["metadata"]["download_url"] = document.get(
                            "download_url")
            yield self.create_text_message(json.dumps(context, ensure_ascii=False))

        # minimal_json: return only referenced documents with download urls
        elif format == "minimal_json":
            yield self.create_text_message(json.dumps(documents, ensure_ascii=False))

        # minimal_markdown: return list of documents with download urls in markdown format
        elif format == "minimal_markdown":
            list = []
            for document in documents:
                list.append(
                    f"- [{document.get('name')}]({document.get('download_url')})")
            yield self.create_text_message("\n".join(list))

        # chunks_html: group by documents, attach chunks, and output as HTML details
        elif format == "chunks_markdown":
            from html import unescape

            doc_dict = {}
            for citation in context:
                meta = citation.get("metadata", {})
                key = (meta.get("dataset_id"), meta.get("document_id"))
                if key not in doc_dict:
                    doc_info = next((d for d in documents if d.get("dataset_id") == key[0] and d.get("document_id") == key[1]), {})
                    doc_dict[key] = {
                        "name": meta.get("document_name", doc_info.get("name", "")),
                        "download_url": doc_info.get("download_url", ""),
                        "chunks": []
                    }
                doc_dict[key]["chunks"].append(citation.get("content", ""))

            html_blocks = []
            for doc in doc_dict.values():
                doc_name = doc.get("name", "")
                download_url = doc.get("download_url", "")
                block = f"<details>\n<summary>{doc_name} ({len(doc['chunks'])})</summary>\n\n"
                block += f"💾 [{doc_name}]({download_url})\n\n"
                for i, content in enumerate(doc["chunks"]):
                    content = unescape(content)
                    quoted = "\n".join(["> " + line for line in content.splitlines()])
                    block += quoted
                    if i != len(doc["chunks"]) - 1:
                        block += "\n\n"
                block += "\n</details>"
                html_blocks.append(block)
            yield self.create_text_message("\n\n".join(html_blocks))
