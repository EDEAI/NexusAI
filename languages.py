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
                Based on the content I input and the provided set of all categories, analyze which category my input belongs to. If you are unsure, please choose the closest matching category.
                The result should be returned in JSON format, as follows: {format}.
            """,
            "user": """
                My input content is: {requirement}.
                All categories are as follows: {categories}.
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
                Please generate detailed task data according to the requirements and task data structure I provided, and split the steps and levels of the task as detailed as possible.
                Task data json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: specific task content, subcategories: sub-task list}}.
                Note that the hierarchical structure of task data is infinitely recursive, and the structure of each element in the sub-task list is consistent with the parent structure.
                Pay attention to the uniqueness of the task id. You can use this format: parent task id-current task id. The previous parent task id is recursively superimposed according to the level, and finally splice task- in front of each task id.
                Note that task keywords should be extracted according to the task content. The keywords should cover the task content as comprehensively as possible, but do not contain irrelevant words. Keywords are separated by commas.
                Finally, they should be returned in json format according to the task data structure.
                Note that the definition of "task data" mentioned above is not necessarily a "task" in the literal sense. It may be any content that can be split into steps or levels. It should be understood according to the actual situation. Refer to the following content for understanding and definition.
            """,
            "user": "Requirement content: {requirement}",
        },
        "recursive_task_assign": {
            "system": """
                Please select the most suitable executor for the current task based on the current task content I provided, the parent task content for reference only, and all task executors. You should select according to the specific functions of each executor. If you are not sure, please select the executor with the closest function and task content.
                Task json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: task corresponding requirement content}}.
                Task executor json structure description: {{executor id: specific function of the executor}}.
                In the end, only the selected executor id must be returned, and no redundant content must be returned.
            """,
            "user": """
                Current task content: {current_task}
                Parent task content for reference only: {parent_task}
                All task executors: {executors}
            """,
        },
        "recursive_task_execute": {
            "system": """
                You are a task executor. Please implement the current task as detailed as possible according to your specific functions, the current task content I provide, the upper-level task content for reference only, the sub-task list for reference only, and the related task content for reference only.
                When implementing the current task, pay attention to two points:
                1. If the upper-level task has actual content, refer to the task scope of the upper-level task content.
                2. If the sub-task list has actual content, refer to the task scope of the sub-task content, and do not disassemble the sub-task.
                Task json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: task corresponding requirement content}}.
                In the end, only the task content you implemented must be returned, and no redundant content should be returned.
            """,
            "user": """
                Your specific duties: {obligations}
                Current task content: {current_task}
                Parent task content for reference only: {parent_task}
                Child task list for reference only: {child_tasks}
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
        'chatroom_smart_selection_status_can_only_input': 'meeting room smart selection status can only input 0 or 1',
        'chatroom_agent_id_is_required': 'agent_id is required',
        'chatroom_agent_active_is_required': 'agent active is required',
        'chatroom_agent_active_can_only_input': 'agent active can only input 0 or 1',
        'chatroom_agent_relation_does_not_exist': 'agent relation does not exist',
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
            'First, you need to analyze the current meeting topic from the user\'s latest message content. Do not copy the meeting topic from historical messages.\n'
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
            '2. You should also analyze the coherence of agent responses. If the last agent\'s response has no relevance to the current meeting topic, please end the conversation.\n\n'
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
        'tag_create_success': 'Tag create success',
        'tag_id_not_found': 'Tag ID not found',
        'tag_update_success': 'Tag update success',
        'tag_delete_success': 'Tag delete success',
        'tag_binding_create_success': 'Tag binding create success',
        'tag_binding_delete_success': 'Tag binding delete success',
        'team_id_not_found': 'Team ID not found'
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
        'tag_create_success': '标签创建成功',
        'tag_id_not_found': '标签ID不存在',
        'tag_update_success': '标签更新成功',
        'tag_delete_success': '标签删除成功',
        'tag_binding_create_success': '标签绑定创建成功',
        'tag_binding_delete_success': '标签绑定删除成功',
        'team_id_not_found': '团队ID不存在',
        'chatroom_manager_system_with_optional_selection_return': (
            '您是会议室的主持人，会议室里有一个用户和至少一个人工智能体。\n'
            '您的职责是选择下一个发言的智能体。\n'
            '我将提供以下JSON格式的会议室所有智能体的详细信息列表：'
            '[{“id”：智能体id，“name”：智能体名称，“description”：智能体职责和能力}，…]；\n'
            '以及当前的会议主题;\n'
            '此外，聊天历史记录列表采用以下JSON格式：'
            '[message, ...];\n'
            '每条消息的JSON结构如下：'
            '{“id”：智能体id（如果演讲者是用户，则id为0），“name”：演讲者姓名，“role”：演讲者角色（用户或智能体），“message”：消息内容，“topic”：会议主题}。\n\n'
            '您应该根据以下规则决定是否结束对话：\n'
            '1. 你应该鼓励所有智能体积极参与关于当前会议主题的对话；\n'
            '2. 您还应该分析智能体响应的连贯性。如果最后一个智能体的响应与当前会议主题无关，请结束对话。\n\n'
            '然后，根据以下要求进行响应：\n'
            '1. 如果您认为对话应该结束，请仅以JSON格式返回：{“id”：0，“message”：结束对话的原因}；否则，请根据以下要求选择智能体。\n'
            '2. 请仅从提供的智能体列表中选择智能体。不要选择聊天历史中存在但不在智能体列表中的智能体；\n'
            '3.请根据当前会议主题、聊天记录以及所有智能体的职责和能力选择下一个发言的智能体。如果您不确定，请选择职责和能力与当前会议主题最匹配的智能体；\n'
            '4. 请以JSON格式返回：{“id”：您选择的智能体的id}。有时智能体的名称可能看起来像ID号，但您仍然必须返回智能体的ID，而不是他们的姓名。'
        ),

        'chatroom_manager_user_return': (
            '下面是聊天记录列表：\n'
            '{messages}\n\n'
            '以下是我的响应参数：{input_var}\n\n'
            '请根据要求从智能体名单中选择下一位智能体发言。'
        ),
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
    "chatroom_role_agent"
}


def get_language_content(key: str, uid: int = 0) -> Any:
    """
    Retrieves the content for the specified key based on the current language.
    Supports nested keys separated by dots.

    :param key: The key for the desired content, with nested keys separated by dots.
    :param uid: The user ID.
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
