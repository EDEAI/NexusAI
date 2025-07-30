from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from rdkit import Chem
from rdkit.Chem import Draw
from .utils import pil_image_to_base64
from rdkit.Chem import AllChem

class VisualizeChemicalReaction(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        smart_str = tool_parameters.get("smarts", "")
        if not smart_str:
            yield self.create_json_message({
                "error": "No SMARTS string provided."
            })
            return
        rxn = AllChem.ReactionFromSmarts(smart_str,useSmiles=True)
        d2d = Draw.MolDraw2DCairo(800,300)
        d2d.DrawReaction(rxn)
        img_byte = d2d.GetDrawingText()
        
        yield self.create_blob_message(
            blob=img_byte,
            meta={
            "mime_type":"image/png"}
        )
