from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import pandas as pd
import io
import base64

# 独立函数，不要放在类里

def safe_read_csv(file_like):
    for encoding in ["utf-8", "gbk", "gb2312", "latin1"]:
        try:
            return pd.read_csv(file_like, encoding=encoding)
        except Exception:
            file_like.seek(0)
    raise ValueError("无法识别的CSV文件编码，请保存为UTF-8或GBK后重试。")

class MergeToMultisheet(Tool):
    def _invoke(self, tool_parameters: dict):
        csv_files = tool_parameters.get("csv_files", [])
        if not csv_files:
            yield self.create_text_message("请上传至少一个文件")
            return

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for f in csv_files:
                ext = getattr(f, "extension", None)
                ext = ext.lstrip('.').lower() if ext else ""
                name = getattr(f, "filename", None) or getattr(f, "name", "Sheet")
                # 读取内容
                file_content = None
                if hasattr(f, "blob") and f.blob:
                    file_content = f.blob
                    if isinstance(file_content, str):
                        try:
                            file_content = base64.b64decode(file_content)
                        except Exception:
                            file_content = file_content.encode("utf-8")
                elif hasattr(f, "read"):
                    file_content = f.read()
                    if isinstance(file_content, str):
                        file_content = file_content.encode("utf-8")
                else:
                    continue
                if not file_content:
                    continue
                if ext == "csv":
                    file_like = io.BytesIO(file_content)
                    df = safe_read_csv(file_like)
                elif ext in ["xls", "xlsx"]:
                    df = pd.read_excel(io.BytesIO(file_content))
                else:
                    continue
                # sheet名不能超过31字符
                df.to_excel(writer, sheet_name=name[:31], index=False)
        output.seek(0)
        yield self.create_blob_message(
            blob=output.getvalue(),
            meta={
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "file_name": "merged_multisheet.xlsx"
            }
        )
        output.close()