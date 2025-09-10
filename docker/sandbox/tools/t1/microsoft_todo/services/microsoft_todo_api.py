import requests

class MicrosoftTodoApiException(Exception):
    def __init__(self, message: str, code: int = None, response: requests.Response = None):
        self.message = message
        self.code = code
        self.response = response
        super().__init__(self.__str__())  # force str message at init

    def __str__(self):
        detail = ""
        if self.response is not None:
            try:
                detail = self.response.json()
            except Exception:
                detail = self.response.text
        if self.code:
            return f"[Error {self.code}] {self.message} → {detail}"
        return f"{self.message} → {detail}" if detail else self.message


BASE_URL = "https://graph.microsoft.com/v1.0/me/todo/lists"


def _headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


def get_default_task_list_id(access_token: str) -> str:
    try:
        print("📥 Fetching task lists...")
        response = requests.get(BASE_URL, headers=_headers(access_token))
        print("📬 Response status:", response.status_code)
        response.raise_for_status()
        data = response.json()
        print("📦 Lists response:", data)

        if data.get("value"):
            print("✅ Found existing list.")
            return data["value"][0]["id"]

        print("🆕 No lists found. Creating a new one...")
        create_response = requests.post(
            BASE_URL,
            headers=_headers(access_token),
            json={"displayName": "Default List"}
        )
        print("🛠️ Create list response status:", create_response.status_code)
        print("📦 Create response body:", create_response.text)

        create_response.raise_for_status()
        created = create_response.json()
        print("✅ Created new list:", created)
        return created["id"]

    except requests.RequestException as e:
        print("❌ Exception during get/create:", str(e))
        raise MicrosoftTodoApiException(
            "Failed to get or create default task list.",
            code=e.response.status_code if e.response else None,
            response=e.response if e.response else None
        )




def create_todo(access_token: str, title: str, due_date: str = None) -> dict:
    try:
        task_list_id = get_default_task_list_id(access_token)
        payload = {"title": title}
        if due_date:
            payload["dueDateTime"] = {"dateTime": due_date, "timeZone": "UTC"}

        response = requests.post(
            f"{BASE_URL}/{task_list_id}/tasks",
            headers=_headers(access_token),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise MicrosoftTodoApiException(
            "Failed to create todo.",
            code=response.status_code if 'response' in locals() else None,
            response=response if 'response' in locals() else None
        )


def get_todos(access_token: str, include_completed: str = "false") -> list[dict]:
    try:
        task_list_id = get_default_task_list_id(access_token)
        if include_completed == "only":
            filter_query = "?$filter=status eq 'completed'"
        elif include_completed == "false":
            filter_query = "?$filter=status ne 'completed'"
        else:
            filter_query = ""

        response = requests.get(
            f"{BASE_URL}/{task_list_id}/tasks{filter_query}",
            headers=_headers(access_token)
        )
        response.raise_for_status()
        return response.json()["value"]
    except requests.RequestException as e:
        raise MicrosoftTodoApiException(
            "Failed to fetch todos.",
            code=response.status_code if 'response' in locals() else None,
            response=response if 'response' in locals() else None
        )


def delete_todo(access_token: str, task_id: str) -> bool:
    try:
        task_list_id = get_default_task_list_id(access_token)
        response = requests.delete(
            f"{BASE_URL}/{task_list_id}/tasks/{task_id}",
            headers=_headers(access_token)
        )
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        raise MicrosoftTodoApiException(
            "Failed to delete todo.",
            code=response.status_code if 'response' in locals() else None,
            response=response if 'response' in locals() else None
        )


def mark_todo_completed(access_token: str, task_id: str) -> dict:
    try:
        task_list_id = get_default_task_list_id(access_token)
        payload = {"status": "completed"}
        response = requests.patch(
            f"{BASE_URL}/{task_list_id}/tasks/{task_id}",
            headers=_headers(access_token),
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise MicrosoftTodoApiException(
            "Failed to mark todo as completed.",
            code=response.status_code if 'response' in locals() else None,
            response=response if 'response' in locals() else None
        )
