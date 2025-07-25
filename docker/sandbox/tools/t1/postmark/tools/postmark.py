from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class PostmarkTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Send an email using Postmark API"""
        # Get the default from email from credentials
        from_email = self.runtime.credentials.get("default_from_email", "")
            
        to_email = tool_parameters.get("to_email", "")
        subject = tool_parameters.get("subject", "")
        html_body = tool_parameters.get("html_body", "")
        cc = tool_parameters.get("cc", "")
        bcc = tool_parameters.get("bcc", "")
        
        # Validate required parameters
        if not from_email:
            yield self.create_text_message("From email is required.")
            return
            
        if not to_email:
            yield self.create_text_message("To email is required.")
            return
            
        if not subject:
            yield self.create_text_message("Subject is required.")
            return
            
        if not html_body:
            yield self.create_text_message("HTML body is required.")
            return
            
        try:
            # Get server token from credentials
            server_token = self.runtime.credentials.get("server_token")
            if not server_token:
                yield self.create_text_message("Postmark server token is required.")
                return
                
            # Prepare the email payload
            payload = {
                "From": from_email,
                "To": to_email,
                "Subject": subject,
                "MessageStream": "outbound"
            }
            
            # Add HTML body to payload
            payload["HtmlBody"] = html_body
                
            if cc:
                payload["Cc"] = cc
                
            if bcc:
                payload["Bcc"] = bcc
            
            # Set up headers
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": server_token
            }
            
            # Send the email
            response = requests.post(
                "https://api.postmarkapp.com/email",
                json=payload,
                headers=headers
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Create a success response
                success_message = f"Email sent successfully to {to_email}"
                if result.get("MessageID"):
                    success_message += f" (Message ID: {result.get('MessageID')})"
                
                yield self.create_text_message(success_message)
                yield self.create_json_message(result)
            else:
                error_message = f"Failed to send email. Status code: {response.status_code}"
                if response.json().get("Message"):
                    error_message += f". {response.json().get('Message')}"
                    
                yield self.create_text_message(error_message)
                
        except requests.RequestException as e:
            yield self.create_text_message(f"Failed to connect to Postmark API: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
