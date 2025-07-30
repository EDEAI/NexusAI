from datetime import datetime
from typing import Any, Generator
from googleapiclient.discovery import build
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class YoutubeVideosAnalyticsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        channel = tool_parameters.get("channel", "")
        if not channel:
            yield self.create_text_message("Please input symbol")
        time_range = [None, None]
        start_date = tool_parameters.get("start_date", "")
        if start_date:
            time_range[0] = start_date
        else:
            time_range[0] = "1800-01-01"
        end_date = tool_parameters.get("end_date", "")
        if end_date:
            time_range[1] = end_date
        else:
            time_range[1] = datetime.now().strftime("%Y-%m-%d")
        if "google_api_key" not in self.runtime.credentials or not self.runtime.credentials["google_api_key"]:
            yield self.create_text_message("Please input api key")
        youtube = build("youtube", "v3", developerKey=self.runtime.credentials["google_api_key"])
        search_results = youtube.search().list(q=channel, type="channel", order="relevance", part="id").execute()
        channel_id = search_results["items"][0]["id"]["channelId"]
        (start_date, end_date) = time_range
        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%dT%H:%M:%SZ")
        time_range_videos = (
            youtube.search()
            .list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                publishedAfter=start_date,
                publishedBefore=end_date,
            )
            .execute()
        )

        def extract_video_data(video_list):
            data = []
            for video in video_list["items"]:
                video_id = video["id"]["videoId"]
                video_info = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
                title = video_info["items"][0]["snippet"]["title"]
                views = video_info["items"][0]["statistics"]["viewCount"]
                data.append({"Title": title, "Views": views})
            return data

        summary = extract_video_data(time_range_videos)
        yield self.create_text_message(str(summary))
