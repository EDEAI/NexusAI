from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from rdkit import Chem
from rdkit.Chem import Descriptors

class WeightFromSmiles(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        smile_str = tool_parameters.get("smiles", "")
        if not smile_str :
            yield self.create_json_message({
                "error": "No SMILES string provided."
            })
            return
        m = Chem.MolFromSmiles(smile_str)
        weight = Descriptors.MolWt(m)
        yield self.create_json_message(
            {
            "molecular_weight":weight
            }
        )
