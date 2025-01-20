import os
from typing import Any

# Dictionary to store language codes and their corresponding language names
language_names = {
    "en": "English",
    "zh": "Chinese",
}

# Define the language pack dictionary structure
language_packs = {
    "en": {
        "requirement_category": {
            "system": """
                You are a content categorization assistant.
                Please analyze which category my input belongs to based on my input content, category judgment criteria, and all category sets. If you are not sure, please choose the category that is closest to my input content.
                The result should be returned in JSON format, as follows: {format}.
            """,
            "user": """
                My input content: {requirement}.
                Category judgment criteria: {judgment_criteria}.
                All category sets: {categories}.
            """,
        },
        "agent_system_prompt_with_auto_match_ability": (
            'Your responsibilities (or identity) are as follows:\n'
            '{obligations}\n\n'
            'You have some abilities, each ability is in the form of a tuple (ability ID, specific information of the ability, output format of the ability) in the following Python list:\n'
            '{abilities_content_and_output_format}\n\n'
            '{reply_requirement}\n'
            'Finally, return a JSON formatted dictionary as follows:\n'
            '{{"ability_id": ability ID (integer type), "output": content replied in the corresponding format of the ability}}'
        ),
        "agent_system_prompt_with_abilities": (
            'Your responsibilities (or identity) are as follows:\n'
            '{obligations}\n\n'
            'You have the following abilities:\n'
            '{abilities_content}\n\n'
            '{reply_requirement}\n'
            'Finally, return a JSON formatted dictionary as follows:\n'
            '{{"output": content replied in {output_format} format}}'
        ),
        "agent_system_prompt_with_no_ability": (
            'Your responsibilities (or identity) are as follows:\n'
            '{obligations}\n\n'
            '{reply_requirement}\n'
            'Finally, return a JSON formatted dictionary as follows:\n'
            '{{"output": content replied in {output_format} format}}'
        ),
        "agent_reply_requirement_with_auto_match_ability": (
            'Please match one corresponding ability based on the user input information and reply in the format corresponding to the ability.'
        ),
        "agent_reply_requirement_with_abilities": (
            'Please reply based on the user input information.'
        ),
        "agent_reply_requirement_with_no_ability": (
            'Please reply based on the user input information.'
        ),
        "agent_reply_requirement_with_task_splitting_and_auto_match_ability": (
            'Please match one corresponding ability based on the user input information, and based on your responsibilities and abilities, select the part of the overall task that you should be responsible for and process it, and reply in the format corresponding to the ability.'
        ),
        "agent_reply_requirement_with_task_splitting_and_abilities": (
            'Based on your responsibilities and abilities, select the part of the overall task that you should be responsible for and process it.'
        ),
        "agent_reply_requirement_with_task_splitting_and_no_ability": (
            'Based on your responsibilities, select the part of the overall task that you should be responsible for and process it.'
        ),
        "agent_output_format_1": "plain text",
        "agent_output_format_2": "JSON",
        "agent_output_format_3": "code",
        "agent_user_prompt_with_retrieved_docs": (
            'Below is the text input by the user:\n'
            '{user_prompt}\n\n'
            'Below is the information retrieved from the knowledge base based on the user input text '
            '(listed in the following JSON format: [{{"content": content, "source": source document name}}, ...])'
            ':\n'
            '{formatted_docs}\n\n'
            'Please reply to the user based on the above information.'
        ),
        "llm_reply_requirement_with_task_splitting": (
            'Please select the part of the overall task that you should be responsible for and process it.'
        ),
        "recursive_task_generation": {
            "system": """
                Please generate detailed task data according to the requirements, task generation goals and task data structure I provided, and try to split the steps and levels of the task in more detail.
                Task data json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: specific task content, subcategories: sub-task list}}.
                Note that the hierarchical structure of task data is infinitely recursive, and the structure of each element in the sub-task list is consistent with the parent structure.
                Pay attention to the uniqueness of the task id. You can use this format: parent task id-current task id. The previous parent task id is recursively superimposed according to the level, and finally splice task- in front of each task id.
                Note that task keywords should be extracted according to the task content. The keywords should cover the task content as comprehensively as possible, but do not contain irrelevant words. Keywords are separated by commas.
                Finally, they should be returned in json format according to the task data structure.
                Note that the definition of "task data" mentioned above is not necessarily a "task" in the literal sense. It may be any content that can be split into steps or levels. It should be understood and defined according to the requirements and task generation goals I provided.
            """,
            "user": """
                Requirement content: {requirement}
                Task generation goals: {task_generation_goals}
            """,
        },
        "recursive_task_assign": {
            "system": """
                Please select the most suitable executor for the current task based on the current task content, parent task content for reference only, executor selection requirements, and all task executors provided by me. Please select according to the executor selection requirements and the specific functions of each executor. If you are not sure, please select the executor with the closest function and task content.
                Task json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: task corresponding requirement content}}.
                Task executor json structure description: {{id: executor id, name: executor name, description: executor description, obligations: executor specific functions}}.
                In the end, only the selected executor id must be returned, and no redundant content must be returned.
            """,
            "user": """
                Current task content: {current_task}
                Parent task content for reference only: {parent_task}
                Executor selection requirements: {executor_selection_requirements}
                All task executors: {executors}
            """,
        },
        "recursive_task_execute": {
            "system": """
                You are a task executor. Please perform the current task as detailed as possible according to your specific responsibilities and abilities, the requirements and goals of the current task, the current task content I provide, the parent task content for reference only, the subtask list for reference only, and the related task content for reference only.
                When performing the current task, pay attention to the following points:
                1. The current task must be performed strictly in accordance with the requirements and goals of the current task.
                2. If your responsibilities and abilities have actual content, refer to your responsibilities and ability settings.
                3. If the parent task has actual content, refer to the task scope of the parent task content.
                4. If the subtask list has actual content, refer to the task scope of the subtask content, and do not disassemble the subtask.
                5. If the related task has actual content, please note that it is only for related reference.
                Task json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: task content}}.
                In the end, only the task content you performed will be returned, and no redundant content will be returned.
            """,
            "user": """
                Your responsibilities and abilities: {obligations}
                Requirements and goals of the current task: {requirements_and_goals}
                Current task content: {current_task}
                Parent task content for reference only: {parent_task}
                Subtask list for reference only: {child_tasks}
                Related task content for reference only: {related_content}
            """,
        },

        # HTTP requeust node
        'http_request_failed': 'HTTP request failed with status code {status_code}',
        'http_response_content_oversize': 'HTTP response content is too large, max size is {max_size} bytes, but current size is {size} bytes',

        # register(user)
        "register_nickname_empty": "login has failed，Nickname cannot be empty",
        "register_nickname_long": "login has failed，Nickname too long",
        "register_inviter_id_empty": "login has failed，The inviter ID is empty",
        "register_team_id_empty": "login has failed，The Team ID is empty",
        "register_phone_failed": "login has failed，The phone number cannot be empty",
        "register_email_failed": "login has failed，Email cannot be empty",
        "register_password_failed": "login has failed，Password cannot be empty",
        "register_failed": "login has failed，try again",
        "register_phone_illegality": "Registration failed, illegal phone number",
        "register_email_illegality": "Registration failed, email address is invalid",
        "register_phone_repeat": "Registration failed, duplicate phone number",
        "register_email_repeat": "Registration failed, duplicate email address",
        "register_email_empty": "Registration failed, the user has not been invited yet",
        # register(team)
        "register_team_name_empty": "login has failed，Team name cannot be empty",
        "register_team_name_repeat": "login has failed，Duplicate team names",
        "register_team_name_legal": "login has failed，The team name is illegal",
        # login
        "login_user_name_empty": "Login failed, Username cannot be empty",
        "login_user_name_failed": "Login failed, Username incorrect",
        "login_user_name_absent": "Login failed, Username does not exist",
        "login_user_password_empty": "Login failed, Password cannot be empty",
        "login_user_password_failed": "Login failed, Password error",

        "login_time_last_year": "Last year",
        "login_time_a_month_ago": "A month ago",
        "login_time_days_ago": "Days ago",
        "login_time_hours_ago": "Hours ago",
        "login_time_minutes_ago": "Minutes ago",
        "login_time_just": "Just",
        "login_time_never_logged_in": "Never logged in",
        # lnvitation
        'lnvitation_already_failed': 'Invitation failed, the email has already been registered',
        'lnvitation_role_failed': 'Invitation failed, insufficient role permissions',
        'lnvitation_email_failed': 'Invitation failed, email cannot be empty',
        'lnvitation_team_failed': 'Invitation failed, team data does not exist',
        'lnvitation_failed': 'Invitation failed, please try again',
        # workflow
        'publish_failed': 'Workflow publishing failure',
        'publish_success': 'Workflow published successfully',
        'no_available_workflows': 'There is no workflow available',
        'node_id_is_not_exist': 'The workflow node does not exist',
        'executor_not_exist': 'The executor does not exist',
        'parent_node_is_not_rte_node': 'The parent node is not Task Execution Node',
        # language
        'switch_the_language_failed': 'Switch language failed',
        'switch_the_language_success': 'Switch language success',
        # agent
        'agent_does_not_exist': 'Agent does not exist',
        'agent_empty_obligation': 'Agent obligation should not be empty!',
        'agent_empty_llm_model': 'Please fill in the LLM model for the Agent!',
        'agent_empty_ability': 'Agent ability should not be empty!',
        'agent_empty_prompt': 'Prompt should not be empty!',
        'api_agent_success': 'success',
        'api_agent_info_app_id_required': 'app_id is required',
        'api_agent_info_app_error': 'app error',
        'api_agent_info_publish_status_error': 'publish_status can only input 0 or 1',
        'api_agent_info_not_creators': 'Only creators can view drafts',
        'api_agent_info_team_not_open': 'Team members are not open',
        'api_agent_info_app_status_not_normal': 'The app status is not normal',
        'api_agent_info_agent_error': 'Agent error',
        'api_agent_info_agent_status_not_normal': 'The agent status is not normal',
        'api_agent_run_agent_id_required': 'agent_id is required',
        'api_agent_run_input_dict_required': 'input_dict is required',
        'api_agent_run_input_dict_wrong': 'input_dict data in wrong format',
        'api_agent_run_prompt_required': 'prompt is required',
        'api_agent_run_prompt_wrong': 'prompt data in wrong format',
        'api_agent_run_agent_error': 'agent error',
        'api_agent_run_agent_status_not_normal': 'The agent status is not normal',
        'api_agent_run_not_creators': 'Only creators can run drafts agent',
        'api_agent_run_app_error': 'app error',
        'api_agent_run_team_not_open': 'Team members are not open',
        'api_agent_run_app_status_not_normal': 'The app status is not normal',
        'api_agent_run_ability_error': 'ability error',
        'api_agent_run_ability_status_not_normal': 'The ability status is not normal',
        'api_agent_base_update_agent_id_required': 'agent_id is required',
        'api_agent_base_update_is_public_error': 'is_public can only input 0 or 1',
        'api_agent_base_update_enable_api_error': 'enable_api can only input 0 or 1',
        'api_agent_base_update_input_variables_wrong': 'input_variables data in wrong format',
        'api_agent_base_update_m_config_id_required': 'm_config_id is required',
        'api_agent_base_update_allow_upload_file_error': 'allow_upload_file can only input 0 or 1',
        'api_agent_base_update_default_output_format_error': 'default_output_format can only input 1 or 2 or 3',
        'api_agent_base_update_agent_error': 'agent error',
        'api_agent_base_update_datasets_error': 'datasets data error',
        'api_agent_base_update_model_configuration_error': 'model configuration error',
        'api_agent_base_update_apps_update_error': 'apps update error',
        'api_agent_base_update_agents_update_error': 'agents update error',
        'api_agent_base_update_agent_dataset_insert_error': 'agent dataset relation insert error',
        'api_agent_base_update_agent_base_update_error': 'agent base update error',
        'api_agent_abilities_set_agent_id_required': 'agent_id is required',
        'api_agent_abilities_set_auto_match_ability_error': 'auto_match_ability can only input 0 or 1',
        'api_agent_abilities_set_agent_error': 'agent error',
        'api_agent_abilities_set_abilities_name_required': 'abilities name is required',
        'api_agent_abilities_set_abilities_content_required': 'abilities content is required',
        'api_agent_abilities_set_abilities_status_error': 'abilities status can only input 1 or 2',
        'api_agent_abilities_set_output_format_error': 'output_format can only input 0 or 1 or 2 or 3',
        'api_agent_abilities_set_agent_abilities_error': 'agent abilities data error',
        'api_agent_abilities_set_agents_update_error': 'agents update error',
        'api_agent_abilities_set_abilities_update_error': 'abilities update error',
        'api_agent_abilities_set_abilities_insert_error': 'abilities insert error',
        'api_agent_abilities_set_agent_abilities_set_error': 'agent abilities set error',
        'api_agent_output_set_agent_id_required': 'agent_id is required',
        'api_agent_output_set_default_output_format_error': 'default_output_format can only input 1 or 2 or 3',
        'api_agent_output_set_agent_error': 'agent error',
        'api_agent_output_set_agent_ability_id_required': 'agent_ability_id is required',
        'api_agent_output_set_agent_ability_id_duplication': 'agent_ability_id duplication',
        'api_agent_output_set_output_format_error': 'output_format can only input 1 or 2 or 3',
        'api_agent_output_set_abilities_output_format_error': 'abilities output format data error',
        'api_agent_output_set_agents_update_error': 'agents update error',
        'api_agent_output_set_abilities_update_error': 'abilities update error',
        'api_agent_output_set_agent_output_set_error': 'agent output set error',
        'api_agent_publish_agent_id_required': 'agent_id is required',
        'api_agent_publish_agent_error': 'agent error',
        'api_agent_publish_app_error': 'app error',
        'api_agent_publish_agent_update_error': 'publish agent update error',
        'api_agent_publish_agent_insert_error': 'publish agent insert error',
        'api_agent_publish_agent_dataset_insert_error': 'agent dataset relation insert error',
        'api_agent_publish_abilities_insert_error': 'abilities insert error',
        'api_agent_publish_app_update_error': 'publish app update error',
        'api_agent_publish_agent_publish_error': 'agent publish error',
        'api_agent_delete_app_id_required': 'app_id is required',
        'api_agent_delete_app_error': 'app error',
        'api_agent_delete_agent_error': 'agent error',
        'api_agent_delete_delete_app_error': 'delete app error',
        'api_agent_delete_delete_agent_error': 'delete agent error',
        'api_agent_delete_agent_delete_error': 'agent delete error',
        'api_agent_batch_create_failed': 'Batch create failed',
        # meeting room
        'chatroom_name_is_required': 'meeting room name is required',
        'chatroom_max_round_is_required': 'max_round is required',
        'chatroom_agent_is_required': 'agent is required',
        'chatroom_agent_item_must_be_a_dictionary': 'agent item must be a dictionary',
        'chatroom_agent_item_missing_keys': 'agent item missing keys',
        'chatroom_id_is_required': 'meeting room id is required',
        'chatroom_does_not_exist': 'meeting room does not exist',
        'chatroom_user_id_not_exist': 'meeting room Illegal user access',
        'chatroom_delete_success': 'meeting room delete success',
        'chatroom_smart_selection_status_is_required': 'meeting room smart selection status is required',
        'chatroom_message_is_null': 'The message content cannot be empty',
        'chatroom_message_is_not_find': 'Chat room messages cannot be empty',
        'chatroom_smart_selection_status_can_only_input': 'meeting room smart selection status can only input 0 or 1',
        'chatroom_agent_id_is_required': 'agent_id is required',
        'chatroom_agent_active_is_required': 'agent active is required',
        'chatroom_agent_active_can_only_input': 'agent active can only input 0 or 1',
        'chatroom_agent_relation_does_not_exist': 'agent relation does not exist',
        'chatroom_status_is_incorrect': 'The current status is incorrect',
        'chatroom_agent_number_less_than_one': 'There must be at least 1 agent present in the meeting room.',
        'chatroom_manager_system': (
            'You are the moderator of the meeting room, where there is one user and at least one AI agent.\n'
            'You are responsible for selecting the next agent to speak.\n'
            'I will provide a list of detailed information about all agents in the meeting room in the following JSON format:'
            '[{"id": agent ID, "name": agent name, "description": agent responsibilities and capabilities}, ...];\n'
            'And the chat history list in the following JSON format:'
            '[message, ...];\n'
            'The JSON structure for each message is as follows:'
            '{"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": speaker role (user or agent), "message": message content, "topic": meeting topic}.\n\n'
            'First, you need to analyze the current meeting topic from the user\'s latest message content. The meeting topic should not be too concise, try to be detailed, and do not copy the meeting topic from historical messages.\n'
            'Then, respond according to the following requirements:\n'
            '1. Please only select agents from the provided agent list. Do not select agents that exist in the chat history but not in the agent list;\n'
            '2. Please select the next agent to speak based on the current meeting topic and all agents\' responsibilities and capabilities. If you are unsure, please select the agent whose responsibilities and capabilities most closely match the historical message content;\n'
            '3. Please return in JSON format: {"topic": current meeting topic, "id": the ID of the agent you selected}. Sometimes an agent\'s name might look like an ID number, but you must still return the agent\'s ID, not their name.'
        ),

        'chatroom_manager_system_with_optional_selection': (
            'You are the moderator of the meeting room, where there is one user and at least one AI agent.\n'
            'You are responsible for selecting the next agent to speak or ending the conversation.\n'
            'I will provide a list of detailed information about all agents in the meeting room in the following JSON format:'
            '[{"id": agent ID, "name": agent name, "description": agent responsibilities and capabilities}, ...];\n'
            'And the current meeting topic;\n'
            'Also, the chat history list in the following JSON format:'
            '[message, ...];\n'
            'The JSON structure for each message is as follows:'
            '{"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": speaker role (user or agent), "message": message content, "topic": meeting topic}.\n\n'
            'You should determine whether to end the conversation according to the following rules:\n'
            '1. You should try to encourage all agents to actively participate in the dialogue regarding the current meeting topic;\n'
            '2. You should also analyze the coherence of agent responses. If there is no content related to the current meeting topic in the content of the last message in the chat history (the content of the "message" field), please end the conversation. Note that only the last message in the chat history is considered, and no other messages are considered.\n\n'
            'Then, respond according to the following requirements:\n'
            '1. If you think the conversation should end, please only return in JSON format: {"id": 0, "message": reason for ending the conversation}; otherwise, select an agent according to the following requirements.\n'
            '2. Please only select agents from the provided agent list. Do not select agents that exist in the chat history but not in the agent list;\n'
            '3. Please select the next agent to speak based on the current meeting topic, chat history, and all agents\' responsibilities and capabilities. If you are unsure, please select the agent whose responsibilities and capabilities most closely match the current meeting topic;\n'
            '4. Please return in JSON format: {"id": the ID of the agent you selected}. Sometimes an agent\'s name might look like an ID number, but you must still return the agent\'s ID, not their name.'
        ),

        'chatroom_manager_user_invalid_selection': (
            'Your last selected ID was {agent_id}, but this ID does not correspond to any agent in the meeting room. Please select again.\n\n'
        ),

        'chatroom_manager_user': (
            'Total number of agents: {agent_count}\n'
            'Below is the detailed information list of all agents in the meeting room:\n'
            '{agents}\n\n'
            'Below is the chat history list:\n'
            '{messages}\n\n'
            'User\'s latest message content: {user_message}\n'
            'Please select the next agent to speak from the agent list according to the requirements.'
        ),

        'chatroom_manager_user_with_optional_selection': (
            'Total number of agents: {agent_count}\n'
            'Below is the detailed information list of all agents in the meeting room:\n'
            '{agents}\n\n'
            'Current meeting topic: {topic}\n'
            'Below is the chat history list:\n'
            '{messages}\n\n'
            'Please select the next agent to speak from the agent list according to the requirements, or end the conversation.'
        ),

        'chatroom_agent_system': (
            'You are an AI agent in the meeting room, where there is one user and at least one AI agent.\n'
            'Please respond based on the current meeting topic and your responsibilities and capabilities description.\n'
            'I will provide the current meeting topic;\n'
            'And the chat history list in the following JSON format:'
            '[message, ...];\n'
            'The JSON structure for each message is as follows:'
            '{"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": speaker role (user or agent), "message": message content, "topic": meeting topic}.\n\n'
            'I will also provide your ID, name, responsibilities, and capabilities description.\n'
            'Your response must follow these requirements:\n'
            '1. You must respond within your responsibilities and capabilities based on the current meeting topic.\n'
            '2. If your responsibilities and capabilities are not directly related to the current meeting topic, please try to adapt to the topic and provide relevant responses, rather than being limited to your specific responsibilities and capabilities.\n'
            '3. Note that historical messages are for reference only. Do not meaninglessly repeat content from historical messages in your response.\n'
            '4. Make sure to respond with text content only, do not wrap your response in the JSON structure used in the message history.\n'
            '5. The ID I provide to you is only for context recognition. Do not mention anything related to IDs in your response.\n'
            '6. Do not explicitly mention the current topic in your response unless the user specifically asks about it.'
        ),

        'chatroom_agent_user_with_abilities': (
            'Below is the chat history list:\n'
            '{messages}\n\n'
            'Current meeting topic: {topic}\n'
            'Your ID: {id_}\n'
            'Your name: {name}\n\n'
            'Below are your responsibilities (or identity):'
            '{obligations}\n\n'
            'Below are your capabilities (listed in JSON format):\n'
            '{abilities}\n\n'
            'Please speak according to these contents and requirements.'
        ),

        'chatroom_agent_user_with_no_ability': (
            'Below is the chat history list:\n'
            '{messages}\n\n'
            'Current meeting topic: {topic}\n'
            'Your ID: {id_}\n'
            'Your name: {name}\n\n'
            'Below are your responsibilities (or identity):'
            '{obligations}\n\n'
            'Please speak according to these contents and requirements.'
        ),

        'chatroom_agent_description_with_abilities': (
            'Agent responsibilities (or identity):\n'
            '{obligations}\n\n'
            'Agent capabilities (listed in JSON format):\n'
            '{abilities}'
        ),

        'chatroom_agent_description_with_no_ability': (
            'Agent responsibilities (or identity):\n'
            '{obligations}'
        ),
        'chatroom_request_sent_successfully': 'Request successful, please wait',
        'chatroom_role_user': 'user',
        'chatroom_role_agent': 'agent',
        # vector
        'api_vector_auth': 'Insufficient permissions',
        'api_vector_file_type': 'The uploaded file information is not matched',
        'api_vector_success': 'success',
        'api_vector_document_loader_type': 'Please provide a valid document_loader_type!',
        'api_vector_embedding_model': 'No available embedding model!',
        'api_vector_available_dataset': 'No available dataset!',
        'api_vector_available_model': 'No available model!',
        'api_vector_document_segment': 'No available document segment!',
        'api_vector_available_document': 'No available document!',
        'api_vector_available_apps': 'No available apps!',
        'api_vector_acquisition_failure': 'Data acquisition failure',
        'api_vector_indexing': 'The knowledge base is being indexed and cannot be changed',
        # upload files
        'upload_files': 'Uploaded file list',
        'api_upload_unsupported': 'Unsupported file types',
        'api_upload_max_size': 'The file size exceeds the 15MB limit',
        'api_upload_size_not': 'Could not get file size',
        # app list
        'app_search_type': '"Error switching team/personal mode',
        # app create
        'name_is_required': 'Name is required',
        'mode_can_only_input': ' App mode is error',
        'apps_insert_error': 'App create failed',
        'agents_insert_error': 'Agent create failed',
        'workflow_insert_error': 'Workflow create failed',
        'workflow_import_copy': 'Copy',
        'workflow_import_invalid_format': 'Invalid YAML file format',
        'workflow_import_item_is_required': 'Missing field in YAML file: ',
        'workflow_import_name_is_required': 'Missing application name in YAML file',
        'workflow_import_mode_error': 'In YAML file, workflow mode must be 2',
        'workflow_import_graph_error': 'Workflow graph data error',
        'workflow_import_insert_error': 'Failed to create workflow',
        'database_insert_error': 'Database create failed',
        'skill_insert_error': 'Skill create failed',
        'apps_insert_success': 'App create success',

        'app_id_is_required': 'APPID is error',
        'app_update_error': 'app update failed',
        'app_update_success': 'app update success',
        'no_modification_permission': 'no_modification_permission',

        'supplier_not_found': 'Supplier not found',
        'supplier_authorized_success': 'Supplier authorized successfully',

        'model_not_found': 'Model not found',
        'model_authorized_success': 'Model authorized successfully',

        'model_switching_success': 'Model switching successfully',
        'model_switching_failed': 'Model switching failed',

        'skill_does_not_exist': 'Skill does not exist',
        'skill_input_variables_error': 'Skill input variables error',
        'skill_output_variables_error': 'Skill output variables error',
        'skill_code_error': 'Skill code error',

        'do_not_have_permission': 'Do not have permission',

        'LLM_HELP': 'Set the default large language model. When you create an agent or use a large language model in a workflow, this model will be used by default.',
        'EMBEDDING_HELP': 'Set the default model for document embedding processing, the retrieval and import of knowledge bases both use this Embedding model for vectorization processing.',
        'RERANKING_HELP': 'Reranking model will reorder the candidate document list based on the semantic matching degree with the user\'s question, thereby improving the semantic sorting result',
        'SPEECH2TEXT_HELP': 'Set the default model for speech-to-text input in the dialog.',
        'TTS_HELP': 'text-to-speech model, used to convert text content into natural speech output.',
        'TEXT2IMG_HELP': 'text-to-image model, used to generate images according to the input text description.',
        'MODERATION_HELP': 'Content moderation model, used to detect and filter inappropriate content to ensure that the generated content conforms to community standards.',

        'LLM_MODEL_TYPE_NAME': 'LLM Model',
        'EMBEDDING_MODEL_TYPE_NAME': 'Embedding Model',
        'RERANKING_MODEL_TYPE_NAME': 'Rerank Model',
        'SPEECH2TEXT_MODEL_TYPE_NAME': 'Speech2Text Model',
        'TTS_MODEL_TYPE_NAME': 'TTS Model',
        'TEXT2IMG_MODEL_TYPE_NAME': 'Text2Img Model',
        'MODERATION_MODEL_TYPE_NAME': 'Moderation Model',

        'recently_active_process': 'Recently active process',
        'recently_active_agent': 'Recently active Agent',
        "graph_validation_errors": {
            "inputs_cannot_be_empty": "The Start node has no input variables set.",
            "multiple_start_nodes": "There can only be one start node.",
            "multiple_end_nodes": "There can only be one end node.",
            "multiple_level_one_edges": "There can only be one edge with level 1.",
            "invalid_level_one_edge_source": "The source node of the level 1 edge must be a start node.",
            "nonexistent_edge_nodes": "All edges must have source and target nodes that exist in the nodes list.",
            "start_node_incoming_edges": "Start node cannot have incoming edges.",
            "start_node_outgoing_edges": "Start node can only have one outgoing edge.",
            "end_node_incoming_edges": "End node must have at least one incoming edge.",
            "end_node_outgoing_edges": "End node cannot have outgoing edges.",
            "node_incoming_outgoing_edges": "Node {node_id} must have at least one incoming and one outgoing edge.",
            "exactly_one_start_node": "There must be exactly one start node.",
            "exactly_one_end_node": "There must be exactly one end node."
        },
        'tag_id_not_found': 'Tag ID not found',
        'tag_update_success': 'Tag update success',
        'tag_update_failed': 'Tag update failed',
        'tag_delete_success': 'Tag delete success',
        'tag_binding_create_success': 'Tag binding create success',
        'tag_binding_delete_success': 'Tag binding delete success',
        'team_id_not_found': 'Team ID not found',
        'chatroom_app_run_id_not_found': 'Current appRunID not found',

        'app_run_error': 'App run record not found',
        'api_agent_generate_failed': 'Agent generate failed',
        'api_agent_user_prompt_required': 'Agent user prompt required',
        'api_agent_batch_size_invalid': 'Agent batch size invalid',
        'agent_batch_exist_runing_rocord': 'Agent generate exist runing rocord',
        
        'generate_agent_system_prompt': '''
            You are an AI agent generation assistant.
            Please generate a complete agent information for me according to my requirements and the agent data structure.
            Please pay attention to the following requirements when generating:
            1. The agent name should be highly anthropomorphic
            2. The agent description should be as detailed as possible and cover all the information of the agent
            3. The agent's functional information should be as detailed as possible, not just limited to the literal "functional" information, but also include other relevant feature information
            4. The ability splitting of the agent should be as detailed as possible, the specific content of each ability should be described in detail, and the output format of the ability should be selected in an appropriate format
            5. Be sure to strictly abide by the json structure of the agent data
            Note that only the json structure data of the agent is returned, and no redundant content is returned.
            Description of the json structure of agent data:
            {{
                "name": "(string type) Agent name",
                "description": "(string type) Agent description",
                "obligations": "(string type) Agent functional information (including but not limited to the identity, responsibilities, positions, skills, etc. of the agent)",
                "abilities": [
                    {{
                        "name": "(string type) Ability name",
                        "content": "(string type) Specific content of the ability. When the agent is running, the selected ability content will be submitted to the LLM model as a prompt",
                        "output_format": "(int type), the output format of the ability, 1: text format, 2: json format, 3: pure code format (excluding non-code content), when the agent is running, the content will be returned according to the output format corresponding to the selected ability"
                    }}
                ]
            }}
            {append_prompt}
        ''',
        'generate_agent_user': '''
            Requirement content:
            {user_prompt}
        ''',
        'regenerate_agent_system': '''
            Note: You have already generated some agents, and you need to generate a new agent. The new agent data should be as different as possible from the generated agent history data.
        ''',
        'regenerate_agent_user': '''
            Generated agent history data:
            {history_agent_list}
        ''',
        'agent_supplement_system': '''
            You are an AI agent generation assistant.
            You have generated an agent. Please adjust the generated agent data according to the correction suggestions I provided.
            Note that only the json structure data of the agent is returned, and no redundant content is returned.
            Description of the json structure of agent data:
            {{
                "name": "(string type) Agent name",
                "description": "(string type) Agent description",
                "obligations": "(string type) Agent functional information (including but not limited to the identity, responsibilities, positions, skills, etc. of the agent)",
                "abilities": [
                    {{
                        "name": "(string type) Ability name",
                        "content": "(string type) Specific content of the ability. When the agent is running, the selected ability content will be submitted to the LLM model as a prompt",
                        "output_format": "(int type), the output format of the ability, 1: text format, 2: json format, 3: pure code format (excluding non-code content), when the agent is running, the content will be returned according to the output format corresponding to the selected ability"
                    }}
                ]
            }}
        ''',
        'agent_supplement_user': '''
            Correction suggestions:
            {agent_supplement}

            Generated agent data:
            {history_agent}
        ''',
        'agent_batch_sample_system': '''
            You are an AI agent generation assistant.
            Please generate a complete sample agent information for me according to the agent data structure based on the requirements for batch generation of agents provided by me.
            Please pay attention to the following requirements when generating:
            1. The agent name should be highly anthropomorphic
            2. The agent description should be as detailed as possible and cover all the information of the agent
            3. The agent's functional information should be as detailed as possible, not just limited to the literal "functional" information, but also include other relevant feature information
            4. The ability splitting of the agent should be as detailed as possible, the specific content of each ability should be described in detail, and the output format of the ability should be selected in an appropriate format
            5. Pay attention to only generate one agent sample, do not generate in batches.
            6. Be sure to strictly abide by the json structure of the agent data
            Note that only the json structure data of the agent is returned, and no redundant content is returned.
            Description of the json structure of agent data:
            {{
                "name": "(string type) Agent name",
                "description": "(string type) Agent description",
                "obligations": "(string type) Agent functional information (including but not limited to the identity, responsibilities, positions, skills, etc. of the agent)",
                "abilities": [
                    {{
                        "name": "(string type) Ability name",
                        "content": "(string type) Specific content of the ability. When the agent is running, the selected ability content will be submitted to the LLM model as a prompt",
                        "output_format": "(int type), the output format of the ability, 1: text format, 2: json format, 3: pure code format (excluding non-code content), when the agent is running, the content will be returned according to the output format corresponding to the selected ability"
                    }}
                ]
            }}
        ''',
        'agent_batch_sample_user': '''
            Requirements for batch generation of agents:
            {agent_batch_requirements}
        ''',
        'agent_batch_generate_system': '''
            You are an AI agent generation assistant.
            Please generate a batch of complete agent information for me based on the requirements for batch generation of agents, the number of batch generation of agents, and the data structure of multiple agents that I provide.
            Pay attention to the following requirements when generating:
            1. The name of the agent should be highly anthropomorphic
            2. The agent description should be as detailed as possible and cover all the information of the agent
            3. The function information of the agent should be as detailed as possible, not just limited to the literal "function" information, but also include other relevant feature information
            4. The ability splitting of the agent should be as detailed as possible, the specific content of each ability should be described in detail, and the output format of the ability should be selected in an appropriate format
            5. Be sure to strictly generate agents according to the number of batch-generated agents I provide, and do not generate more or less than this number
            6. The batch-generated agent data should be kept as different as possible, and do not generate duplicate agents
            7. If the batch-generated agent history has real content, the new agent should be kept as different as possible from the generated agent history
            8. Be sure to strictly abide by the multi-agent data json structure
            Note that only the generated multi-agent json structure data is returned, and no redundant content is returned.
            Description of the json structure of multi-agent data:
            {{
                "multi-agent": [
                    {{
                        "name": "(string type) Agent name",
                        "description": "(string type) Agent description",
                        "obligations": "(string type) Agent functional information (including but not limited to the identity, responsibilities, positions, skills, etc. of the agent)",
                        "abilities": [
                            {{
                                "name": "(string type) Ability name",
                                "content": "(string type) Specific content of the ability. When the agent is running, the selected ability content will be submitted to the LLM model as a prompt",
                                "output_format": "(int type), the output format of the ability, 1: text format, 2: json format, 3: pure code format (excluding non-code content), when the agent is running, the content will be returned according to the output format corresponding to the selected ability"
                            }}
                        ]
                    }}
                ]
            }}
        ''',
        'agent_batch_generate_user': '''
            Requirements for batch generation of agents:
            {agent_batch_requirements}

            Number of batch generation of agents:
            {agent_batch_number}

            Batch-generated agent history:
            {history_agents}
        ''',
        'api_agent_supplement_prompt_required': 'supplement_prompt is requiredapi_agent_generate_failed',
        'api_agent_save_record_error': 'save record errorapp_run_error',
        'api_agent_record_error': 'record not found',
        
        'chatroom_meeting_summary_system': '''
            You are a meeting summary assistant. Please summarize the meeting based on the meeting chat history I provided. The meeting summary should be as detailed as possible.
            Note that only the meeting summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_meeting_summary_user': '''
            Meeting chat history:
            {messages}
        ''',
        'chatroom_meeting_summary_system_correct': '''
            You are a conference content summary assistant. You have made a conference summary through the conference chat history I provided. I provided you with the generated conference summary.
            Please adjust the generated conference summary through the conference chat history I provided, the generated conference summary, and the conference summary corrections.
            Note that only the corrected conference summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_meeting_summary_user_correct': '''
            Conference chat history:
            {messages}

            Generated conference summary:
            {meeting_summary}

            Conference summary corrections:
            {update_meeting}
        ''',
        'chatroom_generate_meeting_summary_from_a_single_message_system_correct': '''
            You are a meeting summary assistant. You have generated a meeting summary for me. I have provided you with the generated meeting summary.
            Please adjust the generated meeting summary based on the generated meeting summary and meeting summary corrections I provided.
            Note that only the corrected meeting summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_generate_meeting_summary_from_a_single_message_user_correct': '''
            Generated meeting summary:
            {meeting_summary}

            Meeting summary corrections:
            {update_meeting}
        ''',
        'chatroom_conference_orientation_system': '''
            You are a data conversion assistant. Please use the meeting summary content and work-oriented data I provided to perform data-oriented conversion.
            Pay attention to the following requirements during conversion:
            1. Pay attention to the split items in the work-oriented data I provided. Be sure to keep the original split items, do not create new split items, and do not delete split items.
            2. The final generated work-oriented data must meet the requirements of the work-oriented data json format. Do not change the data structure.
            3. Be sure to pay attention to the field description and requirements in the work-oriented data json format description, as well as the work-oriented data supplementary description I provided. The two are combined as split reference rules.
            4. Remember that the four fields of name, display_name, required, and type in the work-oriented data I provided must not be changed. You only need to fill in the value field with the split item content.
            5. Be sure to strictly abide by the work-oriented data json format. Note that only the generated json format content is returned in the end, and no redundant content is returned.

            Work-oriented data json format description:
            1. Structural type description: The data corresponding to variables is of list type as a whole. Each element in the list is a data split item, and the data split item is of dict type
            2. Format, field description and requirements:
            {{
                'variables': [
                    {{
                        name: The variable name corresponding to the split item. Do not change this field.
                        required: The variable required corresponding Is it mandatory. Do not change this field.
                        display_name: The variable display name corresponding to the split item. It can be used as a description of the function and purpose of the split item and as a basis for extracting the split item. Do not change this field.
                        type: The variable type corresponding to the split item. It can be "number" or "string". Note that the content of the split item must correspond to the variable type. Do not change this field.
                        value: The final work-oriented split item content
                    }}
                ]
            }}
        ''',
        'chatroom_conference_orientation_user': '''
            Meeting summary content:
            {meeting_summary}

            Work-oriented data:
            {{'variables':{prompt_variables}}}
            
            Supplementary description of work-oriented data:
            {prompt_variables_supplement}
        ''',
        'chatroom_conference_orientation_system_correct': '''
            You are a data conversion assistant. You have already conducted a data-oriented conversion through the meeting summary content I provided. I provided the converted work-oriented data.
            Please adjust the converted work-oriented data through the meeting summary content I provided, the converted work-oriented data, and the data correction suggestions.
            Pay attention to the following requirements when adjusting:
            1. Pay attention to the split items in the work-oriented data I provided. Be sure to keep the original split items, do not create new split items, and do not delete split items.
            2. The final generated work-oriented data must meet the json format requirements of the work-oriented data. Do not change the data structure.
            3. Be sure to pay attention to the field description and requirements in the json format description of the work-oriented data, and use this as a reference rule for splitting.
            4. Remember that the four fields of name, display_name, required, and type in the work-oriented data I provided must not be changed. You only need to fill in the value field with the split item content.
            5. Be sure to strictly abide by the data correction suggestions.
            6. Be sure to strictly abide by the json format of the work-oriented data. Note that only the generated json format content is returned in the end, and do not return redundant content.

            JSON format description of work-oriented data:
            1. Structural type description: The data corresponding to variables is of list type as a whole. Each element in the list is a data split item, and the data split item is of dict type
            2. Format, field description and requirements:
            {{
                'variables': [
                    {{
                        name: The variable name corresponding to the split item. Do not change this field.
                        required: The variable required corresponding Is it mandatory. Do not change this field.
                        display_name: The variable display name corresponding to the split item. It can be used as a description of the function and purpose of the split item and as a basis for extracting the split item. Do not change this field.
                        type: The variable type corresponding to the split item. It can be "number" or "string". Note that the content of the split item must correspond to the variable type. Do not change this field.
                        value: The final content of the work-oriented split item
                    }}
                ]
            }}
        ''',
        'chatroom_conference_orientation_user_correct': '''
            Meeting summary content:
            {meeting_summary}

            Converted work-oriented data:
            {{'variables':{value_meeting_summary}}}

            Data correction suggestions:
            {update_meeting}
        ''',
        'api_skill_success': 'success',
        'api_skill_generate_failed': 'Request failed, please try again later',
        'api_skill_correction_failed': 'Request failed, please try again later',
        'api_skill_user_prompt_required': 'Prompt is required',
    },
    "zh": {
        'http_request_failed': 'HTTP请求失败，错误码：{status_code}',
        'http_response_content_oversize': 'HTTP响应内容过大！最大不应超过{max_size}字节，而实际为{size}字节',

        "register_nickname_empty": "注册失败，昵称不能为空",
        "register_nickname_long": "注册失败，昵称过长",
        "register_team_id_empty": "注册失败，团队ID为空",
        "register_inviter_id_empty": "注册失败，邀请人ID为空",
        "register_phone_failed": "注册失败，手机号不能为空",
        "register_email_failed": "注册失败，邮箱不能为空",
        "register_password_failed": "注册失败，密码不能为空",
        "register_failed": "注册失败，请重试",
        "register_phone_illegality": "注册失败，手机号不合法",
        "register_email_illegality": "注册失败，邮箱不合法",
        "register_phone_repeat": "注册失败，手机号重复",
        "register_email_repeat": "注册失败，邮箱重复",
        "register_email_empty": "注册失败，暂未邀请该用户",

        "register_team_name_empty": "注册失败，团队名不能为空",
        "register_team_name_repeat": "注册失败，团队名称重复",
        "register_team_name_legal": "注册失败，团队名称不合法",

        "login_user_name_empty": "登录失败，用户名不能为空",
        "login_user_name_failed": "登录失败，用户名错误",
        "login_user_name_absent": "登录失败，用户名不存在",
        "login_user_password_empty": "登录失败，密码不能为空",
        "login_user_password_failed": "登录失败，密码错误",

        "login_time_last_year": "年前",
        "login_time_a_month_ago": "月前",
        "login_time_days_ago": "天前",
        "login_time_hours_ago": "小时前",
        "login_time_minutes_ago": "分钟前",
        "login_time_just": "刚刚",
        "login_time_never_logged_in": "从未登录",

        'lnvitation_already_failed': '邀请失败，该邮箱已注册',
        'lnvitation_role_failed': '邀请失败，角色权限不足',
        'lnvitation_email_failed': '邀请失败，邮箱不能为空',
        'lnvitation_team_failed': '邀请失败，团队数据不存在',
        'lnvitation_failed': '邀请失败，请重试',

        'publish_failed': '工作流发布失败',
        'publish_success': '工作流发布成功',
        'no_available_workflows': '没有可用的工作流',
        'node_id_is_not_exist': '工作流节点不存在',
        'executor_not_exist': '执行器不存在',
        'parent_node_is_not_rte_node': '父节点不是任务执行节点',

        'switch_the_language_failed': '切换语言失败',
        'switch_the_language_success': '切换语言成功',

        'agent_does_not_exist': '智能体不存在！',
        'agent_empty_obligation': '智能体职能不应为空！',
        'agent_empty_llm_model': '请填写智能体的LLM模型！',
        'agent_empty_ability': '智能体能力不应为空！',
        'agent_empty_prompt': '提示词不应为空！',
        'api_agent_success': '成功',
        'api_agent_info_app_id_required': '应用ID是必传的',
        'api_agent_info_app_error': '未获取到应用信息',
        'api_agent_info_publish_status_error': '发布状态只能输入0或1',
        'api_agent_info_not_creators': '只有创建者可以查看草稿',
        'api_agent_info_team_not_open': '团队成员不开放',
        'api_agent_info_app_status_not_normal': '应用状态不正确',
        'api_agent_info_agent_error': '未获取到智能体信息',
        'api_agent_info_agent_status_not_normal': '智能体状态不正确',
        'api_agent_run_agent_id_required': '智能体ID是必传的',
        'api_agent_run_input_dict_required': '输入字典是必传的',
        'api_agent_run_input_dict_wrong': '输入字典数据格式错误',
        'api_agent_run_prompt_required': '提示词是必传的',
        'api_agent_run_prompt_wrong': '提示词数据格式错误',
        'api_agent_run_agent_error': '未获取到智能体信息',
        'api_agent_run_agent_status_not_normal': '智能体状态不正确',
        'api_agent_run_not_creators': '只有创建者可以运行草稿智能体',
        'api_agent_run_app_error': '应用状态不正确',
        'api_agent_run_team_not_open': '团队成员不开放',
        'api_agent_run_app_status_not_normal': '应用状态不正确',
        'api_agent_run_ability_error': '未获取到能力信息',
        'api_agent_run_ability_status_not_normal': '能力状态不正确',
        'api_agent_base_update_agent_id_required': '智能体ID是必传的',
        'api_agent_base_update_is_public_error': '是否团队可见只能输入0或1',
        'api_agent_base_update_enable_api_error': '启用接口只能输入0或1',
        'api_agent_base_update_input_variables_wrong': '输入变量数据格式错误',
        'api_agent_base_update_m_config_id_required': '模型配置ID是必传的',
        'api_agent_base_update_allow_upload_file_error': '允许上传文件只能输入0或1',
        'api_agent_base_update_default_output_format_error': '默认输出格式只能输入1或2或3',
        'api_agent_base_update_agent_error': '未获取到智能体信息',
        'api_agent_base_update_datasets_error': '知识库信息错误',
        'api_agent_base_update_model_configuration_error': '模型配置错误',
        'api_agent_base_update_apps_update_error': '更新应用失败',
        'api_agent_base_update_agents_update_error': '更新智能体失败',
        'api_agent_base_update_agent_dataset_insert_error': '添加智能体知识库关联失败',
        'api_agent_base_update_agent_base_update_error': '更新智能体主数据失败',
        'api_agent_abilities_set_agent_id_required': '智能体ID是必传的',
        'api_agent_abilities_set_auto_match_ability_error': '自动匹配能力只能输入0或1',
        'api_agent_abilities_set_agent_error': '未获取到智能体信息',
        'api_agent_abilities_set_abilities_name_required': '能力名称是必传的',
        'api_agent_abilities_set_abilities_content_required': '能力描述是必传的',
        'api_agent_abilities_set_abilities_status_error': '能力状态只能输入1或2',
        'api_agent_abilities_set_output_format_error': '输出格式只能输入0或1或2或3',
        'api_agent_abilities_set_agent_abilities_error': '智能体能力数据错误',
        'api_agent_abilities_set_agents_update_error': '更新智能体失败',
        'api_agent_abilities_set_abilities_update_error': '更新能力失败',
        'api_agent_abilities_set_abilities_insert_error': '添加能力失败',
        'api_agent_abilities_set_agent_abilities_set_error': '智能体能力设置失败',
        'api_agent_output_set_agent_id_required': '智能体ID是必传的',
        'api_agent_output_set_default_output_format_error': '默认输出格式只能输入1或2或3',
        'api_agent_output_set_agent_error': '未获取到智能体信息',
        'api_agent_output_set_agent_ability_id_required': '智能体能力ID是必传的',
        'api_agent_output_set_agent_ability_id_duplication': '智能体能力ID重复',
        'api_agent_output_set_output_format_error': '输出格式只能输入1或2或3',
        'api_agent_output_set_abilities_output_format_error': '能力输出格式数据错误',
        'api_agent_output_set_agents_update_error': '更新智能体失败',
        'api_agent_output_set_abilities_update_error': '更新能力失败',
        'api_agent_output_set_agent_output_set_error': '智能体输出设置错误',
        'api_agent_publish_agent_id_required': '智能体ID是必传的',
        'api_agent_publish_agent_error': '未获取到智能体信息',
        'api_agent_publish_app_error': '未获取到应用信息',
        'api_agent_publish_agent_update_error': '更新发布智能体错误',
        'api_agent_publish_agent_insert_error': '添加发布智能体错误',
        'api_agent_publish_agent_dataset_insert_error': '添加智能体知识库关联失败',
        'api_agent_publish_abilities_insert_error': '添加能力失败',
        'api_agent_publish_app_update_error': '更新发布应用错误',
        'api_agent_publish_agent_publish_error': '智能体发布失败',
        'api_agent_delete_app_id_required': '应用ID是必传的',
        'api_agent_delete_app_error': '未获取到应用信息',
        'api_agent_delete_agent_error': '未获取到智能体信息',
        'api_agent_delete_delete_app_error': '删除应用失败',
        'api_agent_delete_delete_agent_error': '删除智能体失败',
        'api_agent_delete_agent_delete_error': '智能体删除失败',
        'api_agent_batch_create_failed': '批量创建智能体失败',

        'chatroom_name_is_required': '会议室标题不能为空',
        'chatroom_max_round_is_required': '最大回合数不能为空',
        'chatroom_agent_is_required': '智能体不能为空',
        'chatroom_agent_item_must_be_a_dictionary': '智能体的每个元素必须是一个字典',
        'chatroom_agent_item_missing_keys': '智能体的元素缺少必要的键',
        'chatroom_id_is_required': '会议室ID不能为空',
        'chatroom_does_not_exist': '会议室不存在',
        'chatroom_user_id_not_exist': '非法用户进入',
        'chatroom_delete_success': '删除会议室成功',
        'chatroom_smart_selection_status_is_required': '会议室择优应答状态不能为空',
        'chatroom_message_is_null': '消息内容不能为空',
        'chatroom_message_is_not_find': '聊天室消息不能为空',
        'chatroom_smart_selection_status_can_only_input': '会议室择优应答状态只能输入0或1',
        'chatroom_agent_id_is_required': '智能体ID不能为空',
        'chatroom_agent_active_is_required': '智能体状态不能为空',
        'chatroom_agent_active_can_only_input': '智能体状态只能输入0或1',
        'chatroom_agent_relation_does_not_exist': '智能体关系不存在',
        'chatroom_agent_number_less_than_one': '会议室中必须存在至少1个智能体',

        'api_vector_auth': '权限不足',
        'api_vector_file_type': '上传的文件信息不匹配',
        'api_vector_success': '成功',
        'api_vector_document_loader_type': '请提供有效的document_loader_type！',
        'api_vector_embedding_model': '没有可用的嵌入模型！',
        'api_vector_available_dataset': '没有可用的数据集！',
        'api_vector_available_model': '没有可用的模型！',
        'api_vector_document_segment': '没有可用的文档段！',
        'api_vector_available_document': '没有可用的文档！',
        'api_vector_available_apps': '没有可用的应用程序！',
        'api_vector_acquisition_failure': '数据采集失败',
        'api_vector_indexing': '知识库正在建立索引，不能更改',

        'upload_files': '上传文件列表',
        'api_upload_unsupported': '不支持的文件类型',
        'api_upload_max_size': '文件大小超过15MB限制',
        'api_upload_size_not': '无法获取文件大小',

        'app_search_type': '切换团队/个人错误',

        'name_is_required': '应用名称是必填的',
        'mode_can_only_input': '应用类型错误',
        'apps_insert_error': '应用创建失败',
        'agents_insert_error': '智能体应用创建失败 ',
        'workflow_insert_error': '工作流应用创建失败',
        'workflow_import_copy': '副本',
        'workflow_import_invalid_format': 'YAML文件格式错误',
        'workflow_import_item_is_required': 'YAML文件中缺少字段：',
        'workflow_import_name_is_required': 'YAML文件中缺少应用名称',
        'workflow_import_mode_error': 'YAML文件中，工作流的mode必须为2',
        'workflow_import_graph_error': '工作流图数据错误',
        'workflow_import_insert_error': '工作流创建失败',
        'database_insert_error': '知识库应用创建失败',
        'skill_insert_error': '技能应用创建失败',
        'apps_insert_success': '应用创建成功',

        'app_id_is_required': '应用ID错误',
        'app_update_error': '应用更新失败',
        'app_update_success': '应该更新成功',
        'no_modification_permission': '无修改权限',

        'supplier_not_found': '供应商不存在',
        'supplier_authorized_success': '供应商授权成功',

        'model_not_found': '模型不存在',
        'model_authorized_success': '模型授权成功',

        'model_switching_success': '模型切换成功',
        'model_switching_failed': '模型切换失败',

        'skill_does_not_exist': '技能不存在',
        'skill_input_variables_error': '技能输入变量错误',
        'skill_output_variables_error': '技能输出变量错误',
        'skill_code_error': '技能代码错误',

        'do_not_have_permission': '没有权限',

        'LLM_HELP': '设置默认大语言模型，创建智能体以及工作流中使用大语言模型的节点会默认使用该模型。',
        'EMBEDDING_HELP': '设置知识库文档嵌入处理的默认模型，检索和导入知识库均使用该Embedding模型进行向量化处理。',
        'RERANKING_HELP': '重排序模型将根据候选文档列表与用户问题语义匹配度进行重新排序，从而改进语义排序的结果',
        'SPEECH2TEXT_HELP': '设置对话中语音转文字输入的默认使用模型。',
        'TTS_HELP': '文本转语音模型，用于将文本内容转换为自然的语音输出。',
        'TEXT2IMG_HELP': '文本生成图像模型，根据输入的文本描述生成相应的图像。',
        'MODERATION_HELP': '内容审核模型，用于检测和过滤不当内容，确保生成内容符合社区标准。',

        'LLM_MODEL_TYPE_NAME': 'LLM模型',
        'EMBEDDING_MODEL_TYPE_NAME': 'Embedding模型',
        'RERANKING_MODEL_TYPE_NAME': 'Rerank模型',
        'SPEECH2TEXT_MODEL_TYPE_NAME': 'Speech2Text模型',
        'TTS_MODEL_TYPE_NAME': 'TTS模型',
        'TEXT2IMG_MODEL_TYPE_NAME': 'Text2Img模型',
        'MODERATION_MODEL_TYPE_NAME': 'Moderation模型',

        'recently_active_process': '最近运行进程',
        'recently_active_agent': '最近活跃智能体',
        "graph_validation_errors": {
            "inputs_cannot_be_empty": "开始节点未设置输入变量。",
            "multiple_start_nodes": "只能有一个开始节点。",
            "multiple_end_nodes": "只能有一个结束节点。",
            "multiple_level_one_edges": "只能有一个一级edge。",
            "invalid_level_one_edge_source": "一级edge的源节点必须是开始节点。",
            "nonexistent_edge_nodes": "所有edge的源节点和目标节点必须存在于节点列表中。",
            "start_node_incoming_edges": "开始节点不能有传入edge。",
            "start_node_outgoing_edges": "开始节点只能有一个传出edge。",
            "end_node_incoming_edges": "结束节点必须至少有一个传入edge。",
            "end_node_outgoing_edges": "结束节点不能有传出edge。",
            "node_incoming_outgoing_edges": "节点 {node_id} 必须至少有一个传入edge和一个传出edge。",
            "exactly_one_start_node": "必须有且只有一个开始节点。",
            "exactly_one_end_node": "必须有且只有一个结束节点。"
        },
        'tag_id_not_found': '标签ID不存在',
        'tag_update_success': '标签更新成功',
        'tag_update_failed': '标签更新失败',
        'tag_delete_success': '标签删除成功',
        'tag_binding_create_success': '标签绑定创建成功',
        'tag_binding_delete_success': '标签绑定删除成功',
        'team_id_not_found': '团队ID不存在',
        'chatroom_app_run_id_not_found': '当前appRunID未找到',
        'chatroom_status_is_incorrect': '当前状态不正确',
        
        # 'chatroom_meeting_summary_system': '''
        #     你是一个会议内容总结助手，请通过我提供的会议聊天历史进行会议总结，会议总结内容要尽量详细。
        #     注意最终只返回会议总结内容，不要返回多余的内容。
        # ''',
        # 'chatroom_meeting_summary_user': '''
        #     会议聊天历史：
        #     {messages}
        # ''',
        # 'chatroom_meeting_summary_system_correct': '''
        #     你是一个会议内容总结助手，你已经通过我提供的会议聊天历史进行了一次会议总结，我提供了你已生成的会议总结。
        #     请通过我提供的会议聊天历史，已生成的会议总结，以及会议总结修正意见，对已生成的会议总结进行调整。
        #     注意最终只返回修正后的会议总结内容，不要返回多余的内容。
        # ''',
        # 'chatroom_meeting_summary_user_correct': '''
        #     会议聊天历史：
        #     {messages}
            
        #     已生成的会议总结：
        #     {meeting_summary}

        #     会议总结修正意见：
        #     {update_meeting}
        # ''',

        # 'chatroom_generate_meeting_summary_from_a_single_message_system_correct': '''
        #     你是一个会议内容总结助手，你已经为我生成了一次会议总结，我提供了你已生成的会议总结。
        #     请通过我提供的已生成的会议总结，以及会议总结修正意见，对已生成的会议总结进行调整。
        #     注意最终只返回修正后的会议总结内容，不要返回多余的内容。
        # ''',
        # 'chatroom_generate_meeting_summary_from_a_single_message_user_correct': '''
        #     已生成的会议总结：
        #     {meeting_summary}

        #     会议总结修正意见：
        #     {update_meeting}
        # ''',

        # 'chatroom_conference_orientation_system': '''
        #     你是一个数据转化助手，请通过我提供的会议总结内容以及工作导向数据进行数据导向转化。 
        #     转化时注意以下几点要求：
        #     1. 注意我提供的工作导向数据中的拆分项，一定要保持原有拆分项，不要创建新的拆分项，也不要删除拆分项
        #     2. 最终生成的工作导向数据一定要符合工作导向数据json格式要求，不要改变数据结构
        #     3. 一定要注意工作导向数据json格式说明中的字段说明和要求，还有我提供的工作导向数据补充说明，两项结合作为拆分参考规则
        #     4. 切记我提供的工作导向数据中的name，display_name，type这三个字段一定不要更改，只需要将拆分项内容填写value字段
        #     5. 一定要严格遵守工作导向数据json格式，注意最终只返回生成后的json格式内容，不要返回多余的内容。

        #     工作导向数据json格式说明：
        #     1. 结构类型说明：variables对应的数据整体为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型
        #     2. 格式、字段说明和要求：
        #     {{
        #         'variables': [
        #             {{
        #                 name: 拆分项对应的变量名，不要更改此字段，
        #                 display_name: 拆分项对应的变量显示名，可以作为拆分项的功能和用途说明，可以作为拆分项的提取依据，不要更改此字段，
        #                 type: 拆分项对应的变量类型，可为"number"或者"string"，注意拆分项内容一定要与变量类型对应，不要更改此字段，
        #                 value: 最终的工作导向拆分项内容
        #             }}
        #         ]
        #     }}
        # ''',
        # 'chatroom_conference_orientation_user': '''
        #     会议总结内容：
        #     {meeting_summary}
            
        #     工作导向数据：
        #     {{'variables':{prompt_variables}}}
            
        #     工作导向数据补充说明：
        #     {prompt_variables_supplement}
        # ''',
        # 'chatroom_conference_orientation_system_correct': '''
        #     你是一个数据转化助手，你已经通过我提供的会议总结内容进行了一次数据导向转化，我提供了已转化的工作导向数据。
        #     请通过我提供的会议总结内容，已转化的工作导向数据，以及数据修正意见，对已转化的工作导向数据进行调整。
        #     调整时注意以下几点要求：
        #     1. 注意我提供的工作导向数据中的拆分项，一定要保持原有拆分项，不要创建新的拆分项，也不要删除拆分项
        #     2. 最终生成的工作导向数据一定要符合工作导向数据json格式要求，不要改变数据结构
        #     3. 一定要注意工作导向数据json格式说明中的字段说明和要求，以此为拆分参考规则
        #     4. 切记我提供的工作导向数据中的name，display_name，type这三个字段一定不要更改，只需要将拆分项内容填写value字段
        #     5. 一定要严格遵守数据修正意见
        #     6. 一定要严格遵守工作导向数据json格式，注意最终只返回生成后的json格式内容，不要返回多余的内容。

        #     工作导向数据json格式说明：
        #     1. 结构类型说明：variables对应的数据整体为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型
        #     2. 格式、字段说明和要求：
        #     {{
        #         'variables': [
        #             {{
        #                 name: 拆分项对应的变量名，不要更改此字段，
        #                 display_name: 拆分项对应的变量显示名，可以作为拆分项的功能和用途说明，可以作为拆分项的提取依据，不要更改此字段，
        #                 type: 拆分项对应的变量类型，可为"number"或者"string"，注意拆分项内容一定要与变量类型对应，不要更改此字段，
        #                 value: 最终的工作导向拆分项内容
        #             }}
        #         ]
        #     }}
        # ''',
        # 'chatroom_conference_orientation_user_correct': '''
        #     会议总结内容：
        #     {meeting_summary}

        #     已转化的工作导向数据：
        #     {{'variables':{value_meeting_summary}}}
            
        #     数据修正意见：
        #     {update_meeting}
        # ''',

        'chatroom_request_sent_successfully': '请求成功，请等待',
        
        # 'generate_agent_system_prompt': '''
        #     你是一个AI智能体生成助手。
        #     请通过我的需求内容，按照智能体的数据结构为我生成一个完整的智能体信息。
        #     生成时注意以下几点要求：
        #     1. 智能体名称要高度拟人化
        #     2. 智能体描述要尽量详细，要覆盖智能体的所有信息
        #     3. 智能体的职能信息要尽量详细，不要仅仅局限于字面意义上的“职能”信息，也要包括其他相关的特征信息
        #     4. 智能体的能力拆分要尽量详细，每个能力的具体内容要详细描述，能力的输出结果格式要选择合适的格式
        #     5. 一定要严格遵守智能体数据json结构
        #     注意只返回智能体的json结构数据，不要返回多余的内容。
        #     智能体数据json结构说明：
        #     {{
        #         "name": "(string类型) 智能体名称",
        #         "description": "(string类型) 智能体描述",
        #         "obligations": "(string类型) 智能体的职能信息（包括但不限于智能体的身份、职责、岗位、技能等信息）",
        #         "abilities": [
        #             {{
        #                 "name": "(string类型) 能力名称",
        #                 "content": "(string类型) 能力的具体内容，智能体运行时会把选择的能力内容作为prompt提交给LLM模型",
        #                 "output_format": "(int类型)，能力的输出结果格式，1：文本形式，2：json格式，3：纯代码形式（不包含非代码类内容），智能体运行时会按照选择的能力对应的输出结果格式进行内容返回"
        #             }}
        #         ]
        #     }}
        #     {append_prompt}
        # ''',
        # 'generate_agent_user':(
        #     '需求内容：\n'
        #     '{user_prompt}\n\n'
        # ),

        # 'regenerate_agent_system': (
        #     '注意：你已经生成了一些智能体，你需要再生成一个全新的智能体，新智能体数据要尽量与已生成的智能体历史数据内容不同。\n'
        # ),
        # 'regenerate_agent_user': (
        #     '已生成的智能体历史数据：\n'
        #     '{history_agent_list}\n'
        # ),

        # 'agent_supplement_system':(
        #     '你是一个AI智能体生成助手。'
        #     '你已经生成了一个智能体，请通过我提供的修正意见，对已生成的智能体数据进行调整。\n'
        #     '注意只返回智能体的json结构数据，不要返回多余的内容。\n'
        #     '智能体数据json结构说明：\n'
        #     '{{\n'
        #     '  "name": "(string类型) 智能体名称",\n'
        #     '  "description": "(string类型) 智能体描述",\n'
        #     '  "obligations": "(string类型) 智能体的职能信息（包括但不限于智能体的身份、职责、岗位、技能等信息）",\n'
        #     '  "abilities": [\n'
        #     '    {{\n'
        #     '      "name": "(string类型) 能力名称",\n'
        #     '      "content": "(string类型) 能力的具体内容，智能体运行时会把选择的能力内容作为prompt提交给LLM模型",\n'
        #     '      "output_format": "(int类型)，能力的输出结果格式，1：文本形式，2：json格式，3：纯代码形式（不包含非代码类内容），智能体运行时会按照选择的能力对应的输出结果格式进行内容返回"\n'
        #     '    }}\n'
        #     '  ]\n'
        #     '}}\n'
        # ),
        # 'agent_supplement_user':(
        #     '修正意见：\n'
        #     '{agent_supplement}\n\n'
        #     '已生成的智能体数据：\n'
        #     '{history_agent}\n'
        # ),

        # 'agent_batch_sample_system': '''
        #     你是一个AI智能体生成助手。
        #     请通过我提供的批量生成智能体的需求，按照智能体的数据结构为我生成一个完整的样例智能体信息。
        #     生成时注意以下几点要求：
        #     1. 智能体名称要高度拟人化
        #     2. 智能体描述要尽量详细，要覆盖智能体的所有信息
        #     3. 智能体的职能信息要尽量详细，不要仅仅局限于字面意义上的“职能”信息，也要包括其他相关的特征信息
        #     4. 智能体的能力拆分要尽量详细，每个能力的具体内容要详细描述，能力的输出结果格式要选择合适的格式
        #     5. 注意只生成一个智能体样例，不要进行批量生成。
        #     6. 一定要严格遵守智能体数据json结构
        #     注意只返回智能体的json结构数据，不要返回多余的内容。
        #     智能体数据json结构说明：
        #     {{
        #         "name": "(string类型) 智能体名称",
        #         "description": "(string类型) 智能体描述",
        #         "obligations": "(string类型) 智能体的职能信息（包括但不限于智能体的身份、职责、岗位、技能等信息）",
        #         "abilities": [
        #             {{
        #                 "name": "(string类型) 能力名称",
        #                 "content": "(string类型) 能力的具体内容，智能体运行时会把选择的能力内容作为prompt提交给LLM模型",
        #                 "output_format": "(int类型)，能力的输出结果格式，1：文本形式，2：json格式，3：纯代码形式（不包含非代码类内容），智能体运行时会按照选择的能力对应的输出结果格式进行内容返回"
        #             }}
        #         ]
        #     }}
        # ''',
        # 'agent_batch_sample_user': '''
        #     批量生成智能体的需求：
        #     {agent_batch_requirements}
        # ''',
        # 'agent_batch_generate_system': '''
        #     你是一个AI智能体生成助手。
        #     请通过我提供的批量生成智能体的需求、批量生成智能体的数量、多智能体的数据结构为我生成一批完整的智能体信息。
        #     生成时注意以下几点要求：
        #     1. 智能体名称要高度拟人化
        #     2. 智能体描述要尽量详细，要覆盖智能体的所有信息
        #     3. 智能体的职能信息要尽量详细，不要仅仅局限于字面意义上的“职能”信息，也要包括其他相关的特征信息
        #     4. 智能体的能力拆分要尽量详细，每个能力的具体内容要详细描述，能力的输出结果格式要选择合适的格式
        #     5. 一定要严格按照我提供的批量生成智能体的数量去生成智能体，不要多余或少于此数量
        #     6. 批量生成的智能体数据要尽量保持差异性，不要生成重复的智能体
        #     7. 如果已批量生成的智能体历史有真实内容，新的智能体要尽量与已生成的智能体历史保持差异性
        #     8. 一定要严格遵守多智能体数据json结构
        #     注意只返回生成的多智能体json结构数据，不要返回多余的内容。
        #     多智能体数据json结构说明：
        #     {{
        #         "multi-agent": [
        #             {{
        #                 "name": "(string类型) 智能体名称",
        #                 "description": "(string类型) 智能体描述",
        #                 "obligations": "(string类型) 智能体的职能信息（包括但不限于智能体的身份、职责、岗位、技能等信息）",
        #                 "abilities": [
        #                     {{
        #                         "name": "(string类型) 能力名称",
        #                         "content": "(string类型) 能力的具体内容，智能体运行时会把选择的能力内容作为prompt提交给LLM模型",
        #                         "output_format": "(int类型)，能力的输出结果格式，1：文本形式，2：json格式，3：纯代码形式（不包含非代码类内容），智能体运行时会按照选择的能力对应的输出结果格式进行内容返回"
        #                     }}
        #                 ]
        #             }}
        #         ]
        #     }}
        # ''',
        # 'agent_batch_generate_user': '''
        #     批量生成智能体的需求：
        #     {agent_batch_requirements}
            
        #     批量生成智能体的数量：
        #     {agent_batch_number}
            
        #     已批量生成的智能体历史：
        #     {history_agents}
        # ''',
        'app_run_error': 'app运行记录不存在',
        'api_agent_generate_failed': 'agent生成记录失败',
        'api_agent_user_prompt_required': '提示词不能为空',
        'api_agent_batch_size_invalid': '批量生成数量有误',
        'agent_batch_exist_runing_rocord': '存在正在执行的记录',
        'api_agent_supplement_prompt_required': '补充提示词不能为空',
        'api_agent_save_record_error': '保存记录失败',
        'api_agent_record_error': '记录不存在',
        'generate_skill_system_prompt':'''
            你是一个AI工具生成助手，
            请通过我的需求内容，按照工具的数据结构为我生成一个完整的工具信息。
            注意只返回工具的结构数据，不要返回多余的内容。
            工具数据json结构说明：
            1.结构类型说明: 
            input_variables为输入变量，整体结构为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型，properties为变量数据，properties_name是每个变量的名称。
            output_variables为输出变量，整体结构为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型，properties为变量数据，properties_name是每个变量的名称。
            2.格式、字段说明和要求
            {{
                "name":"(string类型)工具名称",
                "description":"(string类型)工具描述",
                "input_variables":[
                    {{
                        "name":"(string类型)输入变量名称",
                        "type":"(string类型)输入变量类型['string','number']",
                        "required":"(bool类型)输入变量是否必填,True必填,False不必填",
                        "display_name":"(string类型),name的首字母大写格式"
                    }}
                ],
                "dependencies":
                {{
                    "python3":[
                        "python依赖名称，你要完全区分内部依赖和外部依赖，依赖名称要保证完全正确。"
                    ]
                }},
                "code":
                {{
                    "python3":"(string类型)python3代码部分，你只需要提供方法即可。方法需要规定返回类型。方法形参是输入变量，变量要限制类型。return内容为dict类型，内容要和输出变量一致。"
                }},
                "output_type":"(int类型),输出类型包含以下四种类型： 1:文本  2: 数据库 3: 代码 4: 文档",
                "output_variables":[
                    {{
                        "name": "(string类型)输出变量名称",
                        "type": "(string类型)输出属性类型，包含以下六种类型：'string','number','object','Array[string]','Array[number]','Array[object]'",
                        "display_name": "(string类型)，name的首字母大写格式。"
                    }}
                ]
            }}
            {append_prompt}
        ''',
        'generate_skill_user':'''
            需求内容：
            {user_prompt}
        ''',
        'correction_skill_system_prompt':'''
            你是一个AI工具生成助手。
            你已经生成了一个工具，请通过我提供的修正意见，对已生成的工具数据进行调整。
            注意只返回技能的结构数据，不要返回多余的内容。
            工具数据json结构说明：
            1.结构类型说明: input_variables为输入变量，整体结构为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型，properties为变量数据，properties_name是每个变量的名称。
            output_variables为输出变量，整体结构为list类型，list中每个元素为一个数据拆分项，数据拆分项为dict类型，properties为变量数据，properties_name是每个变量的名称。
            2.格式、字段说明和要求
            {{
                "name":"(string类型)工具名称",
                "description":"(string类型)工具描述",
                "input_variables":[
                    {{
                        "name":"(string类型)输入变量名称",
                        "type":"(string类型)输入变量类型['string','number']",
                        "required":"(bool类型)输入变量是否必填,True必填,False不必填",
                        "display_name":"(string类型),name的首字母大写格式"
                    }}
                ]},
                "dependencies":{{
                    "python3":[
                        "python依赖名称，你要完全区分内部依赖和外部依赖，依赖名称要保证完全正确。"
                    ]
                }},
                "code":{{
                    "python3":"(string类型)python3代码部分，你只需要提供方法即可。方法需要规定返回类型。方法形参是输入变量，变量要限制类型。return内容为dict类型，内容要和输出变量一致。"
                }},
                "output_type":"(int类型),输出类型包含以下四种类型： 1:文本  2: 数据库 3: 代码 4: 文档",
                "output_variables":[
                    {{
                        "name": "(string类型)输出变量名称",
                        "type": "(string类型)输出属性类型，包含以下六种类型：'string','number','object','Array[string]','Array[number]','Array[object]'",
                        "display_name": "(string类型)，name的首字母大写格式。"
                    }}
                ]
            }}
        ''',
        'correction_skill_user':'''
            修正意见：
            {correction_prompt}
            已生成的工具信息：
            {history_skill}
        ''',
        'api_skill_success': '请求成功，请等待',
        'api_skill_generate_failed': '请求失败，请稍后再试',
        'api_skill_correction_failed': '请求失败，请稍后再试',
        'api_skill_user_prompt_required': '提示词不能为空',
    }
}

# Dictionary to store all prompt keys
prompt_keys = {
    "requirement_category",
    "agent_system_prompt_with_auto_match_ability",
    "agent_system_prompt_with_abilities",
    "agent_system_prompt_with_no_ability",
    "agent_reply_requirement_with_auto_match_ability",
    "agent_reply_requirement_with_abilities",
    "agent_reply_requirement_with_no_ability",
    "agent_reply_requirement_with_task_splitting_and_auto_match_ability",
    "agent_reply_requirement_with_task_splitting_and_abilities",
    "agent_reply_requirement_with_task_splitting_and_no_ability",
    "agent_output_format_1",
    "agent_output_format_2",
    "agent_output_format_3",
    "agent_user_prompt_with_retrieved_docs",
    "llm_reply_requirement_with_task_splitting",
    "recursive_task_generation",
    "recursive_task_assign",
    "recursive_task_execute",
    "chatroom_manager_system",
    "chatroom_manager_system_with_optional_selection",
    "chatroom_manager_user_invalid_selection",
    "chatroom_manager_user",
    "chatroom_manager_user_with_optional_selection",
    "chatroom_agent_system",
    "chatroom_agent_user_with_abilities",
    "chatroom_agent_user_with_no_ability",
    "chatroom_agent_description_with_abilities",
    "chatroom_agent_description_with_no_ability",
    "chatroom_role_user",
    "chatroom_role_agent",
    "generate_agent_system_prompt",
    "generate_agent_user",
    "regenerate_agent_system",
    "regenerate_agent_user",
    "agent_supplement_system",
    "agent_supplement_user",
    "agent_batch_sample_system",
    "agent_batch_sample_user",
    "agent_batch_generate_system",
    "agent_batch_generate_user",
    "chatroom_meeting_summary_system",
    "chatroom_meeting_summary_user",
    "chatroom_meeting_summary_system_correct",
    "chatroom_meeting_summary_user_correct",
    "chatroom_generate_meeting_summary_from_a_single_message_system_correct",
    "chatroom_generate_meeting_summary_from_a_single_message_user_correct",
    "chatroom_conference_orientation_system",
    "chatroom_conference_orientation_user",
    "chatroom_conference_orientation_system_correct",
    "chatroom_conference_orientation_user_correct"
}


def get_language_content(key: str, uid: int = 0, append_ret_lang_prompt: bool = True) -> Any:
    """
    Retrieves the content for the specified key based on the current language.
    Supports nested keys separated by dots.

    :param key: The key for the desired content, with nested keys separated by dots.
    :param uid: The user ID.
    :param append_ret_lang_prompt: Whether to append the language prompt to the content.
    :return: The content string in the current language.
    """
    from api.utils.auth import get_current_language

    actual_uid = uid if uid > 0 else int(os.getenv('ACTUAL_USER_ID', 0))
    current_language = get_current_language(actual_uid)
    keys = key.split('.')

    if key in prompt_keys:
        content = language_packs.get("en", {})
        for k in keys:
            if isinstance(content, dict):
                content = content.get(k, None)
            else:
                return None
        if append_ret_lang_prompt:
            return_language_prompt = f"\n\nPlease note that the language of the returned content must be {language_names[current_language]}."
            if isinstance(content, str):
                content += return_language_prompt
            elif isinstance(content, dict):
                content = content.copy()
                if 'system' in content:
                    content['system'] += return_language_prompt
        return content

    content = language_packs.get(current_language, {})
    for k in keys:
        if isinstance(content, dict):
            content = content.get(k, None)
        else:
            return None

    if isinstance(content, dict):
        return content.copy()
    return content
