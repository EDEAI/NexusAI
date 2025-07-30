from collections.abc import Generator
from typing import Any
import json
import os
import httpx
import tempfile
from pathlib import Path
import random

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RagflowApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取凭证
        app_key = str(self.runtime.credentials.get("app_key"))
        app_url = str(self.runtime.credentials.get("app_url"))
        
        # 获取参数
        dataset_id = tool_parameters.get("dataset_id", '')
        document_id = tool_parameters.get("document_id", '')
        document_name = tool_parameters.get("document_name", '')
        append_content = tool_parameters.get("append_content", '')
        mode = tool_parameters.get("mode", 'append')
        
        print(f"dataset_id: {dataset_id}")
        print(f"document_id: {document_id}")
        print(f"document_name: {document_name}")
        # 验证必要参数
        if not dataset_id:
            yield self.create_text_message('Please enter the dataset ID')
            return
            
        if not document_id and not document_name:
            yield self.create_text_message('Please enter the document ID or document name')
            return
            
        if not append_content:
            yield self.create_text_message('Please enter the content to add')
            return
        
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix="ragflow_update_")
            temp_file_path = os.path.join(temp_dir, 'temp_document.txt')
            filename = None
            is_new_file = False
            to_delete_file_id = None
            
            # 如果提供了document_id，尝试下载现有文档
            if document_id:
                try:
                    # 步骤0: 验证文件是否存在并获取文件名
                    verify_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents"
                    headers = {
                        'Authorization': f'Bearer {app_key}',
                        'Content-Type': 'application/json'
                    }
                    
                    # 构建查询参数
                    params = {
                        'id': document_id,
                        'page': 1,
                        'page_size': 1
                    }
                    
                    # 发送验证请求
                    verify_response = httpx.get(
                        url=verify_url,
                        headers=headers,
                        params=params,
                        timeout=30.0
                    )
                    
                    # 处理验证响应
                    verify_data = verify_response.json()
                    print(f"文档验证响应: {verify_data}")
                    
                    if verify_data.get("code") == 0 and verify_data.get("data", {}).get("docs"):
                        # 获取文件信息
                        doc_info = verify_data.get("data", {}).get("docs", [])[0]
                        filename = doc_info.get("name", f"document_{document_id}")
                        doc_status = doc_info.get("run", "0")
                        to_delete_file_id = doc_info.get("id")
                        
                        print(f"找到文档: {filename}, 状态: {doc_status}")
                        
                        # 步骤1: 下载文档
                        download_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents/{document_id}"
                        
                        # 发送下载请求
                        with httpx.stream("GET", download_url, headers=headers, timeout=60.0) as response:
                            if response.status_code == 200:
                                # 使用之前获取的文件名
                                temp_file_path = os.path.join(temp_dir, filename)
                                with open(temp_file_path, 'wb') as f:
                                    for chunk in response.iter_bytes():
                                        f.write(chunk)
                                
                                print(f"文档已下载到: {temp_file_path}")
                                
                                # 下载成功后，将原文件重命名为备份格式
                                if to_delete_file_id:
                                    # 获取文件名和扩展名
                                    name_parts = os.path.splitext(filename)
                                    base_name = name_parts[0]
                                    extension = name_parts[1] if len(name_parts) > 1 else ""
                                    
                                    # 生成新的备份文件名：原名_日期_back.扩展名
                                    from datetime import datetime
                                    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
                                    # 生成4位随机数
                                    random_num = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                                    backup_name = f"{base_name}_{date_str}_{random_num}_back{extension}"
                                    
                                    # 调用更新接口重命名原文件
                                    update_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents/{to_delete_file_id}"
                                    update_data = {
                                        "name": backup_name
                                    }
                                    
                                    # 发送更新请求
                                    update_response = httpx.put(
                                        url=update_url,
                                        headers={
                                            'Authorization': f'Bearer {app_key}',
                                            'Content-Type': 'application/json'
                                        },
                                        json=update_data,
                                        timeout=30.0
                                    )
                                    
                                    # 处理更新响应
                                    update_result = update_response.json()
                                    print(f"文件重命名响应: {update_result}")
                                    
                                    if update_result.get("code") != 0:
                                        print(f"文件重命名失败: {update_result.get('message', '未知错误')}")
                            else:
                                print(f"下载文档失败: HTTP {response.status_code}")
                                raise Exception("下载文档失败")
                    else:
                        print("文档验证失败，将创建新文件")
                        raise Exception("文档验证失败")
                        
                except Exception as e:
                    print(f"获取现有文档失败: {str(e)}，将创建新文件")
                    if document_name:
                        is_new_file = True
                    else:
                        yield self.create_text_message(f"Error occurred while getting the document: {str(e)}")
                        return
            else:
                # 如果没有提供document_id但提供了document_name，创建新文件
                if document_name:
                    is_new_file = True
                else:
                    yield self.create_text_message("No document ID or document name provided")
                    return
            
            # 如果需要创建新文件
            if is_new_file:
                filename = document_name
                if not filename.endswith('.txt'):
                    filename += '.txt'
                temp_file_path = os.path.join(temp_dir, filename)
                
                # 创建新文件并写入内容
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(append_content)
                
                print(f"已创建新文件: {temp_file_path}")
            else:
                # 在现有文件末尾添加内容
                if mode == 'append':
                    with open(temp_file_path, 'a', encoding='utf-8') as f:
                        f.write("\n\n$$$$$$\n\n" + append_content)
                elif mode == 'overwrite':
                    with open(temp_file_path, 'w', encoding='utf-8') as f:
                        f.write(append_content)
                
                print(f"已将内容添加到文件末尾")
            
            # 步骤3: 上传文档
            upload_url = f"{app_url}/api/v1/datasets/{dataset_id}/documents"
            
            print(f"开始上传文件: {temp_file_path}")
            # 使用文件上传
            with open(temp_file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'application/octet-stream')
                }
                
                # 发送上传请求
                upload_response = httpx.post(
                    url=upload_url,
                    headers={
                        'Authorization': f'Bearer {app_key}'
                    },
                    files=files,
                    timeout=60.0
                )
            
            # 处理上传响应
            upload_data = upload_response.json()
            print(f"上传响应: {upload_data}")
            
            if upload_data.get("code") != 0:
                error_msg = upload_data.get("message", "Unknown error")
                yield self.create_text_message(f"File upload failed: {error_msg}")
                return
            
            # 获取新上传的文档ID
            new_document_id = None
            if upload_data.get("data") and len(upload_data["data"]) > 0:
                new_document_id = upload_data["data"][0].get("id")
            
            if not new_document_id:
                yield self.create_text_message("Unable to get the new uploaded document ID")
                return
            
            # 步骤4: 触发文档重新解析
            parse_url = f"{app_url}/api/v1/datasets/{dataset_id}/chunks"
            parse_data = {
                "document_ids": [new_document_id]
            }
            
            # 发送解析请求
            parse_response = httpx.post(
                url=parse_url,
                headers={
                    'Authorization': f'Bearer {app_key}',
                    'Content-Type': 'application/json'
                },
                json=parse_data,
                timeout=60.0
            )
            
            # 处理解析响应
            parse_data = parse_response.json()
            print(f"解析响应: {parse_data}")
            
            if parse_data.get("code") != 0:
                error_msg = parse_data.get("message", "Unknown error")
                yield self.create_text_message(f"Document parsing failed: {error_msg}")
                return
            
            # 清理临时文件
            # try:
            #     os.remove(temp_file_path)
            #     os.rmdir(temp_dir)
            # except Exception as e:
            #     print(f"清理临时文件失败: {str(e)}")
            
            # 返回成功结果
            yield self.create_json_message({
                "result": {
                    "message": "Document updated successfully",
                    "old_document_id": document_id,
                    "new_document_id": new_document_id,
                    "dataset_id": dataset_id
                }
            })
                
        except Exception as e:
            print(f"Error occurred while updating the document: {str(e)}")
            yield self.create_text_message(f"Error occurred while updating the document: {str(e)}")