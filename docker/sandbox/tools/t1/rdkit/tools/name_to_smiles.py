from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests

class NameToSmiles(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        chemical_name = tool_parameters.get("molecule_name", "")
        if not chemical_name:
            yield self.create_json_message({
                "error": "No Molecule name provided."
            })
            return
        get_smile_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{chemical_name}/property/CanonicalSMILES/JSON"
        response = requests.get(get_smile_url)
        response_json = response.json()
        canonical_smiles = response_json["PropertyTable"]["Properties"][0].get("CanonicalSMILES","Sorry No SMILES found")
        
        yield self.create_json_message(
            {
            "smiles":canonical_smiles
            }
        )
