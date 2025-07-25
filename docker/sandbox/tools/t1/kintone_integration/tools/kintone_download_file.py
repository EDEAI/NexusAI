import json
from collections.abc import Generator
from typing import Any, Dict

import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class KintoneDownloadFileTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # kintone の認証情報を取得
        kintone_domain = tool_parameters.get("kintone_domain")
        if not kintone_domain:
            yield self.create_text_message("kintone ドメインが見つかりません。kintone_domainパラメータを確認してください。")
            return

        kintone_api_token = tool_parameters.get("kintone_api_token")
        if not kintone_api_token:
            yield self.create_text_message("kintone APIトークンが見つかりません。kintone_api_tokenパラメータを確認してください。")
            return

        # ファイルキーの取得
        file_key = tool_parameters.get("file_key")
        if not file_key:
            yield self.create_text_message("ファイルキーが見つかりません。file_keyパラメータを確認してください。")
            return

        # APIリクエスト用のヘッダー設定
        headers = {
            "X-Cybozu-API-Token": kintone_api_token
        }

        # kintone のファイルダウンロード API のエンドポイント
        url = f"https://{kintone_domain}/k/v1/file.json"

        # クエリパラメータの設定
        params = {
            "fileKey": file_key
        }

        try:
            # APIリクエストの実行
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30,  # タイムアウトを30秒に設定（ファイルダウンロードは時間がかかる可能性があるため）
                    stream=True  # ストリーミングモードを有効化
                )
                # HTTPエラーがあれば例外を発生
                response.raise_for_status()
            except Timeout:
                yield self.create_text_message("kintone APIへのリクエストがタイムアウトしました。ネットワーク接続を確認してください。")
                return
            except HTTPError as e:
                # kintoneのエラーメッセージをそのまま返す
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', str(e))
                except (json.JSONDecodeError, AttributeError):
                    error_message = str(e)
                
                yield self.create_text_message(f"kintone APIエラー: {error_message}")
                return
            except RequestException as e:
                yield self.create_text_message(f"kintone APIへの接続中にエラーが発生しました: {str(e)}")
                return

            # Content-Typeを取得
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            
            # ファイルデータの読み込み
            file_data = response.content
            
            # ファイルサイズのチェック（15MB制限）
            MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB
            if len(file_data) > MAX_FILE_SIZE:
                yield self.create_text_message("ファイルサイズが大きすぎます。15MB以下のファイルを指定してください。")
                return
            
            # create_blob_messageを使用してファイルを返す
            yield self.create_blob_message(
                file_data,  # バイナリデータ
                {"mime_type": content_type}  # メタデータとしてContent-Typeを渡す
            )

        except Exception as e:
            # 予期しないエラーの処理
            error_message = f"kintone API 呼び出し中に予期しないエラーが発生しました: {str(e)}"
            yield self.create_text_message(error_message)
