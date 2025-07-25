import re
from typing import List, Tuple


# ref: https://github.com/fla9ua/markdown_to_mrkdwn
class SlackMarkdownConverter:
    """
    A converter class to transform Markdown text into Slack's mrkdwn format.

    Attributes:
        encoding (str): The character encoding used for the conversion.
        patterns (List[Tuple[str, str]]): A list of regex patterns and their replacements.
    """

    def __init__(self, encoding="utf-8"):
        """
        Initializes the SlackMarkdownConverter with a specified encoding.

        Args:
            encoding (str): The character encoding to use for the conversion. Default is 'utf-8'.
        """
        self.encoding = encoding
        self.in_code_block = False
        self.table_replacements = {}
        # Use compiled regex patterns for better performance
        self.patterns: List[Tuple[re.Pattern, str]] = [
            (
                re.compile(r"^(\s*)- \[([ ])\] (.+)", re.MULTILINE),
                r"\1• ☐ \3",
            ),  # Unchecked task list
            (
                re.compile(r"^(\s*)- \[([xX])\] (.+)", re.MULTILINE),
                r"\1• ☑ \3",
            ),  # Checked task list
            (re.compile(r"^(\s*)- (.+)", re.MULTILINE), r"\1• \2"),  # Unordered list
            (
                re.compile(r"^(\s*)(\d+)\. (.+)", re.MULTILINE),
                r"\1\2. \3",
            ),  # Ordered list
            (re.compile(r"!\[.*?\]\((.+?)\)", re.MULTILINE), r"<\1>"),  # Images to URL
            (
                re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", re.MULTILINE),
                r"_\1_",
            ),  # Italic
            (re.compile(r"^###### (.+)$", re.MULTILINE), r"*\1*"),  # H6 as bold
            (re.compile(r"^##### (.+)$", re.MULTILINE), r"*\1*"),  # H5 as bold
            (re.compile(r"^#### (.+)$", re.MULTILINE), r"*\1*"),  # H4 as bold
            (re.compile(r"^### (.+)$", re.MULTILINE), r"*\1*"),  # H3 as bold
            (re.compile(r"^## (.+)$", re.MULTILINE), r"*\1*"),  # H2 as bold
            (re.compile(r"^# (.+)$", re.MULTILINE), r"*\1*"),  # H1 as bold
            (
                re.compile(r"(^|\s)~\*\*(.+?)\*\*(\s|$)", re.MULTILINE),
                r"\1 *\2* \3",
            ),  # Bold with space handling
            (re.compile(r"(?<!\*)\*\*(.+?)\*\*(?!\*)", re.MULTILINE), r"*\1*"),  # Bold
            (re.compile(r"__(.+?)__", re.MULTILINE), r"*\1*"),  # Underline as bold
            (re.compile(r"\[(.+?)\]\((.+?)\)", re.MULTILINE), r"<\2|\1>"),  # Links
            (re.compile(r"`(.+?)`", re.MULTILINE), r"`\1`"),  # Inline code
            (re.compile(r"^> (.+)", re.MULTILINE), r"> \1"),  # Blockquote
            (
                re.compile(r"^(---|\*\*\*|___)$", re.MULTILINE),
                r"──────────",
            ),  # Horizontal line
            (re.compile(r"~~(.+?)~~", re.MULTILINE), r"~\1~"),  # Strikethrough
        ]
        # Placeholders for triple emphasis
        self.triple_start = "%%BOLDITALIC_START%%"
        self.triple_end = "%%BOLDITALIC_END%%"

    def convert(self, markdown: str) -> str:
        """
        Convert Markdown text to Slack's mrkdwn format.

        Args:
            markdown (str): The Markdown text to convert.

        Returns:
            str: The converted text in Slack's mrkdwn format.
        """
        if not markdown:
            return ""

        try:
            markdown = markdown.strip()

            self.table_replacements = {}

            markdown = self._convert_tables(markdown)

            lines = markdown.split("\n")
            converted_lines = [self._convert_line(line) for line in lines]
            result = "\n".join(converted_lines)

            for placeholder, table in self.table_replacements.items():
                result = result.replace(placeholder, table)

            return result.encode(self.encoding).decode(self.encoding)
        except Exception as e:
            # Log the error for debugging
            return markdown

    def _convert_tables(self, markdown: str) -> str:
        """
        Convert Markdown tables to Slack's mrkdwn format.

        Args:
            markdown (str): The Markdown text containing tables.

        Returns:
            str: The text with tables converted to Slack's format.
        """
        table_pattern = re.compile(
            r"^\|(.+)\|\s*$\n^\|[-:| ]+\|\s*$(\n^\|.+\|\s*$)*", re.MULTILINE
        )

        def convert_table(match):
            original_table = match.group(0)

            table_lines = original_table.strip().split("\n")
            header_line = table_lines[0]
            separator_line = table_lines[1]
            data_lines = table_lines[2:] if len(table_lines) > 2 else []

            headers = [cell.strip() for cell in header_line.strip("|").split("|")]

            rows = []
            for line in data_lines:
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                rows.append(cells)

            result = []
            result.append(" | ".join(f"*{header}*" for header in headers))

            for row in rows:
                result.append(" | ".join(row))

            placeholder = f"%%TABLE_PLACEHOLDER_{hash(original_table)}%%"
            self.table_replacements[placeholder] = "\n".join(result)
            return placeholder

        return table_pattern.sub(convert_table, markdown)

    def _convert_line(self, line: str) -> str:
        """
        Convert a single line of Markdown.

        Args:
            line (str): A single line of Markdown text.

        Returns:
            str: The converted line in Slack's mrkdwn format.
        """
        if line.startswith("%%TABLE_PLACEHOLDER_") and line.endswith("%%"):
            return line

        code_block_match = re.match(r"^```(\w*)$", line)
        if code_block_match:
            language = code_block_match.group(1)
            self.in_code_block = not self.in_code_block
            if self.in_code_block and language:
                return f"```{language}"
            return "```"

        if self.in_code_block:
            return line

        line = re.sub(
            r"(?<!\*)\*\*\*([^*\n]+?)\*\*\*(?!\*)",
            lambda m: f"{self.triple_start}{m.group(1)}{self.triple_end}",
            line,
        )

        for pattern, replacement in self.patterns:
            line = pattern.sub(replacement, line)

        line = re.sub(
            re.escape(self.triple_start) + r"(.*?)" + re.escape(self.triple_end),
            r"*_\1_*",
            line,
            flags=re.MULTILINE,
        )

        return line.rstrip()
