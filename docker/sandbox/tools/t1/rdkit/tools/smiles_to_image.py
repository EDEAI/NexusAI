from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from rdkit import Chem
from rdkit.Chem import Draw
from .utils import pil_image_to_base64

class SmilesToImage(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        smiles = tool_parameters.get("smiles", "")
        if not smiles:
            yield self.create_json_message({
                "error": "No SMILES string provided."
            })
            return
        m = Chem.MolFromSmiles(smiles)
        img = Draw.MolToImage(m)
        img_byte = pil_image_to_base64(img)
        yield self.create_blob_message(
            blob=img_byte,
            meta={
            "mime_type":"image/png"}
        )
