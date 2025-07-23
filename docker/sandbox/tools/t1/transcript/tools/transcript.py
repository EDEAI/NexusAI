from typing import Any, Generator
from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class YouTubeTranscriptTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the YouTube transcript tool
        """
        try:
            video_input = tool_parameters["video_id"]
            language = tool_parameters.get("language")
            output_format = tool_parameters.get("format", "text")
            preserve_formatting = tool_parameters.get("preserve_formatting", False)
            proxy = tool_parameters.get("proxy")
            cookies = tool_parameters.get("cookies")
            video_id = self._extract_video_id(video_input)
            kwargs = {
                "proxies": {"https": proxy} if proxy else None,
                "cookies": cookies,
            }
            try:
                if language:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(
                        video_id, **kwargs
                    )
                    try:
                        transcript = transcript_list.find_transcript([language])
                    except:
                        transcript = transcript_list.find_transcript(["en"]).translate(
                            language
                        )
                    transcript_data = transcript.fetch()
                else:
                    transcript_data = YouTubeTranscriptApi.get_transcript(
                        video_id, preserve_formatting=preserve_formatting, **kwargs
                    )
                formatter_class = {
                    "json": "JSONFormatter",
                    "pretty": "PrettyPrintFormatter",
                    "srt": "SRTFormatter",
                    "vtt": "WebVTTFormatter",
                }.get(output_format)
                if formatter_class:
                    from youtube_transcript_api import formatters

                    formatter = getattr(formatters, formatter_class)()
                    formatted_transcript = formatter.format_transcript(transcript_data)
                else:
                    formatted_transcript = " ".join(
                        (entry["text"] for entry in transcript_data)
                    )
                yield self.create_text_message(text=formatted_transcript)
            except Exception as e:
                yield self.create_text_message(
                    text=f"Error getting transcript: {str(e)}"
                )
        except Exception as e:
            yield self.create_text_message(text=f"Error processing request: {str(e)}")

    def _extract_video_id(self, video_input: str) -> str:
        """
        Extract video ID from URL or return as-is if already an ID
        """
        if "youtube.com" in video_input or "youtu.be" in video_input:
            parsed_url = urlparse(video_input)
            if "youtube.com" in parsed_url.netloc:
                return parse_qs(parsed_url.query)["v"][0]
            else:
                return parsed_url.path[1:]
        return video_input
