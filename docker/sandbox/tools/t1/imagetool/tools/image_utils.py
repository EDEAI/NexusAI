import logging
import time
from typing import Any, Dict, Generator

from dify_plugin.entities.tool import ToolInvokeMessage
import requests

logger = logging.getLogger(__name__)

API_TIMEOUT = 30            # HTTP 请求超时时间(秒)
POLL_INTERVAL = 2           # 轮询间隔(秒)
MAX_POLL_RETRIES = 900      # 最大轮询次数

def validate_params(params: dict[str, Any], required: list[str]) -> None:
    """
    验证必填参数是否存在。
    - params: 输入参数字典
    - required: 必填参数名列表
    如果缺少任何必填项，则抛出 ValueError。
    """
    missing = [k for k in required if k not in params or params[k] is None]
    if missing:
        raise ValueError(f"Missing parameter(s): {', '.join(missing)}")

def submit_image_task(api_key: str, api_url: str, payload: Dict[str, Any]) -> str:
    """
    提交异步图片生成任务。
    - api_key: API Key
    - api_url: API 端点
    - payload: 有效载荷
    返回 task_id 字符串，供后续轮询使用。
    如果请求失败或响应不包含 task_id，会抛出 RuntimeError 或 ValueError。
    """
    try:
        resp = requests.post(
            url=api_url,
            headers={
                "X-DashScope-Async": "enable",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json=payload,
            timeout=API_TIMEOUT
        )
        resp.raise_for_status()
        data = resp.json()

        if not (data.get("output") and data["output"].get("task_id")):
            raise ValueError("Invalid API response: missing task_id")
            
        logger.debug("Task submitted successfully: %s", data["output"]["task_id"])
        return data["output"]["task_id"]
    
    except requests.exceptions.RequestException as e:
        logger.error("Failed to submit task: %s", e)
        raise RuntimeError(e)

def fetch_task_result(api_key: str, task_id: str) -> Dict[str, Any]:
    """
    获取任务结果
    - api_key: API Key
    - task_id: 任务 ID
    返回解析后的 JSON 字典，可能包含 status、results 等字段。
    如果请求失败，会抛出 RuntimeError。
    """
    try:
        resp = requests.get(
            url=f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=API_TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()
    
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch task result: %s", e)
        raise RuntimeError(e)

def handle_success_result(
    task_data: Dict[str, Any],
    task_id: str,
    tool: Any
) -> Generator[ToolInvokeMessage, None, None]:
    """
    处理成功的任务结果，依次产出：
    1. JSON 消息，包含 task_id、image_count、results 列表
    2. 对每张图片 URL，产出一个 image message
    """
    output = task_data["output"]
    results = output.get("results") or output.get("render_urls") or []

    yield tool.create_json_message({
        "task_id": task_id,
        "image_count": len(results),
        "results": results
    })

    for item in results:
        if isinstance(item, str):
            # 字符串列表的情况
            yield tool.create_image_message(item)
        elif isinstance(item, dict) and (url := item.get("url")):
            # 对象列表的情况
            yield tool.create_image_message(url)

def poll_task_status(
    tool: Any,
    api_key: str,
    task_id: str
) -> Generator[ToolInvokeMessage, None, None]:
    """
    持续轮询任务状态直到 SUCCEEDED 或出错/超时。
    - tool: 工具实例
    - api_key: API Key
    - task_id: 任务 ID
    轮询过程中若 status=SUCCEEDED，则调用 handle_success_result。
    若 status=FAILED/UNKNOWN，抛出 RuntimeError。
    若超出最大重试次数，抛出 TimeoutError。
    """
    for _ in range(MAX_POLL_RETRIES):
        td = fetch_task_result(api_key, task_id)
        status = td["output"].get("task_status")
        message = td["output"].get("message")

        if status == "SUCCEEDED":
            yield from handle_success_result(td, task_id, tool)
            return
        
        if status in ("FAILED", "UNKNOWN"):
            raise RuntimeError(f"Task {task_id} failed: {status}. {message}")
        time.sleep(POLL_INTERVAL)
        
    raise TimeoutError("Task polling timed out")
