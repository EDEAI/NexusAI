from typing import Any, Generator
import httpx
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from tools.utils.slack_markdown_converter import SlackMarkdownConverter


class SlackPostToThreadTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Slack Post to Thread
        API Document: https://api.slack.com/methods/chat.postMessage
        """
        # Slack Botのトークン
        bot_token = tool_parameters.get("bot_token", "").strip()
        if not bot_token:
            yield self.create_text_message(
                "Invalid parameter: 'bot_token' is required."
            )
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bot_token}",
        }

        # チャンネルID
        channel_id = tool_parameters.get("channel_id", "")
        if not channel_id:
            yield self.create_text_message(
                "Invalid parameter: 'channel_id' is required."
            )
            return

        # スレッドのタイムスタンプ
        thread_ts = tool_parameters.get("thread_ts", "")
        if not thread_ts:
            yield self.create_text_message(
                "Invalid parameter: 'thread_ts' is required."
            )
            return

        # 送信したいメッセージ本文
        content = tool_parameters.get("content", "")
        if not content:
            yield self.create_text_message("Invalid parameter: 'content' is required.")
            return

        converter = SlackMarkdownConverter()
        converted_content = converter.convert(content)

        # Slackで指定されている3,000文字以上の場合は分割
        # https://api.slack.com/reference/block-kit/composition-objects#text__fields
        MAX_MSG_LEN = 3000
        if len(converted_content) > MAX_MSG_LEN:
            lines = converted_content.split("\n")
            chunks = []
            current_chunk = ""

            for line in lines:
                # line自体がMAX_MSG_LENを超える場合を考慮
                if len(line) > MAX_MSG_LEN:
                    # lineをさらにサブ分割
                    sub_chunks = [
                        line[i : i + MAX_MSG_LEN]
                        for i in range(0, len(line), MAX_MSG_LEN)
                    ]
                    for sub in sub_chunks:
                        if (
                            len(current_chunk)
                            + (len(sub) + (1 if current_chunk else 0))
                            <= MAX_MSG_LEN
                        ):
                            if current_chunk:
                                current_chunk += "\n"
                            current_chunk += sub
                        else:
                            chunks.append(current_chunk)
                            current_chunk = sub
                else:
                    # lineがMAX_MSG_LEN以内なら従来の行ごと処理
                    added_length = len(line) + (1 if current_chunk else 0)
                    if len(current_chunk) + added_length <= MAX_MSG_LEN:
                        if current_chunk:
                            current_chunk += "\n"
                        current_chunk += line
                    else:
                        chunks.append(current_chunk)
                        current_chunk = line

            # 最後に残っていたら追加
            if current_chunk:
                chunks.append(current_chunk)
        else:
            chunks = [converted_content]

        # 処理状態管理用フラグ/メッセージ
        all_success = True
        failure_chunk_index = None
        failure_reason = ""

        for i, chunk in enumerate(chunks, start=1):
            answer_blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": chunk},
                }
            ]

            payload = {
                "channel": channel_id,
                "text": chunk,
                "blocks": answer_blocks,
                "thread_ts": thread_ts,
            }
            try:
                # Slackのchat.postMessage APIをコール
                res = httpx.post(
                    "https://slack.com/api/chat.postMessage",
                    headers=headers,
                    json=payload,
                )

                # HTTPステータスが2xx以外の場合
                if not res.is_success:
                    all_success = False
                    failure_chunk_index = i
                    failure_reason = (
                        f"HTTP status code: {res.status_code}, response: {res.text}"
                    )
                    break

                data = res.json()
                # Slack APIが "ok": false を返した場合
                if not data.get("ok", False):
                    all_success = False
                    failure_chunk_index = i
                    failure_reason = (
                        f"Slack API error: {data.get('error', 'unknown_error')}"
                    )
                    break

            except Exception as e:
                all_success = False
                failure_chunk_index = i
                failure_reason = f"Exception occurred: {str(e)}"
                break

        # 全チャンク送信の成否に応じて、最後に一度だけメッセージを返す
        if all_success:
            # すべて成功
            yield self.create_text_message(
                f"All {len(chunks)} message chunks were sent successfully."
            )
        else:
            # どこかで失敗
            yield self.create_text_message(
                f"Failed to send chunk {failure_chunk_index}. Reason: {failure_reason}"
            )
