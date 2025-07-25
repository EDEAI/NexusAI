from collections.abc import Generator
from typing import Any, List, Dict
import json
import httpx
import os # 用於提取文件名
import urllib.parse # 用於 URL 解碼文件名

from dify_plugin import Tool, File
from dify_plugin.entities.tool import ToolInvokeMessage

class UploadAndParseDocumentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        app_key = str(self.runtime.credentials.get("app_key"))
        app_url = str(self.runtime.credentials.get("app_url"))
        dify_url = str(self.runtime.credentials.get("dify_url", "")).rstrip('/') # 確保dify_url末尾沒有斜線

        dataset_id = tool_parameters.get("dataset_id", '')
        files_input_raw = tool_parameters.get("files", []) 
        oss_remote_files_str = tool_parameters.get("oss_remote_files", '')

        files_input: List[File] = []
        if files_input_raw:
            if isinstance(files_input_raw, list):
                files_input = files_input_raw
            else:
                files_input = [files_input_raw]

        if not app_url or not app_key:
            yield self.create_text_message("RAGFlow API URL or API Key is not configured.")
            return
        
        if not dify_url and files_input: # 如果有本地文件但dify_url未配置
            yield self.create_text_message("Dify URL (dify_url) is not configured in credentials, cannot download local files.")
            return

        if not dataset_id:
            yield self.create_text_message("Dataset ID is required.")
            return

        if not files_input and not oss_remote_files_str:
            yield self.create_text_message("No files provided for upload (neither local files nor OSS remote files).")
            return
        
        upload_results = []
        uploaded_doc_ids = []
        overall_success = True
        
        # 待上傳的文件列表，每個元素是 {'name': str, 'data': bytes, 'source_description': str}
        files_to_process_for_ragflow = []

        auth_headers_ragflow = {
            'Authorization': f'Bearer {app_key}'
        }

        print(f"files_input: {files_input}")

        # 1. 處理本地 Dify 文件
        # 首先過濾掉 files_input 中的 None 元素
        actual_files_to_process = [f_obj for f_obj in files_input if f_obj is not None]

        if actual_files_to_process and dify_url: # 確保列表非空且 dify_url 已配置
            yield self.create_text_message(f"準備處理 {len(actual_files_to_process)} 個有效的Dify平台文件...")
            for i, file_obj in enumerate(actual_files_to_process): # 迭代過濾後的列表
                # 此處 file_obj 保證不是 None
                file_name = file_obj.filename
                # 確保 URL 正確拼接, file_obj.url 通常是 /files/... 的相對路徑
                full_dify_file_url = f"{dify_url}{file_obj.url if file_obj.url.startswith('/') else '/' + file_obj.url}"
                source_desc = f"Dify file: {file_name} (from {full_dify_file_url})"
                yield self.create_text_message(f"正在下載Dify文件: {file_name} ({i+1}/{len(actual_files_to_process)}) from {full_dify_file_url}...")
                try:
                    with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                        response = client.get(full_dify_file_url)
                        response.raise_for_status()
                        file_data = response.content
                    files_to_process_for_ragflow.append({
                        "name": file_name, 
                        "data": file_data, 
                        "source_description": source_desc
                    })
                    yield self.create_text_message(f"Dify文件 '{file_name}' 下載成功。")
                except httpx.HTTPStatusError as e:
                    overall_success = False
                    error_msg = f"HTTP error {e.response.status_code} while downloading {source_desc}: {e.response.text[:200]}"
                    upload_results.append({"name": file_name, "status": "failed_download", "type":"dify_local", "error": error_msg})
                    yield self.create_text_message(error_msg)
                except Exception as e:
                    overall_success = False
                    error_msg = f"Error downloading {source_desc}: {str(e)}"
                    upload_results.append({"name": file_name, "status": "failed_download", "type":"dify_local", "error": error_msg})
                    yield self.create_text_message(error_msg)
        elif not actual_files_to_process and files_input and dify_url: # 如果原始列表有內容但過濾後為空
            yield self.create_text_message("Dify平台文件列表中未找到有效的文件對象（可能提供了空文件或無效文件）。")
        
        # 2. 處理遠程 OSS 文件
        if oss_remote_files_str:
            remote_file_urls = [url.strip() for url in oss_remote_files_str.split('\n') if url.strip()]
            if remote_file_urls:
                yield self.create_text_message(f"準備處理 {len(remote_file_urls)} 個遠程OSS文件...")
                for i, remote_url in enumerate(remote_file_urls):
                    # 從 URL 中提取文件名，如果失敗則生成一個基礎名稱
                    try:
                        # 移除查詢參數後取 basename，然後進行 URL 解碼
                        raw_filename = os.path.basename(remote_url.split('?')[0])
                        file_name_from_url = urllib.parse.unquote(raw_filename) # URL 解碼
                        if not file_name_from_url or file_name_from_url == '':
                            file_name_from_url = f"remote_file_{i+1}.dat"
                    except Exception:
                        file_name_from_url = f"remote_file_{i+1}.dat"
                    
                    source_desc = f"Remote OSS file: {file_name_from_url} (from {remote_url})"
                    yield self.create_text_message(f"正在下載遠程文件: {file_name_from_url} ({i+1}/{len(remote_file_urls)}) from {remote_url}...")
                    try:
                        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
                            response = client.get(remote_url)
                            response.raise_for_status()
                            file_data = response.content
                        files_to_process_for_ragflow.append({
                            "name": file_name_from_url, 
                            "data": file_data, 
                            "source_description": source_desc
                        })
                        yield self.create_text_message(f"遠程文件 '{file_name_from_url}' ({remote_url}) 下載成功。")
                    except httpx.HTTPStatusError as e:
                        overall_success = False
                        error_msg = f"HTTP error {e.response.status_code} while downloading {source_desc}: {e.response.text[:200]}"
                        upload_results.append({"name": remote_url, "status": "failed_download", "type":"remote_oss", "error": error_msg})
                        yield self.create_text_message(error_msg)
                    except Exception as e:
                        overall_success = False
                        error_msg = f"Error downloading {source_desc}: {str(e)}"
                        upload_results.append({"name": remote_url, "status": "failed_download", "type":"remote_oss", "error": error_msg})
                        yield self.create_text_message(error_msg)

        # 3. 將所有成功下載的文件內容上傳到 RAGFlow
        if not files_to_process_for_ragflow:
            if overall_success: # 如果之前沒有任何類型的文件輸入，且下載也沒出錯（雖然不可能到這裡）
                 yield self.create_text_message("沒有文件被成功處理以下載，無法進行上傳。")
            # else: 如果 overall_success 為 false，說明下載階段已經報過錯了，這裡不再重複報「無文件上傳」
            # 仍然需要生成最終的 JSON 報告
        else:
            yield self.create_text_message(f"準備上傳 {len(files_to_process_for_ragflow)} 個已下載的文件到RAGFlow數據集 {dataset_id}...")
            ragflow_upload_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents"

            for i, file_to_upload in enumerate(files_to_process_for_ragflow):
                file_name = file_to_upload["name"]
                file_data = file_to_upload["data"]
                source_desc = file_to_upload["source_description"]
                
                # 嘗試獲取或猜測MIME類型，如果需要更精確的MIME類型，可能需要 python-magic 庫
                # 這裡為了簡化，對於遠程文件統一使用 application/octet-stream
                # 对于 Dify 本地文件，之前可以从 file_obj.mimetype 获取，但现在 file_obj 不在此作用域
                # 可以在 files_to_process_for_ragflow 中也存儲 mimetype (如果可從 file_obj 獲取)
                mime_type = 'application/octet-stream' 

                files_payload_for_ragflow = {
                    'file': (file_name, file_data, mime_type)
                }
                yield self.create_text_message(f"正在上傳: {file_name} ({i+1}/{len(files_to_process_for_ragflow)}) 到 RAGFlow...")
                current_doc_id = None
                upload_successful = False
                try:
                    with httpx.Client(timeout=120.0) as client:
                        response = client.post(
                            ragflow_upload_url,
                            headers=auth_headers_ragflow,
                            files=files_payload_for_ragflow
                        )
                        response.raise_for_status()
                        response_data = response.json()
                    
                    if response_data.get("code") == 0 and response_data.get("data"):
                        if isinstance(response_data["data"], list) and len(response_data["data"]) > 0:
                            current_doc_id = response_data["data"][0].get("id")
                            doc_name_from_ragflow = response_data["data"][0].get("name")
                            if current_doc_id:
                                upload_successful = True
                                # 上傳成功，暫不加入 uploaded_doc_ids，等待配置更新成功
                                upload_results.append({"name": file_name, "original_source": source_desc, "status": "success_upload_pending_config", "id": current_doc_id, "ragflow_name": doc_name_from_ragflow})
                                yield self.create_text_message(f"文件 '{file_name}' (來自 {source_desc}) 上傳RAGFlow成功。文檔 ID: {current_doc_id}. 準備更新配置...")
                            else:
                                overall_success = False
                                upload_results.append({"name": file_name, "original_source": source_desc, "status": "failed_upload", "error": "RAGFlow API success but no document ID returned."})
                                yield self.create_text_message(f"文件 '{file_name}' (來自 {source_desc}) 上傳RAGFlow後未獲取到文檔 ID。響應: {json.dumps(response_data)}")
                        else:
                            overall_success = False
                            upload_results.append({"name": file_name, "original_source": source_desc, "status": "failed_upload", "error": "RAGFlow API success but data format unexpected.", "response": response_data})
                            yield self.create_text_message(f"文件 '{file_name}' (來自 {source_desc}) 上傳RAGFlow後返回數據格式異常。響應: {json.dumps(response_data)}")
                    else:
                        overall_success = False
                        error_message = response_data.get("message", "Unknown error during RAGFlow upload")
                        upload_results.append({"name": file_name, "original_source": source_desc, "status": "failed_upload", "error": error_message, "response_code": response_data.get("code")})
                        yield self.create_text_message(f"文件 '{file_name}' (來自 {source_desc}) 上傳RAGFlow失敗: {error_message} (Code: {response_data.get('code')})")
                except httpx.HTTPStatusError as e:
                    overall_success = False
                    error_body_text = e.response.text[:200]
                    upload_results.append({"name": file_name, "original_source": source_desc, "status": "failed_upload", "error": f"HTTP error: {e.response.status_code}", "details": error_body_text})
                    yield self.create_text_message(f"上傳文件 '{file_name}' (來自 {source_desc}) 到RAGFlow時發生 HTTP 錯誤: {e.response.status_code}. 響應: {error_body_text}")
                except Exception as e:
                    overall_success = False
                    upload_results.append({"name": file_name, "original_source": source_desc, "status": "failed_upload", "error": str(e)})
                    yield self.create_text_message(f"上傳文件 '{file_name}' (來自 {source_desc}) 到RAGFlow時發生異常: {str(e)}")

                # 新增：如果上傳成功 (获得了 current_doc_id)，則更新文檔配置
                if upload_successful and current_doc_id:
                    update_doc_config_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents/{current_doc_id}"
                    config_payload = {
                        "chunk_method": "naive",
                        "parser_config": {
                            "delimiter": "\n"
                            # 為了保持其他 naive 配置項的默認值或現有值，這裡只指定 delimiter
                            # 如果需要完全控制，應獲取文檔現有 parser_config 並與之合併，或提供所有 naive 參數
                        }
                    }
                    yield self.create_text_message(f"正在為文檔 ID {current_doc_id} ('{file_name}') 更新解析配置為 delimiter: '\n'...")
                    try:
                        with httpx.Client(timeout=60.0) as client:
                            update_response = client.put(
                                update_doc_config_url,
                                headers=auth_headers_ragflow, # Content-Type is application/json by default for json payload
                                json=config_payload
                            )
                            update_response.raise_for_status()
                            update_response_data = update_response.json()
                        
                        if update_response_data.get("code") == 0:
                            uploaded_doc_ids.append(current_doc_id) # 配置更新成功，才將 doc_id 加入待解析列表
                            # 更新 upload_results 中的狀態
                            for res in upload_results:
                                if res.get("id") == current_doc_id:
                                    res["status"] = "success_upload_and_config"
                                    break
                            yield self.create_text_message(f"文檔 ID {current_doc_id} ('{file_name}') 解析配置更新成功。")
                        else:
                            overall_success = False # 配置更新失敗也算整體操作部分失敗
                            error_message = update_response_data.get("message", "Unknown error during document config update")
                            # 更新 upload_results 中的狀態
                            for res in upload_results:
                                if res.get("id") == current_doc_id:
                                    res["status"] = "failed_config_update"
                                    res["error_config_update"] = error_message
                                    break
                            yield self.create_text_message(f"文檔 ID {current_doc_id} ('{file_name}') 解析配置更新失敗: {error_message} (Code: {update_response_data.get('code')}). 仍會嘗試解析原配置。")
                            # 即使配置更新失敗，我們仍然將其加入待解析列表，讓RAGFlow用默認配置嘗試解析
                            uploaded_doc_ids.append(current_doc_id)

                    except httpx.HTTPStatusError as e:
                        overall_success = False
                        error_body_text = e.response.text[:200]
                        for res in upload_results:
                            if res.get("id") == current_doc_id:
                                res["status"] = "failed_config_update"
                                res["error_config_update"] = f"HTTP error: {e.response.status_code}, {error_body_text}"
                                break
                        yield self.create_text_message(f"更新文檔 ID {current_doc_id} ('{file_name}') 解析配置時發生 HTTP 錯誤: {e.response.status_code}. 響應: {error_body_text}. 仍會嘗試解析原配置。")
                        uploaded_doc_ids.append(current_doc_id)
                    except Exception as e:
                        overall_success = False
                        for res in upload_results:
                            if res.get("id") == current_doc_id:
                                res["status"] = "failed_config_update"
                                res["error_config_update"] = str(e)
                                break
                        yield self.create_text_message(f"更新文檔 ID {current_doc_id} ('{file_name}') 解析配置時發生異常: {str(e)}. 仍會嘗試解析原配置。")
                        uploaded_doc_ids.append(current_doc_id)

        # 4. 觸發解析 (邏輯基本不變, 使用收集到的 uploaded_doc_ids)
        parse_triggered = False
        parsing_status_message = "沒有成功上傳到RAGFlow的文件可供解析。"
        if uploaded_doc_ids:
            yield self.create_text_message(f"準備為 {len(uploaded_doc_ids)} 個已成功上傳到RAGFlow的文檔觸發解析...")
            parse_url = f"{app_url}/api/v1/datasets/{dataset_id}/chunks"
            payload = {"document_ids": uploaded_doc_ids}
            
            # 添加調試日誌
            print(f"Attempting to trigger parsing. URL: {parse_url}, Payload: {json.dumps(payload)}")

            json_headers_parse = {
                'Authorization': f'Bearer {app_key}',
                'Content-Type': 'application/json'
            }
            try:
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(parse_url, headers=json_headers_parse, json=payload)
                    response.raise_for_status()
                    parse_response_data = response.json()
                
                if parse_response_data.get("code") == 0:
                    parse_triggered = True
                    parsing_status_message = f"已成功觸發對 {len(uploaded_doc_ids)} 個文檔的解析任務。"
                    yield self.create_text_message(parsing_status_message)
                else:
                    overall_success = False # 即使上傳部分成功，但解析觸發失敗也算 overall_success=False
                    error_message = parse_response_data.get("message", "Unknown error during parsing trigger")
                    parsing_status_message = f"觸發文檔解析失敗: {error_message} (Code: {parse_response_data.get('code')})"
                    yield self.create_text_message(parsing_status_message)
            except httpx.HTTPStatusError as e:
                overall_success = False
                error_body_text = e.response.text[:200]
                parsing_status_message = f"觸發解析時發生 HTTP 錯誤: {e.response.status_code}. 響應: {error_body_text}"
                yield self.create_text_message(parsing_status_message)
            except Exception as e:
                overall_success = False
                parsing_status_message = f"觸發解析時發生異常: {str(e)}"
                yield self.create_text_message(parsing_status_message)
        else:
            if overall_success : # 如果到這裡 overall_success 仍然為 true, 說明沒有文件被下載成功
                 parsing_status_message = "沒有文件成功下載並上傳，因此無法觸發解析。"
            yield self.create_text_message(parsing_status_message)

        final_summary = {
            "overall_success": overall_success,
            "operation_summary": upload_results, # 改名以更好反映其內容
            "parsing_triggered": parse_triggered,
            "parsed_doc_ids_on_trigger": uploaded_doc_ids if parse_triggered else [], # 更明確的名稱
            "parsing_status_message": parsing_status_message
        }
        yield self.create_json_message(final_summary) 