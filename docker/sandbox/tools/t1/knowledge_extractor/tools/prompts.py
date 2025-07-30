EXTRACT_KNOWLEDGE_PROMPT = """Analyze this page as if you're studying from a book.

SKIP content if the page contains:
- Table of contents
- Chapter listings
- Index pages
- Blank pages
- Copyright information
- Publishing details
- References or bibliography
- Acknowledgments

DO extract knowledge if the page contains:
- Preface content that explains important concepts
- Actual educational content
- Key definitions and concepts
- Important arguments or theories
- Examples and case studies
- Significant findings or conclusions
- Methodologies or frameworks
- Critical analyses or interpretations

For valid content:
- Set has_content to true
- Extract detailed, learnable knowledge points
- Include important quotes or key statements
- Capture examples with their context
- Preserve technical terms and definitions

For pages to skip:
- Set has_content to false
- Return empty knowledge list

### Instructions
Some extra information are provided below, You should always follow the instructions as possible.
<instructions>
{instruction}
</instructions>

### Output Structure
Here is the structure of the expected output, You should always follow the output structure.
{output_structure}

### Page text
Inside <text></text> XML tags, there is a text that you should extract knowledge and convert to a JSON object.
<text>
{text}
</text>

### Answer in {language}
You should always output a valid JSON object. Output nothing other than the JSON object.
```JSON
"""

ANALYZE_KNOWLEDGE_PROMPT = """Create a comprehensive summary of the provided content in a concise but detailed way, using markdown format.

Use markdown formatting:
- ## for main sections
- ### for subsections
- Bullet points for lists
- `code blocks` for any code or formulas
- **bold** for emphasis
- *italic* for terminology
- > blockquotes for important notes

Return only the markdown summary, nothing else. Do not say 'here is the summary' or anything like that before or after.

Instructions:
Some extra information are provided below, You should always follow the instructions as possible.
<instructions>
{instruction}
</instructions>

Analyze this content:
<content>
{content}
</content>

Answer in {language}:
"""  # noqa: E501


OUTPUT_STRUCTURE = {
    "has_content": "(type: boolean)",
    "knowledge": "(type: array of string)"
}
