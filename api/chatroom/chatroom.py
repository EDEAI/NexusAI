from core.database.models import (Chatrooms, Apps, AppRuns, AIToolLLMRecords, ChatroomAgentRelation, ChatroomMessages,
                                  Agents, Workflows, ChatroomDrivenRecords, Models)
from fastapi import APIRouter
from api.utils.common import *
from api.utils.jwt import *
from api.schema.chat import *
from languages import get_language_content
from core.workflow import (create_graph_from_dict, flatten_variable, create_variable_from_dict)
from core.llm import Messages, Prompt
import json
import sys, os
from time import time
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))
from datetime import datetime
# from api.utils.ai_tool import call_llm_for_ai_tool
from core.helper import truncate_messages_by_token_limit

from core.database.models import AppRuns

router = APIRouter()
models = Models()


@router.get("/", response_model=ChatRoomListResponse, summary="Fetching the List of Chat Rooms")
async def chatroom_list(page: int = 1, page_size: int = 10, name: str = "",
                        userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch a list of all chat rooms.

    This endpoint fetches a paginated list of all available chat rooms, allowing users to optionally filter the results by a name. The pagination is controlled through the page number and page size parameters.

    Parameters:
    - page (int): The current page number for pagination. Defaults to 1.
    - page_size (int): The number of chat rooms to return per page. Defaults to 10.
    - name (str): Optional. A string to filter chat rooms by name.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A successful response containing the list of chat rooms, formatted according to the ChatRoomListResponse model.

    Raises:
    - HTTPException: If there are issues with pagination parameters or if the user is not authenticated.
    """
    result = Chatrooms().all_chat_room_list(page, page_size, userinfo.uid, name)
    return response_success(result)


@router.post("/", response_model=CreateChatRoomResponse, summary="Create a new Chat Room")
async def create_chatroom(chat_request: ReqChatroomCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Create a new chat room with specified attributes.

    This endpoint facilitates the creation of a chat room, allowing configuration of various settings such as name, description, API access, visibility, and activation status through the provided schema. The mode parameter specifies the type of application, with a default value for chat rooms.

    Parameters:
    - chat_request (ReqChatroomCreateSchema): A schema containing all the necessary information to create a chat room, including name, description, API access settings, visibility, and activation status. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object indicating the success of the operation and containing the ID of the created chat room, formatted according to the CreateChatRoomResponse model.

    Raises:
    - HTTPException: If any of the required parameters are missing or invalid, or if the user is not authenticated.
    """
    chat_data = chat_request.dict(exclude_unset=True)
    name: str = chat_data['name']
    description: str = chat_data['description']
    max_round: int = chat_data['max_round']
    agent = chat_data['agent']
    mode: int = 5

    if not name:
        return response_error(get_language_content("chatroom_name_is_required"))

    if max_round is None or max_round == '':
        return response_error(get_language_content("chatroom_max_round_is_required"))

    if not agent or len(agent) == 0:
        return response_error(get_language_content("chatroom_agent_is_required"))
    else:
        required_keys = {'agent_id', 'active'}
        for index, item in enumerate(agent):
            if not isinstance(item, dict):
                return response_error(get_language_content("chatroom_agent_item_must_be_a_dictionary"))

            missing_keys = required_keys - item.keys()
            if missing_keys:
                return response_error(get_language_content("chatroom_agent_item_missing_keys"))

    app_id = Apps().insert(
        {
            'team_id': userinfo.team_id,
            'user_id': userinfo.uid,
            'name': name,
            'description': description,
            'mode': mode,
            'status': 1
        }
    )
    chatroom_id = Chatrooms().insert(
        {
            'team_id': userinfo.team_id,
            'user_id': userinfo.uid,
            'app_id': app_id,
            'max_round': max_round,
            'status': 1
        }
    )
    ChatroomAgentRelation().insert_agent(
        {
            'agent': agent,
            'chatroom_id': chatroom_id
        }
    )

    return response_success({'chatroom_id': chatroom_id})


@router.get("/recent", response_model=RecentChatRoomListResponse,
            summary="Fetch a List of Recently Accessed Chat Rooms")
async def recent_chatroom_list(chatroom_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch a list of chat rooms that the user has recently accessed.

    This endpoint retrieves a list of chat rooms sorted by the time of the user's last access, providing an easy way to access frequently used chat rooms.
    The list excludes the chat room with the specified chatroom_id.

    Parameters:
    - chatroom_id (int): The ID of the chat room to exclude from the recently accessed list. This could be used to exclude the current chat room from the list of recent chat rooms.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object containing the list of recently accessed chat rooms, formatted according to the RecentChatRoomListResponse model.

    Raises:
    - HTTPException: If the user is not authenticated or if there are other issues with the request.
    """
    result = Chatrooms().recent_chatroom_list(chatroom_id, userinfo.uid)
    return response_success(result)


@router.delete("/{chatroom_id}", response_model=OperationResponse, summary="Delete the Chat Room")
async def delete_chatroom(chatroom_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete a chat room by its ID.

    This endpoint allows users to delete a chat room based on the provided chat room ID. The deletion process involves setting the status of the chat room and associated app to an inactive state, rather than physically removing the data.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room to be deleted. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Raises:
    - HTTPException: If the chat room ID is missing, the user is not authenticated, or the chat room does not exist.
    """
    if not chatroom_id:
        return response_error(get_language_content("chatroom_id_is_required"))

    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    Chatrooms().update(
        [
            {"column": "id", "value": chatroom_id},
            {"column": "user_id", "value": userinfo.uid},
        ], {
            'status': 3
        }
    )
    Apps().update(
        [
            {"column": "user_id", "value": userinfo.uid},
            {"column": "id", "value": find_chatroom['app_id']},
        ], {
            'status': 3
        }
    )
    ChatroomAgentRelation().delete(
        [
            {"column": "chatroom_id", "value": chatroom_id},
        ]
    )
    return response_success({'msg': get_language_content("chatroom_delete_success")})


@router.get("/{chatroom_id}/details", response_model=ChatRoomDetailResponse, summary="Fetching Details of a Chat Room")
async def show_chatroom_details(chatroom_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch detailed information about a specific chat room.

    This endpoint fetches comprehensive details about a chat room, including associated application data and the list of agents that have joined the chat room. It serves users who need to view the configuration and participants of a chat room.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room to fetch details for. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object that contains chat room details and a list of joined agents, and records the current number of my agents and the number of agents in the team, formatted according to the ChatRoomDetailResponse model.

    Raises:
    - HTTPException: If the 'chatroom_id' is invalid, the user is not authenticated, or the chat room does not exist.
    """
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_success(
            detail=get_language_content("chatroom_does_not_exist"),
            code=1
        )

    chat_info = Apps().get_app_by_id(find_chatroom['app_id'])
    agent_list = ChatroomAgentRelation().show_chatroom_agent(chatroom_id)

    for agent in agent_list:
        agent['type'] = ''
        if agent['user_id'] == userinfo.uid:
            agent['type'] = 'my_agent'
        else:
            agent['type'] = 'more_agent'

    return response_success({
        'chat_info': chat_info,
        'agent_list': agent_list,
        'max_round': find_chatroom['max_round'],
        'smart_selection': find_chatroom['smart_selection'],
        'chatroom_status': find_chatroom['chatroom_status']
    })


@router.post("/{chatroom_id}/smart_selection", response_model=ChatRoomResponseBase,
             summary="Enables or Disables Smart Selection for a Chat Room")
async def toggle_smart_selection_switch(chatroom_id: int, data: ToggleSmartSelectionSwitch,
                                        userinfo: TokenData = Depends(get_current_user)):
    """
    Enables or Disables Smart Selection for a Chat Room.

    This endpoint allows the modification of the smart selection status of a chat room.
    It sets the smart selection status of the specified chat room based on the provided value.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room. Required.
    - data (ToggleSmartSelectionSwitch): A data model containing the new smart selection status for the chat room. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object indicating the success of the operation, formatted according to the ChatRoomResponseBase model.

    Raises:
    - HTTPException: If the 'chatroom_id' is invalid, the user is not authenticated, or the chat room does not exist.
    - HTTPException: If the 'smart_selection' value is not provided or is not one of the accepted values (0 or 1).
    """

    if not chatroom_id:
        return response_error(get_language_content("chatroom_id_is_required"))

    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    if data.smart_selection is None or data.smart_selection == '':
        return response_error(get_language_content("chatroom_smart_selection_status_is_required"))

    if data.smart_selection not in [0, 1]:
        return response_error(get_language_content("chatroom_smart_selection_status_can_only_input"))

    Chatrooms().update(
        {'column': 'id', 'value': chatroom_id},
        {'smart_selection': data.smart_selection}
    )

    return response_success()


@router.post("/{chatroom_id}/update_chatroom", response_model=UpdateChatRoomResponse, summary="Update the Chat Room")
async def update_chatroom(chatroom_id: int, chat_request: ReqChatroomUpdateSchema,
                          userinfo: TokenData = Depends(get_current_user)):
    """
    Updates an existing chat room with specified attributes.

    This endpoint allows for the modification of various chat room settings, including name, description, API access, visibility, and activation status.
    The chat room's mode is set to a default value, and the provided information is used to update the chat room's configuration.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room to be updated. Required.
    - chat_request (ReqChatroomUpdateSchema): A schema containing all the information required to update the chat room, including name, description, API access settings, visibility, and activation status. Compulsory.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object representing a successful operation and containing the updated chat room ID, formatted according to the UpdateChatRoomResponse model.

    Raises:
    - HTTPException: If any required parameters are missing or invalid, or if the user has not been authenticated.
    """
    chat_data = chat_request.dict(exclude_unset=True)
    name: str = chat_data['name']
    description: str = chat_data['description']
    max_round: int = chat_data['max_round']
    # agent = chat_data['agent']
    new_agents: List[AgentModel] = chat_data['agent']
    mode: int = 5
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    if not name:
        return response_error(get_language_content("chatroom_name_is_required"))

    if max_round is None or max_round == '':
        return response_error(get_language_content("chatroom_max_round_is_required"))

    if not new_agents or len(new_agents) == 0:
        return response_error(get_language_content("chatroom_agent_is_required"))
    else:
        required_keys = {'agent_id', 'active'}
        for index, item in enumerate(new_agents):
            if not isinstance(item, dict):
                return response_error(get_language_content("chatroom_agent_item_must_be_a_dictionary"))

            missing_keys = required_keys - item.keys()
            if missing_keys:
                return response_error(get_language_content("chatroom_agent_item_missing_keys"))

    Apps().update(
        [
            {"column": "id", "value": find_chatroom['app_id']},
            {"column": "team_id", "value": userinfo.team_id},
            {"column": "user_id", "value": userinfo.uid},
            {"column": "mode", "value": 5},
        ], {
            'name': name,
            'description': description
        }
    )

    Chatrooms().update(
        [
            {"column": "id", "value": chatroom_id}
        ], {
            'max_round': max_round
        }
    )

    existing_agents = ChatroomAgentRelation().get_agents_by_chatroom_id(chatroom_id)

    existing_agent_ids = {agent['agent_id'] for agent in existing_agents}

    new_agent_ids = {agent['agent_id'] for agent in new_agents}
    agents_to_delete = existing_agent_ids - new_agent_ids
    agents_to_add = [agent for agent in new_agents if agent['agent_id'] not in existing_agent_ids]
    agents_to_update = [agent for agent in new_agents if agent['agent_id'] in existing_agent_ids]

    if agents_to_delete:
        agent_ids = list(agents_to_delete)
        for agent_id in agent_ids:
            ChatroomAgentRelation().delete(
                [
                    {"column": "agent_id", "value": agent_id},
                    {"column": "chatroom_id", "value": chatroom_id},
                ]
            )

    if agents_to_add:
        ChatroomAgentRelation().insert_agent(
            {
                'agent': agents_to_add,
                'chatroom_id': chatroom_id
            }
        )

    if agents_to_update:
        ChatroomAgentRelation().insert_agent(
            {
                'agent': agents_to_update,
                'chatroom_id': chatroom_id
            }
        )

    return response_success({'chatroom_id': chatroom_id})


@router.put("/{chatroom_id}/agents/{agent_id}/setting", response_model=ChatRoomResponseBase,
            summary="Set the Chat Room Agent's Automatic Responses")
async def toggle_auto_answer_switch(chatroom_id: int, agent_id: int, agent_setting: ReqAgentSettingSchema,
                                    userinfo: TokenData = Depends(get_current_user)):
    """
    Set the automatic response settings for an agent in a chat room.

    This endpoint allows the modification of an agent's automatic response behavior within a chat room. It enables the setting of whether the automatic response feature is active and the frequency of automatic replies.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room where the agent's settings are to be modified. Required.
    - agent_id (int): The unique identifier of the agent whose settings are being updated. Required.
    - agent_setting (ReqAgentSettingSchema): A schema containing the settings for the agent, including whether the automatic response feature is enabled and the number of automatic responses. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object indicating the success of the operation, formatted according to the ChatRoomResponseBase model.

    Raises:
    - HTTPException: If the 'chatroom_id' or 'agent_id' is invalid, the user is not authenticated, or the chat room or agent does not exist.
    """
    if not chatroom_id:
        return response_error(get_language_content("chatroom_id_is_required"))

    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    if not agent_id:
        return response_error(get_language_content("chatroom_agent_id_is_required"))

    find_agent = Chatrooms().search_agent_id(agent_id)
    if not find_agent:
        return response_error(get_language_content("agent_does_not_exist"))

    agent_data = agent_setting.dict(exclude_unset=True)
    active = agent_data['active']

    if active is None or active == '':
        return response_error(get_language_content("chatroom_agent_active_is_required"))

    if active not in [0, 1]:
        return response_error(get_language_content("chatroom_agent_active_can_only_input"))

    find_chatroom_agent = ChatroomAgentRelation().search_chatroom_agent_relation_id(chatroom_id, agent_id)
    if not find_chatroom_agent['status']:
        return response_error(get_language_content("chatroom_agent_relation_does_not_exist"))

    if active == 0:
        agents = ChatroomAgentRelation().get_active_agents_by_chatroom_id(chatroom_id)
        if len(agents) <= 1:
            return response_error(get_language_content("chatroom_agent_number_less_than_one"))

    ChatroomAgentRelation().update(
        [
            {"column": "chatroom_id", "value": chatroom_id},
            {"column": "agent_id", "value": agent_id},
        ], {
            'active': active
        }
    )
    return response_success()


@router.get("/{chatroom_id}/chatroom_message", response_model=ChatRoomResponseBase,
            summary="Get a list of historical messages")
async def show_chatroom_details(chatroom_id: int, page: int = 1, page_size: int = 10,
                                userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve historical messages for a specific chat room.

    This endpoint retrieves historical chat information about the chat room and provides services for users who need to view chat history and participants.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room to fetch details for. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object containing the chat room details and the list of joined agents, formatted according to the HistoryChatroomMessages model.

    Raises:
    - HTTPException: If the 'chatroom_id' is invalid, the user is not authenticated, or the chat room does not exist.
    """
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    chatroom_history_msg = ChatroomMessages().history_chatroom_messages(chatroom_id, page, page_size)

    Chatrooms().update(
        {"column": "id", "value": chatroom_id},
        {'active': 0}
    )
    ChatroomMessages().update(
        {"column": "chatroom_id", "value": chatroom_id},
        {'is_read': 1}
    )

    return response_success(chatroom_history_msg)


@router.post("/{chatroom_id}/chat_history_message_summary", response_model=ChatRoomResponseBase, summary="Chat History Message Summary")
async def chat_history_summary(chatroom_id: int, chat_request: ChatHistoryMessageSummary, userinfo: TokenData = Depends(get_current_user)):
    """
    Use specified properties to query existing applications.
    Distinguish between agents and workFlows based on the current application
    By using the parameter passing rules of agent&workFlows, the splicing parameters are disassembled and the chat history is summarized through LLM to obtain the meeting summary content
    Parameters:
    -Chatroom_id (int): The unique identifier of the chat room to be updated. Compulsory.
    -Chat_dequest (ChatHistorySummary): app_run_id App Runs Data Table,corrected_parameter Correction suggestions proposed by users.

    -Userinfo (TokenData): Information about the current user is provided through dependency injection. Compulsory.


    Returns:
    - A response object representing a successful operation and containing the parameters returned by LLM for front-end processing and manual authentication.

    Raises:
    - HTTPException: If any required parameters are missing or invalid, or if the user has not been authenticated.
    """
    chat_data = chat_request.dict(exclude_unset=True)
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    conditions = [
        {"column": "chatroom_id", "value": chatroom_id},
        {'column': 'id', 'op': '>', 'value': find_chatroom['initial_message_id']},
        [
            {'column': 'chatroom_messages.agent_id', 'op': '!=', 'value': 0, 'logic': 'or'},
            {'column': 'chatroom_messages.user_id', 'op': '!=', 'value': 0}
        ]
    ]

    chat_message = ChatroomMessages().select(
        columns=['agent_id', 'message', 'topic'],
        conditions=conditions,
        order_by="id ASC",
    )

    if not chat_message:
        return response_error(get_language_content("chatroom_message_is_null"))

    chatMessageList = ChatroomMessages().get_history_list(chat_message)

    # Post added processing of chat history with long logic
    model_info = models.get_model_by_type(1, userinfo.team_id, uid=userinfo.uid)
    model_info = models.get_model_by_config_id(model_info['model_config_id'])
    chatMessageList = truncate_messages_by_token_limit(chatMessageList, model_info)

    if chat_data['corrected_parameter'] != '':
        meeting_summary = AIToolLLMRecords().select_one(
            columns=['outputs', 'inputs', 'correct_prompt'],
            conditions=[
                {"column": "app_run_id", "value": chat_data['app_run_id']},
                {"column": "ai_tool_type", "value": 3}
            ],
            order_by="created_time DESC",
        )

        if meeting_summary['inputs'] is None and meeting_summary['correct_prompt'] is None:
            # system prompt
            system_prompt = get_language_content('chatroom_generate_meeting_summary_from_a_single_message_system_correct', userinfo.uid, True)

            # user prompt
            user_prompt = get_language_content('chatroom_generate_meeting_summary_from_a_single_message_user_correct', userinfo.uid, False)
            user_prompt = user_prompt.format(
                meeting_summary=meeting_summary['outputs']['value'],
                update_meeting=chat_data['corrected_parameter']
            )
        else:
            # system prompt
            system_prompt = get_language_content('chatroom_meeting_summary_system_correct', userinfo.uid, True)

            # user prompt
            user_prompt = get_language_content('chatroom_meeting_summary_user_correct', userinfo.uid, False)
            meeting_summary = meeting_summary['outputs']['value']
            user_prompt = user_prompt.format(
                messages=json.dumps(chatMessageList, ensure_ascii=False),
                meeting_summary=meeting_summary,
                update_meeting=chat_data['corrected_parameter']
            )
    else:
        # system prompt
        system_prompt = get_language_content('chatroom_meeting_summary_system', userinfo.uid, True)

        # user prompt
        user_prompt = get_language_content('chatroom_meeting_summary_user', userinfo.uid, False)
        user_prompt = user_prompt.format(
            messages=json.dumps(chatMessageList, ensure_ascii=False),
        )
    start_time = time()
    start_datetime_str = datetime.fromtimestamp(start_time) \
        .replace(microsecond=0).isoformat(sep='_')

    input_messages = Prompt(system_prompt, user_prompt).to_dict()
    if chat_data['app_run_id'] != '':
        app_run_id = chat_data['app_run_id']
        AppRuns().update(
            {"column": "id", "value": app_run_id},
            {'status': 1}
        )
        record_id = AIToolLLMRecords().initialize_correction_record(
            app_run_id=app_run_id,
            ai_tool_type=3,
            user_prompt=chat_data['corrected_parameter'],
            correct_prompt=input_messages
        )
    else:
        app_run_id = AppRuns().insert(
            {
                'user_id': userinfo.uid,
                'app_id': 0,
                'type': 2,
                'chatroom_id': chatroom_id,
                'name': f'Chat_history_summary_{start_datetime_str}',
                'status': 1
            }
        )

        ChatroomDrivenRecords().insert(
            {
                'data_source_run_id': app_run_id,
                'chatroom_id': chatroom_id
            }
        )
        record_id = AIToolLLMRecords().initialize_execution_record(
            app_run_id=app_run_id,
            ai_tool_type=3,
            inputs=input_messages
        )
    return response_success({'app_run_id': app_run_id, 'record_id': record_id, 'message': 'Executing, please wait'})


@router.post("/{chatroom_id}/chat_history_summary", response_model=ChatRoomResponseBase, summary="Chat History Summary")
async def chat_history_summary(chatroom_id: int, chat_request: ChatHistorySummary,
                               userinfo: TokenData = Depends(get_current_user)):
    """
    Use specified properties to query existing applications.
    Distinguish between agents and workFlows based on the current application
    By using the parameter passing rules of agent&workFlows, the splicing parameters are disassembled and the chat history is summarized through LLM to obtain the meeting summary content
    Parameters:
    -Chatroom_id (int): The unique identifier of the chat room to be updated. Compulsory.
    -Chat_dequest (ChatHistorySummary): app_id Application ID, app_run_id App Runs Data Table, status Update Status 1 First Request 2 Correction,corrected_parameter Correction suggestions proposed by users.
    -Userinfo (TokenData): Information about the current user is provided through dependency injection. Compulsory.

    Returns:
    - A response object representing a successful operation and containing the parameters returned by LLM for front-end processing and manual authentication.

    Raises:
    - HTTPException: If any required parameters are missing or invalid, or if the user has not been authenticated.
    """
    chat_data = chat_request.dict(exclude_unset=True)
    app_id: int = chat_data['app_id']
    app_run_id: int = chat_data['app_run_id']
    update_status: int = chat_data['status']
    if update_status not in [1, 2]:
        return response_error(get_language_content("chatroom_status_is_incorrect"))

    app_info = Apps().get_app_by_id_search(app_id)
    if app_info is None:
        return response_error(get_language_content("api_agent_info_app_error"))

    if app_info['user_id'] != userinfo.uid:
        if app_info['is_public'] != 1:
            return response_error(get_language_content("api_agent_info_not_creators"))

    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))
    app_id = app_info["id"]

    appStatus = AppRuns().select_one(
        columns=['status'],
        conditions=[
            {"column": "id", "value": app_run_id},
            {"column": "status", "value": 3}
        ]
    )

    if appStatus is None:
        return response_error(get_language_content("chatroom_app_run_id_not_found"))

    # get ai request
    meeting_summary = AIToolLLMRecords().select_one(
        columns=['outputs'],
        conditions=[
            {"column": "app_run_id", "value": app_run_id},
            {"column": "ai_tool_type", "value": 3}
        ],
        order_by="created_time DESC",
    )
    meeting_summary = meeting_summary['outputs']['value']

    agent_id = 0
    workflow_id = 0
    prompt_variables = None
    if app_info['mode'] == 1:
        apps_model = Agents()
        agent = apps_model.select_one(
            columns=['input_variables', 'id'],
            conditions=[
                {"column": "app_id", "value": app_id},
                {"column": "status", "value": 1},
                {"column": "publish_status", "value": 1},
            ]
        )

        if agent is None:
            return response_error(get_language_content("agent_does_not_exist"))
        input_variable = create_variable_from_dict(agent['input_variables'])
        prompt_variables = [
            # {k: v for k, v in var.to_dict().items() if k not in ['required', 'max_length']}
            {k: v for k, v in var.to_dict().items() if k not in ['max_length']}
            for var in input_variable.properties.values()
        ]
        agent_id = agent['id']
        workflow_id = 0

    if app_info['mode'] == 2:
        workflow = Workflows().select_one(
            columns=['graph', 'id'],
            conditions=[
                {'column': 'app_id', 'value': app_id},
                {'column': 'status', 'value': 1},
                {'column': 'publish_status', 'value': 1}
            ]
        )
        if workflow is None:
            return
        input_var = workflow['graph']['nodes'][0]['data']['input']
        input_variable = create_variable_from_dict(input_var)
        prompt_variables = [
            # {k: v for k, v in var.to_dict().items() if k not in ['required', 'max_length']}
            {k: v for k, v in var.to_dict().items() if k not in ['max_length']}
            for var in input_variable.properties.values()
        ]
        agent_id = 0
        workflow_id = workflow['id']

    if chat_data['status'] == 2:
        # system prompt
        system_prompt = get_language_content('chatroom_conference_orientation_system_correct', userinfo.uid, True)

        # user prompt
        user_prompt = get_language_content('chatroom_conference_orientation_user_correct', userinfo.uid, False)

        meeting_summary_return = AIToolLLMRecords().select_one(
            columns=['outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "ai_tool_type", "value": 4}
            ],
            order_by="created_time DESC",
        )
        meeting_summary_return = meeting_summary_return['outputs']['value']
        meeting_summary_return = json.loads(meeting_summary_return)
        input_variable = create_variable_from_dict(meeting_summary_return)
        meeting_summary_return = [
            # {k: v for k, v in var.to_dict().items() if k not in ['required', 'max_length']}
            {k: v for k, v in var.to_dict().items() if k not in ['max_length']}
            for var in input_variable.properties.values()
        ]

        user_prompt = user_prompt.format(
            meeting_summary=meeting_summary,
            value_meeting_summary=meeting_summary_return,
            update_meeting=chat_data['corrected_parameter']
        )
    else:
        # system prompt
        system_prompt = get_language_content('chatroom_conference_orientation_system', userinfo.uid, True)

        # user prompt
        user_prompt = get_language_content('chatroom_conference_orientation_user', userinfo.uid, False)

        user_prompt = user_prompt.format(
            meeting_summary=meeting_summary,
            prompt_variables=prompt_variables
        )

    input_messages = Prompt(system_prompt, user_prompt).to_dict()
    if update_status == 1:
        AppRuns().update(
            {"column": "id", "value": app_run_id},
            {
                'agent_id': agent_id,
                'workflow_id': workflow_id,
                'status': 1
            }
        )
        record_id = AIToolLLMRecords().initialize_execution_record(
            app_run_id=app_run_id,
            ai_tool_type=4,
            inputs=input_messages
        )
    else:
        AppRuns().update(
            {"column": "id", "value": app_run_id},
            {'status': 1}
        )
        record_id = AIToolLLMRecords().initialize_correction_record(
            app_run_id=app_run_id,
            ai_tool_type=4,
            correct_prompt=input_messages,
            user_prompt=chat_data['corrected_parameter']
        )
    return response_success({'app_run_id': app_run_id, 'record_id': record_id, 'message': 'Executing, please wait'})


@router.post("/{chatroom_id}/chat_single_message_generation", response_model=ChatRoomResponseBase, summary="Generate meeting summary from a single message")
async def chat_single_message_generation(chatroom_id: int, chat_request: ChatSingleMessage, userinfo: TokenData = Depends(get_current_user)):
    """
    Generate a meeting summary from a single message in a specified chat room.

    This endpoint processes a single message within a chat room to generate a meeting summary using a Language Model (LLM).
    It distinguishes between agents and workflows based on the current application and uses the parameter passing rules
    of agents and workflows to disassemble the parameters and summarize the chat history.

    Parameters:
    - chatroom_id (int): The unique identifier of the chat room to be updated. This is a required parameter.
    - chat_request (ChatSingleMessage): The request object containing the message to be processed. This is a required parameter.
        - message (str): The content of the chat room message to be summarized.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. This is a required parameter.

    Returns:
    - A response object (ChatRoomResponseBase) representing a successful operation. The response contains the parameters returned by the LLM for front-end processing and manual verification.

    Raises:
    - HTTPException: If any required parameters are missing or invalid, or if the user has not been authenticated.
    """
    chat_data = chat_request.dict(exclude_unset=True)
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    # conditions = [
    #     {"column": "chatroom_id", "value": chatroom_id},
    #     {"column": "id", "value": chatroom_message_id},
    #     {'column': 'id', 'op': '>', 'value': find_chatroom['initial_message_id']},
    #     [
    #         {'column': 'chatroom_messages.agent_id', 'op': '!=', 'value': 0, 'logic': 'or'},
    #         {'column': 'chatroom_messages.user_id', 'op': '!=', 'value': 0}
    #     ]
    # ]
    #
    # chat_message = ChatroomMessages().select_one(
    #     columns=['message'],
    #     conditions=conditions
    # )
    #
    if chat_data['message'] is None:
        return response_error(get_language_content("chatroom_message_is_not_find"))

    start_time = time()
    start_datetime_str = datetime.fromtimestamp(start_time) \
        .replace(microsecond=0).isoformat(sep='_')

    outputs = {
        "name": "text",
        "type": "string",
        "value": chat_data['message'],
        "max_length": 0
    }

    app_run_id = AppRuns().insert(
        {
            'user_id': userinfo.uid,
            'app_id': 0,
            'type': 2,
            'chatroom_id': chatroom_id,
            'name': f'Chat_single_message_generation_{start_datetime_str}',
            'status': 3,
            'outputs': outputs
        }
    )
    record_id = AIToolLLMRecords().insert(
        {
            'app_run_id': app_run_id,
            'ai_tool_type': 3,
            'status': 3,
            'run_type': 1,
            'loop_id': 0,
            'loop_limit': 0,
            'loop_count': 0,
            'outputs': outputs
        }
    )

    ChatroomDrivenRecords().insert(
        {
            'data_source_run_id': app_run_id,
            'chatroom_id': chatroom_id
        }
    )
    return response_success(
        {'app_run_id': app_run_id, 'record_id': record_id, 'outputs': outputs, 'message': 'Processing successful'})



@router.get('/chat_room_history', response_model=ChatRoomHistoryList)
async def get_chat_room_history(
    chatroom_id: int,
    page: int = 1,
    page_size: int = 10,
    userinfo: TokenData = Depends(get_current_user)
):
    """Get chat room history including meeting summaries, corrections, and directed actions."""
    find_chatroom = Chatrooms().search_chatrooms_id(chatroom_id, userinfo.uid)
    if not find_chatroom['status']:
        return response_error(get_language_content("chatroom_does_not_exist"))

    result = ChatroomDrivenRecords().get_history_by_chatroom_id(
        chatroom_id=chatroom_id,
        page=page,
        page_size=page_size
    )
    return response_success(result)