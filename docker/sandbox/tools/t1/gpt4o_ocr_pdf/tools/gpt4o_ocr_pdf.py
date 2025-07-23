from collections.abc import Generator
import io
import base64
from typing import Any
import fitz  # PyMuPDF
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI, OpenAI

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class Gpt4oOcrPdfTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if not self.runtime or not self.runtime.credentials:
            raise Exception("Tool runtime or credentials are missing")
        
        # Get credentials
        api_key = str(self.runtime.credentials.get("api_key", "")).strip()
        api_type = str(self.runtime.credentials.get("api_type", "azure")).strip().lower()
        
        # Check if API key is provided
        if not api_key:
            raise ValueError("API key is missing")
        
        # Initialize variables for client creation
        client = None
        model_name = "gpt-4o"
        
        # Create appropriate client based on API type
        if api_type == "azure":
            endpoint = str(self.runtime.credentials.get("api_endpoint", "")).strip()
            deployment_name = str(self.runtime.credentials.get("deployment_name", "")).strip()
            api_version = str(self.runtime.credentials.get("api_version", "")).strip()
            
            # Check Azure-specific credentials
            if not endpoint:
                raise ValueError("Azure API endpoint is missing")
            if not deployment_name:
                raise ValueError("Azure deployment name is missing")
            if not api_version:
                raise ValueError("Azure API version is missing")
                
            # Use deployment name as the model name for Azure
            model_name = deployment_name
        else:  # OpenAI
            # For OpenAI, we can use the default model name (gpt-4o) or get it from credentials
            model_name = str(self.runtime.credentials.get("model_name", "gpt-4o")).strip()

        # Get file
        file = tool_parameters.get("upload_file")
        if not file:
            raise ValueError("PDF file is required")
        
        file_binary = io.BytesIO(file.blob)
        
        # Extract images from PDF
        pdf_document = fitz.open(stream=file_binary, filetype="pdf")
        
        # Prepare system message for OCR
        system_message = """You are an expert OCR system. Your task is to:
            1. Extract all text content from the provided PDF images
            2. Preserve the document structure including headings, paragraphs, lists, and tables
            3. Format the output in clean Markdown
            4. Maintain the original formatting as much as possible
            5. Handle any tables by converting them to Markdown tables
            6. Preserve bullet points and numbered lists
            7. Include image captions if present

            Output only the Markdown content without any explanations or additional text."""
        
        # Process PDF pages
        all_images = []
        all_markdown = []
        
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Get page as an image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution for better OCR
            img_bytes = pix.tobytes(output="png")
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            all_images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            })
            
            # If we have accumulated several pages or reached the end, process them in batches
            if len(all_images) >= 5 or page_num == len(pdf_document) - 1:
                # Create appropriate client based on API type
                if api_type == "azure":
                    client = AzureOpenAI(
                        api_version=api_version,
                        azure_endpoint=endpoint,
                        api_key=api_key
                    )
                else:  # OpenAI
                    client = OpenAI(
                        api_key=api_key
                    )
                
                # Call GPT-4o API for OCR
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Extract the text from these PDF pages and convert to Markdown format. Preserve the original structure and formatting as much as possible."},
                        *all_images
                    ]}
                ]
                
                response = client.chat.completions.create(
                    model=model_name,  # Use the appropriate model name based on API type

                    messages=messages,
                    temperature=0.0,
                    max_tokens=4000
                )                
                # Extract markdown content from response
                markdown_content = response.choices[0].message.content
                
               
                # If the content is wrapped in markdown code blocks, extract just the content
                if markdown_content.startswith("```markdown") and markdown_content.endswith("```"):
                    markdown_content = markdown_content[len("```markdown"):].rstrip("```").strip()
                elif markdown_content.startswith("```") and markdown_content.endswith("```"):
                    markdown_content = markdown_content[len("```"):].rstrip("```").strip()
                               
                # Add markdown content to our collection
                all_markdown.append(markdown_content)
                
                # Reset images for next batch
                all_images = []
        
        # Combine all markdown content and return the final result
        final_markdown = "\n\n".join(all_markdown)
        
        # Return the markdown content as plain text
        yield self.create_text_message(final_markdown)
