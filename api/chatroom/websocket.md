## Connection

URL: `{{chatroom_ws_url}}`

- `session_token` is obtained from the `POST /{encrypted_chatroom_app_id}/session` endpoint.

## Message Sending and Receiving

### Single Client WebSocket → Service

**Format:**

A list containing exactly two elements: `[command, parameter]`

- `command`: string
- `parameter`: any type (integer, string, list, dictionary, null, etc.)

**Examples:**

```json
["ENTER", 43]
```

```json
["INPUT", "Please briefly introduce the \"Legend of Zelda\" series."]
```

**Note:**  
The list must be converted to a JSON string (`json.dumps`) before being sent to the Roundtable service.

### Service → Client WebSocket (Broadcast)

**Important:**

To support message synchronization across multiple clients in the same chatroom, every chatroom action is broadcast by the server to all clients. Therefore, the frontend should update the UI based on **both user actions and server messages**.

**Example:**  
After a user sends a message, the frontend needs to lock the input box and send button. Either of the following conditions should trigger the lock:

1. The user clicks the send button
2. The server sends a `CHAT` command

**Message formats:**

1. A string that matches the following format is treated as an instruction:

```
--NEXUSAI-INSTRUCTION-[command, parameter]--
```

The content between `--NEXUSAI-INSTRUCTION-` and `--` is a JSON-formatted instruction.

After parsing with `json.loads`, it becomes a list with two elements: `[command, parameter]`.

2. Any string that does not match the above format is treated as AI reply content (plain text stream).

**Instruction examples:**

```
--NEXUSAI-INSTRUCTION-["CHAT", "Please briefly introduce the \"Legend of Zelda\" series."]--
```

```
--NEXUSAI-INSTRUCTION-["REPLY", 1]--
```

## Command List

### Single Client WebSocket → Service

| Command | Description | Parameter | Parameter Type | Example |
|-------|-------------|-----------|----------------|---------|
| ENTER | Enter a session chatroom (must be sent once per WebSocket connection before any other operations; re-entering is not allowed) | Session chatroom ID | Int (> 0) | `["ENTER", 43]` |
| ISDESKTOP | Indicates whether the client is a desktop client | Is desktop | Bool (default: False) | `["ISDESKTOP", true]` |
| MCPTOOLLIST | List of MCP tools | Tool list | List[Dict] (default: empty list) | See example |
| TRUNCATE | Clear chatroom memory | Chatroom ID | Int (0 = current chatroom) | `["TRUNCATE", 0]` |
| SETABILITY | Set Agent ability | Ability ID | Int (0 = all abilities) | `["SETABILITY", 23]` |
| FILELIST | Files sent with the current message | File ID list | List[Int] | `["FILELIST", [120,121]]` |
| INPUT | User sends a message | Message content | Str (non-empty) | `["INPUT", "Hello"]` |
| MCPTOOLFILES | User-supplied files for tool/workflow execution | File data | Dict | See example |
| MCPTOOLRESULT | Desktop client returns MCP tool execution result | Execution result | Dict | See example |
| STOP | User clicks stop during chat | None | Null | `["STOP", null]` |

### Service → Client WebSocket (Broadcast)

| Command | Description | Parameter | Type | Frontend Action | Example |
|-------|-------------|-----------|------|-----------------|---------|
| OK | Acknowledgement for ENTER / ISDESKTOP / MCPTOOLLIST / SETABILITY / FILELIST | None | Null | Defined by frontend | `["OK", null]` |
| TRUNCATABLE | Whether the chatroom memory can be cleared | Can truncate | Bool | Enable/disable truncate button | `["TRUNCATABLE", false]` |
| TRUNCATEOK | Chatroom memory cleared successfully | Chatroom ID | Int | Defined by frontend | `["TRUNCATEOK", 13]` |
| CHAT | User message broadcast | Message content | Str | Add user bubble, lock input | `["CHAT", "Hello"]` |
| WITHFILELIST | User file list | File list | List[Dict] | Attach files to message | See example |
| REPLY | Agent is about to reply | Agent ID | Int | Create Agent bubble | `["REPLY", 23]` |
| ABILITY | Ability used by Agent | Ability ID | Int | Display ability name | `["ABILITY", 35]` |
| TEXT | Agent starts sending plain text | None | Null | Create text bubble | `["TEXT", null]` |
| MCPTOOLUSE | MCP tool invocation started | Tool details | Dict | Show tool running state | See example |
| WITHMCPTOOLFILES | User supplies additional files | File + args | Dict | Update tool bubble | See example |
| WITHWFSTATUS | Workflow execution status | Status info | Dict | Update workflow state | See example |
| WITHMCPTOOLRESULT | MCP tool execution result | Result | Dict | Update tool status | See example |
| ENDREPLY | Agent reply finished | Agent ID | Int | Defined by frontend | `["ENDREPLY", 23]` |
| ENDCHAT | Current chat round finished | None | Null | Unlock input | `["ENDCHAT", null]` |
| TITLE | Session title (desktop only) | Title | Str | Update session title | `["TITLE", "Zelda Overview"]` |
| STOPPABLE | Whether the chat can be stopped | Can stop | Bool | Update button state | `["STOPPABLE", false]` |
| ERROR | Chat error occurred | Error message | Str | Show error toast | `["ERROR", "Agent not found"]` |

## Special Commands and Parameters for Skills / Workflows

### MCPTOOLUSE - `args` Parameter

**Skill:**

```json
{
  "input_variables": {
    "key": "value"
  }
}
```

**Workflow:**

```json
{
  "input_variables": {
    "key": "value"
  },
  "node_confirm_users": {
    "node_id": "confirmer_id"
  }
}
```

### MCPTOOLUSE - `files_to_upload` Parameter

```json
{
  "name": "name",
  "variable_name": "variable_name",
  "id": 0,
  "file_name": null,
  "file_path": null
}
```

### MCPTOOLFILES - `files_to_upload` Parameter

```json
{
  "name": "name",
  "variable_name": "variable_name",
  "id": 34,
  "file_name": "file.png",
  "file_path": null
}
```

### WITHMCPTOOLFILES - `files_to_upload` Parameter

```json
{
  "name": "name",
  "variable_name": "variable_name",
  "id": 34,
  "file_name": "file.png",
  "file_path": "http://example.com/file.png"
}
```

### WITHWFSTATUS - `status` Parameter

**Running:**

```json
{
  "id": 361,
  "status": "running",
  "app_run_id": 37411,
  "node_exec_id": 20893
}
```

**Waiting for Confirmation:**

```json
{
  "id": 361,
  "status": "waiting_confirm",
  "app_run_id": 37411,
  "node_exec_id": 20894,
  "workflow_name": "Bubble Sort",
  "need_user_confirm": false,
  "show_todo_button": true
}
```

### WITHMCPTOOLRESULT - `result` Parameter

**Success:**

```json
{
  "status": "success",
  "outputs": {
    "key": "value"
  },
  "file_list": [
    {
      "file_name": "output.xlsx",
      "file_path": "http://example.com/output.xlsx",
      "variable_name": "Excel file path"
    }
  ]
}
```

**Failure:**

```json
{
  "status": "failed",
  "message": "Error message"
}
```

