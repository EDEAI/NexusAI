import httpx
from typing import Dict, Any, List, Optional
import json
import os


def d1_executor(sql_query: str, params: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a SQL query on the Cloudflare D1 database using environment variables.

    Args:
        sql_query: SQL query to be executed (using ? as placeholders)
        params: SQL query parameters as a stringified array, e.g.:
               - Single string parameter: '["value1"]'
               - Multiple parameters: '["value1", "value2"]'
               - With numbers: '["value1", 42]'
               - With null: '["value1", null]'
               Pass None or empty string if no parameters needed.

    Returns:
        Dict containing query results from cloudflare_d1_query.
        On success: {"success": True, "metadata": response_data}
        On failure: {"error": error_type, "metadata": error_details}

    Note:
        The params argument must be a string representation of a JSON array,
        whose elements will replace the ? placeholders in order of appearance.
    """
    account_id = os.getenv("CF_ACCOUNT_ID")
    database_id = os.getenv("CF_DATABASE")
    api_token = os.getenv("CF_API_TOKEN")

    result = cloudflare_d1_query(account_id, database_id, api_token, sql_query, params)
    # print(f"\n========================================{result}\n========================================")
    return result


def cloudflare_d1_query(
    account_id: str,
    database_id: str,
    api_token: str,
    sql_query: str,
    params: Optional[str],
) -> Dict[str, Any]:
    """
    Execute a query on the Cloudflare D1 database.

    Args:
        account_id: Cloudflare account ID
        database_id: D1 database ID
        api_token: Cloudflare API Bearer Token
        sql_query: SQL query to execute (using ? as placeholders)
        params: SQL query parameters as a stringified array, e.g.:
               - Single string parameter: '["value1"]'
               - Multiple parameters: '["value1", "value2"]'
               - With numbers: '["value1", 42]'
               - With null: '["value1", null]'
               Pass None or empty string if no parameters needed.

    Returns:
        Dict containing query results. On success: {"success": True, "metadata": response_data}
        On failure: {"error": error_type, "metadata": error_details}

    Note:
        The params argument must be a string representation of a JSON array,
        whose elements will replace the ? placeholders in order of appearance.
    """
    # Parameter validation
    if not account_id:
        return {"error": "invalid_parameter", "metadata": "account_id cannot be empty"}
    if not database_id:
        return {"error": "invalid_parameter", "metadata": "database_id cannot be empty"}
    if not sql_query:
        return {"error": "invalid_parameter", "metadata": "sql_query cannot be empty"}

    query_params: List[Any] = []

    if params:
        try:
            query_params = json.loads(params)
            if not isinstance(query_params, list):
                return {
                    "error": "invalid_parameter",
                    "metadata": 'params must be a JSON array string, e.g., \'["value1", "value2"]\'',
                }
        except json.JSONDecodeError as e:
            return {
                "error": "invalid_parameter",
                "metadata": f"params is not a valid JSON string: {str(e)}",
            }

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    data = {"sql": sql_query, "params": query_params}

    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()
        return {"success": True, "metadata": response.json()}

    except httpx.HTTPError as e:  # Simplified HTTPError handling
        try:
            error_data = e.response.json()  # Attempt to get JSON, even if it fails
        except json.JSONDecodeError:
            # Fallback if not JSON
            error_data = {"response_text": e.response.text}

        return {
            "error": "http_request_error",
            "metadata": {
                "http_status": e.response.status_code,
                "detail": str(e),
                # Include the entire payload (JSON or text)
                "response_payload": error_data,
            },
        }
    except json.JSONDecodeError as e:
        return {"error": "json_decode_error", "metadata": str(e)}
    except Exception as e:
        return {"error": "other_error", "metadata": str(e)}


def cloudflare_token_verify(token):
    """
    Verifies a Cloudflare API token by calling the Cloudflare token verification endpoint.

    Args:
        token (str): The Cloudflare API token to verify.

    Returns:
        dict: A dictionary representing the verification result.
              Returns a dictionary in the format:
              - On successful verification (status active and success true):
                {'success': True, 'message': 'Token is valid and active', 'data': <full cloudflare response>}
              - On unsuccessful verification (status not active or success false):
                {'success': False, 'error': 'Token verification failed: <reason>', 'data': <full cloudflare response>}
              - On HTTP errors during the request:
                {'success': False, 'error': 'HTTP error during token verification: <error message>', 'details': <error details>}
              - On other exceptions during the request:
                {'success': False, 'error': 'Unexpected error during token verification: <error message>', 'details': <exception details>}
    """
    try:
        response = httpx.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get("success") and data.get("result", {}).get("status") == "active":
            return {
                "success": True,
                "message": "Token is valid and active",
                "data": data,
            }
        else:
            error_message = "Token verification failed: "
            if not data.get("success"):
                error_message += (
                    f"API request was not successful. Errors: {data.get('errors')}"
                )
            elif data.get("result", {}).get("status") != "active":
                error_message += f"Token status is not active. Status: {data.get('result', {}).get('status')}"
            else:  # Fallback in case of unexpected response structure
                error_message += "Unknown verification failure."
            return {"success": False, "error": error_message, "data": data}

    except httpx.HTTPStatusError as e:
        error_detail = {}
        try:
            # Try to get more details from response body if it's JSON
            error_detail = e.response.json()
        except ValueError:  # If response body is not JSON
            error_detail = {
                "status_code": e.response.status_code,
                "text": e.response.text,
            }
        return {
            "success": False,
            "error": f"HTTP error during token verification: {e}",
            "details": error_detail,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error during token verification: {e}",
            "details": {
                "exception_type": type(e).__name__,
                "exception_message": str(e),
            },
        }


def cloudflare_d1_result_success(result: Dict[str, Any]) -> bool:
    """
    Check if a Cloudflare D1 query result is successful.

    Args:
        result (Dict[str, Any]): The result dictionary from cloudflare_d1_query

    Returns:
        bool: True if the query was successful, False otherwise
    """
    if not result.get("success"):
        return False

    metadata = result.get("metadata", {})
    if not metadata.get("success"):
        return False

    # Check if there's at least one result object and it was successful
    results = metadata.get("result", [])
    if not results or not results[0].get("success", False):
        return False

    return True
