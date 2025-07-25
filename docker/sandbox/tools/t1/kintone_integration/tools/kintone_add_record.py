import json
import re
from collections.abc import Generator
from typing import Any, Dict, List, Tuple

import requests
from requests.exceptions import RequestException, Timeout, HTTPError

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class KintoneAddRecordTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # kintone の認証情報およびアプリIDを取得
        kintone_domain = tool_parameters.get("kintone_domain")
        if not kintone_domain:
            yield self.create_text_message("kintone ドメインが見つかりません。kintone_domainパラメータを確認してください。")
            return

        kintone_app_id = tool_parameters.get("kintone_app_id")
        if not kintone_app_id:
            yield self.create_text_message("kintone アプリIDが見つかりません。kintone_app_idパラメータを確認してください。")
            return

        kintone_api_token = tool_parameters.get("kintone_api_token")
        if not kintone_api_token:
            yield self.create_text_message("kintone APIトークンが見つかりません。kintone_api_tokenパラメータを確認してください。")
            return

        # レコードデータの取得
        record_data = tool_parameters.get("record_data")
        if not record_data:
            yield self.create_text_message("レコードデータが見つかりません。record_dataパラメータを確認してください。")
            return

        # レコードデータをJSONとして解析
        try:
            record_json = json.loads(record_data)
        except json.JSONDecodeError:
            yield self.create_text_message("レコードデータが有効なJSON形式ではありません。正しいJSON形式で入力してください。")
            return
            
        # レコードデータの基本的な構造を検証
        validation_errors = self._validate_record_structure(record_json)
        if validation_errors:
            error_message = "レコードデータの構造が不正です:\n" + "\n".join(validation_errors)
            yield self.create_text_message(error_message)
            return
            
        # フィールドタイプに基づいた詳細なバリデーションを実行
        try:
            field_types = self._get_app_fields(kintone_domain, kintone_app_id, kintone_api_token)
            is_valid, validation_errors = self._validate_field_values(record_json, field_types)
            if not is_valid:
                error_message = "レコードデータの検証に失敗しました:\n" + "\n".join(validation_errors)
                yield self.create_text_message(error_message)
                return
        except Exception as e:
            # フィールド情報の取得に失敗した場合は警告を表示して続行
            yield self.create_text_message(f"警告: フィールド情報の取得に失敗したため、詳細な検証をスキップします: {str(e)}")

        # APIリクエスト用のヘッダー設定
        headers = {
            "X-Cybozu-API-Token": kintone_api_token,
            "Content-Type": "application/json"
        }

        # kintone のレコード追加 API のエンドポイント
        url = f"https://{kintone_domain}/k/v1/record.json"

        try:
            # リクエスト用のJSONボディを作成
            request_body = {
                "app": kintone_app_id,
                "record": record_json
            }

            # APIリクエストの実行
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=request_body,
                    timeout=10  # タイムアウトを10秒に設定
                )
                # HTTPエラーがあれば例外を発生
                response.raise_for_status()
            except Timeout:
                yield self.create_text_message("kintone APIへのリクエストがタイムアウトしました。ネットワーク接続を確認してください。")
                return
            except HTTPError as e:
                # HTTPステータスコードに基づいたエラーメッセージ
                status_code = e.response.status_code if hasattr(e, 'response') else 'unknown'
                if status_code == 401:
                    yield self.create_text_message("kintone APIの認証に失敗しました。APIトークンを確認してください。")
                elif status_code == 403:
                    yield self.create_text_message("kintone APIへのアクセス権限がありません。APIトークンの権限を確認してください。")
                elif status_code == 404:
                    yield self.create_text_message("指定されたkintoneアプリが見つかりません。アプリIDを確認してください。")
                elif status_code >= 500:
                    yield self.create_text_message(f"kintoneサーバーでエラーが発生しました（ステータスコード: {status_code}）。")
                else:
                    yield self.create_text_message(f"kintone APIリクエスト中にHTTPエラーが発生しました: {str(e)}")
                return
            except RequestException as e:
                yield self.create_text_message(f"kintone APIへの接続中にエラーが発生しました: {str(e)}")
                return

            # レスポンスのJSONデータを解析
            try:
                data = response.json()
            except json.JSONDecodeError:
                yield self.create_text_message("kintone APIからの応答を解析できませんでした。無効なJSONレスポンスです。")
                return

            # レコードIDの取得
            record_id = data.get("id")
            if not record_id:
                yield self.create_text_message("レコードの追加に成功しましたが、レコードIDを取得できませんでした。")
                return

            # 成功メッセージを返す
            success_message = f"レコードが正常に追加されました。レコードID: {record_id}"
            yield self.create_text_message(success_message)

        except Exception as e:
            # 予期しないエラーの処理
            error_message = f"kintone API 呼び出し中に予期しないエラーが発生しました: {str(e)}"
            yield self.create_text_message(error_message)
            
    def _validate_record_structure(self, record_data: Dict[str, Any]) -> List[str]:
        """
        レコードデータの基本的な構造を検証する関数
        
        Args:
            record_data: 検証するレコードデータ
            
        Returns:
            エラーメッセージのリスト（空リストの場合は検証成功）
        """
        errors = []
        
        # レコードデータが辞書型であることを確認
        if not isinstance(record_data, dict):
            errors.append("レコードデータは辞書型である必要があります")
            return errors
            
        # 各フィールドの構造を検証
        for field_code, field_data in record_data.items():
            # フィールドコードが文字列であることを確認
            if not isinstance(field_code, str):
                errors.append(f"フィールドコードは文字列である必要があります: {field_code}")
                continue
                
            # フィールドデータが辞書型であることを確認
            if not isinstance(field_data, dict):
                errors.append(f"フィールド '{field_code}' のデータは辞書型である必要があります")
                continue
                
            # valueキーが存在することを確認
            if "value" not in field_data:
                errors.append(f"フィールド '{field_code}' に 'value' キーがありません")
                
        return errors
        
    def _get_app_fields(self, domain: str, app_id: Any, api_token: str) -> Dict[str, str]:
        """
        kintoneアプリのフィールド情報を取得する関数
        
        Args:
            domain: kintoneドメイン
            app_id: アプリID
            api_token: APIトークン
            
        Returns:
            フィールドコードとフィールドタイプのマッピング辞書
        """
        # APIリクエスト用のヘッダー設定
        headers = {
            "X-Cybozu-API-Token": api_token,
            "Content-Type": "application/json"
        }
        
        # kintone のフィールド情報取得 API のエンドポイント
        url = f"https://{domain}/k/v1/app/form/fields.json"
        
        # リクエストパラメータ
        params = {
            "app": app_id
        }
        
        # APIリクエストの実行
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=10
        )
        
        # HTTPエラーがあれば例外を発生
        response.raise_for_status()
        
        # レスポンスのJSONデータを解析
        data = response.json()
        properties = data.get("properties", {})
        
        # フィールドコードとフィールドタイプのマッピングを作成
        field_types = {}
        for field_code, field_info in properties.items():
            field_types[field_code] = field_info.get("type", "UNKNOWN")
            
        return field_types
        
    def _validate_field_values(self, record_data: Dict[str, Any], field_types: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        フィールドタイプに基づいてフィールド値を検証する関数
        
        Args:
            record_data: 検証するレコードデータ
            field_types: フィールドコードとフィールドタイプのマッピング
            
        Returns:
            (検証結果, エラーメッセージのリスト)
        """
        errors = []
        
        for field_code, field_data in record_data.items():
            # フィールドタイプが不明な場合はスキップ
            if field_code not in field_types:
                continue
                
            field_type = field_types[field_code]
            value = field_data.get("value")
            
            # フィールドタイプに基づいた検証
            if field_type == "NUMBER":
                # 数値フィールドの検証
                if value is not None and value != "":
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"フィールド '{field_code}' の値は数値である必要があります: {value}")
                        
            elif field_type == "DATE":
                # 日付フィールドの検証（YYYY-MM-DD形式）
                if value and not re.match(r'^\d{4}-\d{2}-\d{2}$', str(value)):
                    errors.append(f"フィールド '{field_code}' の値は YYYY-MM-DD 形式である必要があります: {value}")
                    
            elif field_type == "TIME":
                # 時刻フィールドの検証（HH:MM形式）
                if value and not re.match(r'^\d{2}:\d{2}$', str(value)):
                    errors.append(f"フィールド '{field_code}' の値は HH:MM 形式である必要があります: {value}")
                    
            elif field_type == "DATETIME":
                # 日時フィールドの検証
                if value and not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z?$', str(value)):
                    errors.append(f"フィールド '{field_code}' の値は YYYY-MM-DDThh:mm:ssZ 形式である必要があります: {value}")
                    
            elif field_type in ["CHECK_BOX", "MULTI_SELECT"]:
                # 複数選択フィールドの検証
                if value is not None and not isinstance(value, list):
                    errors.append(f"フィールド '{field_code}' の値はリスト形式である必要があります: {value}")
                    
            elif field_type in ["USER_SELECT", "ORGANIZATION_SELECT", "GROUP_SELECT"]:
                # ユーザー/組織/グループ選択フィールドの検証
                if value is not None:
                    if not isinstance(value, list):
                        errors.append(f"フィールド '{field_code}' の値はリスト形式である必要があります: {value}")
                    else:
                        for item in value:
                            if not isinstance(item, dict) or "code" not in item or "type" not in item:
                                errors.append(f"フィールド '{field_code}' の各項目には 'code' と 'type' キーが必要です: {item}")
        
        return len(errors) == 0, errors
