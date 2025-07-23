import re

from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WordCountTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """

        # extract tool_parameters
        text = tool_parameters.get("text", "").strip()
        if not text:
            yield self.create_text_message("Invalid text")
            return

        try:
            # 行数
            lines = text.splitlines()
            # 非空行数（排除空行、只有空格的行、只有不可见字符的行）
            lines_non_empty = [line for line in lines if line.strip()]
            # 总字符数
            chars_total = len(text)
            # 可见字符数（排除不可见字符）
            chars_visible = len([c for c in text if c.isprintable()])
            # 非空字符数（排除不可见字符和空格字符）
            chars_non_whitespace = len([c for c in text if c.isprintable() and not c.isspace()])
            # 不包含标点符号的中英文字符数（排除标点符号）
            chars_non_punctuation = len(re.findall(r'[A-Za-z0-9\u4e00-\u9fff]', text))
            # 英文字母数
            chars_letter = len(re.findall(r'[A-Za-z]', text))
            # 中文字符数
            chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
            # 英文单词数
            english_words = len(re.findall(r'[A-Za-z]+', text))

            result = {
                "lines": len(lines),
                "lines_non_empty": len(lines_non_empty),
                "chars_total": chars_total,
                "chars_visible": chars_visible,
                "chars_non_whitespace": chars_non_whitespace,
                "chars_non_punctuation": chars_non_punctuation,
                "chars_letter": chars_letter,
                "chinese_chars": chinese_chars,
                "english_words": english_words
            }

            yield self.create_json_message(json=result)
            for key, value in result.items():
                yield self.create_variable_message(variable_name=key, variable_value=str(value))
        except Exception as e:
            yield self.create_text_message(f"Failed to count words, error: {str(e)}")
