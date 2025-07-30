import time
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.proxycurl_api import ProxycurlAPI, ProxycurlApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class EnrichLinkedInProfileTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        self.api_key = self.runtime.credentials.get("api_key")
        self.api = ProxycurlAPI(self.api_key)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            linkedin_url = tool_parameters["linkedin_url"]

            yield self.create_text_message("🔍 Fetching LinkedIn profile data...")
            profile_data = self.api.enrich_profile(linkedin_url)

            if not profile_data or "full_name" not in profile_data:
                yield self.create_text_message("⚠️ No enriched profile data found.")
                return

            name = profile_data.get("full_name", "Unknown")
            occupation = profile_data.get("occupation", "Not available")
            summary = profile_data.get("summary", "No summary available")
            headline = profile_data.get("headline", "No headline available")
            profile_pic = profile_data.get("profile_pic_url", None)

            msg = f"""👤 **{name}**
- 🏢 {occupation}
- 📝 {headline}
- 📄 {summary[:300]}{'...' if len(summary) > 300 else ''}"""

            if profile_pic:
                # Older dify-plugin versions don't support `alt`, omit it for now
                yield self.create_image_message(image_url=profile_pic)

            yield self.create_text_message(msg)

        except ProxycurlApiException as e:
            raise ToolProviderCredentialValidationError(f"[Proxycurl API Error] {str(e)}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(f"[Unexpected Error] {str(e)}")
