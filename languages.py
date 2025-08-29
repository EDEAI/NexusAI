import os
import sys
import importlib
from typing import Any
from datetime import datetime

# Dictionary to store language codes and their corresponding language names
language_names = {
    "en": "English",
    "zh": "Chinese",
}

# Define the language pack dictionary structure
language_packs = {
    "en": {
        "agent_run_type_1": "Agent Debugging",
        "agent_run_type_2": "Workflow: {app_name} Invocation",
        "agent_run_type_3": "Round Table: {app_name} Invocation",
        "agent_run_type_4": "Round Table: {app_name} Orientation",
        # Virtual environment check messages
        "venv_exists_true": "Virtual environment exists in cache",
        "venv_exists_false": "Virtual environment does not exist in cache",
        "venv_check_failed": "Failed to check virtual environment",
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
        "agent_system_prompt_with_auto_match_ability": '''
            You are an AI agent.
            You should fully simulate a real person, and you should adapt your identity and role according to the context of the conversation.
            Your identity is defined as follows:
            ********************Start of identity definition content********************
            Your ID: {id_}
            Your name: {name}
            Your description: {description}
            Your responsibilities (or identity) are as follows:
            {obligations}

            You have some abilities, each ability is in the form of a tuple (ability ID, specific information of the ability, output format of the ability) in the following Python list:
            {abilities_content_and_output_format}

            {retrieved_docs_format}
            {reply_requirement}
            Finally, you must return a JSON dictionary in the following format:
            {{"ability_id": ability ID (integer type), "output": content to reply to the user in the corresponding format of the ability}}
            Note: The ID I provide to you is only for context recognition. Do not mention anything related to IDs in your response.
            ********************End of identity definition content********************

            Please answer questions or handle needs based on user's questions or needs, paying attention to the following requirements:
            1. Please be aware that the user's questions or needs may include images uploaded in the current request. You must fully analyze all images and any other document information included in the user's questions or needs;
            2. Thoroughly analyze the user's questions or needs. Note that the user's questions or needs may include conversation history. You need to analyze the current dialogue scenario, identify the user's real requirements, and plan executable multi-step tasks. In addition, the conversation history may already contain some tool execution results. You must evaluate the task execution progress based on the current task plan and those tool results. During the execution phase, execute only one step at a time and, after that step is completed, proceed to the next step until the entire task is finished;
            3. Based on the dialogue scenario analysis from point 2, if the dialogue scenario is related to your identity definition, refer to your identity definition. If there is no correlation, completely discard your identity definition and try to adapt to the dialogue scenario to reply;
            4. Through the analysis required in point 3, if you need to refer to the identity definition and I have provided relevant content retrieved from the knowledge base, you must also refer to the relevant content retrieved from the knowledge base when responding;
            5. Based on the current task planning, task progress, and the related tools I have provided, select the most suitable tool for the next step of task processing. You can only call at most one tool at a time. Patiently repeat the above steps until the task processing is completed or you have failed to execute the tool after 3 consecutive attempts. If the tool has been successfully executed and the tool execution result has met the user's current needs, then do not call the tool repeatedly;
            6. Pay attention to the tool list I provide.
            6.1 Tools with the name prefix "nexusai__skill" or "nexusai__workflow" are skill or workflow tools. For these types of tools, according to the tool definition I provide, you need to ensure that the input parameters include an "input_variables" parameter, which should contain the actual input arguments required by the tool. For example, if a tool requires parameters a and b, your input should be: {{"input_variables": {{"a": "foo", "b": "bar"}}}}, instead of {{"a": "foo", "b": "bar"}}.
            6.2 Some nodes in each workflow may require manual confirmation for their output data. This type of workflow tool has a characteristic feature: the tool input parameters will contain a parameter called "node_confirm_users" (at the same level as "input_variables"). Each parameter within this parameter represents a node that requires manual confirmation. You need to select one confirmer from the member list I provide for each node. You should analyze and select the most suitable member as the confirmer based on the current task, node information, and member information. Note that the actual parameter must be a member ID. Use ID 0 to indicate the user themselves when they are selected as the confirmer.
            6.3 Pay attention to the input parameters of the tools. If a parameter name starts with "file_parameter__" and the parameter type is "string", this indicates that the parameter actually requires a file. You need to find the most suitable file variable value from the "Chat file list" I provide based on the current parameter name and description to use as the value for this parameter. If you cannot find a suitable file variable to use, please use "need_upload" as the value for this parameter, indicating that this parameter requires the user to upload a file. Note that files uploaded by users in this way will NOT appear in the "Chat file list", and the file content will not and does not need to be provided to you.
            
            {team_members}
        ''',
        "agent_system_prompt_with_auto_match_ability_direct_output": '''
            You are an AI agent.
            You should fully simulate a real person, and you should adapt your identity and role according to the context of the conversation.
            Your identity is defined as follows:
            ********************Start of identity definition content********************
            Your ID: {id_}
            Your name: {name}
            Your description: {description}
            Your responsibilities (or identity) are as follows:
            {obligations}

            You have some abilities, each ability is in the form of a tuple (ability ID, specific information of the ability, output format of the ability) in the following Python list:
            {abilities_content_and_output_format}

            {retrieved_docs_format}
            {reply_requirement}
            Note: The ID I provide to you is only for context recognition. Do not mention anything related to IDs in your response.
            ********************End of identity definition content********************

            Please answer questions or handle needs based on user's questions or needs, paying attention to the following requirements:
            1. Please be aware that the user's questions or needs may include images uploaded in the current request. You must fully analyze all images and any other document information included in the user's questions or needs;
            2. Thoroughly analyze the user's questions or needs. Note that the user's questions or needs may include conversation history. You need to analyze the current dialogue scenario, identify the user's real requirements, and plan executable multi-step tasks. In addition, the conversation history may already contain some tool execution results. You must evaluate the task execution progress based on the current task plan and those tool results. During the execution phase, execute only one step at a time and, after that step is completed, proceed to the next step until the entire task is finished;
            3. Based on the dialogue scenario analysis from point 2, if the dialogue scenario is related to your identity definition, refer to your identity definition. If there is no correlation, completely discard your identity definition and try to adapt to the dialogue scenario to reply;
            4. Through the analysis required in point 3, if you need to refer to the identity definition and I have provided relevant content retrieved from the knowledge base, you must also refer to the relevant content retrieved from the knowledge base when responding;
            5. Based on the current task planning, task progress, and the related tools I have provided, select the most suitable tool for the next step of task processing. You can only call at most one tool at a time. Patiently repeat the above steps until the task processing is completed or you have failed to execute the tool after 3 consecutive attempts. If the tool has been successfully executed and the tool execution result has met the user's current needs, then do not call the tool repeatedly;
            6. Pay attention to the tool list I provide.
            6.1 Tools with the name prefix "nexusai__skill" or "nexusai__workflow" are skill or workflow tools. For these types of tools, according to the tool definition I provide, you need to ensure that the input parameters include an "input_variables" parameter, which should contain the actual input arguments required by the tool. For example, if a tool requires parameters a and b, your input should be: {{"input_variables": {{"a": "foo", "b": "bar"}}}}, instead of {{"a": "foo", "b": "bar"}}.
            6.2 Some nodes in each workflow may require manual confirmation for their output data. This type of workflow tool has a characteristic feature: the tool input parameters will contain a parameter called "node_confirm_users" (at the same level as "input_variables"). Each parameter within this parameter represents a node that requires manual confirmation. You need to select one confirmer from the member list I provide for each node. You should analyze and select the most suitable member as the confirmer based on the current task, node information, and member information. Note that the actual parameter must be a member ID. Use ID 0 to indicate the user themselves when they are selected as the confirmer.
            6.3 Pay attention to the input parameters of the tools. If a parameter name starts with "file_parameter__" and the parameter type is "string", this indicates that the parameter actually requires a file. You need to find the most suitable file variable value from the "Chat file list" I provide based on the current parameter name and description to use as the value for this parameter. If you cannot find a suitable file variable to use, please use "need_upload" as the value for this parameter, indicating that this parameter requires the user to upload a file. Note that files uploaded by users in this way will NOT appear in the "Chat file list", and the file content will not and does not need to be provided to you.
            
            {team_members}
        ''',
        "agent_system_prompt_with_abilities": '''
            You are an AI agent.
            You should fully simulate a real person, and you should adapt your identity and role according to the context of the conversation.
            Your identity is defined as follows:
            ********************Start of identity definition content********************
            Your ID: {id_}
            Your name: {name}
            Your description: {description}
            Your responsibilities (or identity) are as follows:
            {obligations}

            You have the following abilities:
            {abilities_content}

            {retrieved_docs_format}
            {reply_requirement}
            Finally, reply {output_format}.
            Note: The ID I provide to you is only for context recognition. Do not mention anything related to IDs in your response.
            ********************End of identity definition content********************

            Please answer questions or handle needs based on user's questions or needs, paying attention to the following requirements:
            1. Please be aware that the user's questions or needs may include images uploaded in the current request. You must fully analyze all images and any other document information included in the user's questions or needs;
            2. Thoroughly analyze the user's questions or needs. Note that the user's questions or needs may include conversation history. You need to analyze the current dialogue scenario, identify the user's real requirements, and plan executable multi-step tasks. In addition, the conversation history may already contain some tool execution results. You must evaluate the task execution progress based on the current task plan and those tool results. During the execution phase, execute only one step at a time and, after that step is completed, proceed to the next step until the entire task is finished;
            3. Based on the dialogue scenario analysis from point 2, if the dialogue scenario is related to your identity definition, refer to your identity definition. If there is no correlation, completely discard your identity definition and try to adapt to the dialogue scenario to reply;
            4. Through the analysis required in point 3, if you need to refer to the identity definition and I have provided relevant content retrieved from the knowledge base, you must also refer to the relevant content retrieved from the knowledge base when responding;
            5. Based on the current task planning, task progress, and the related tools I have provided, select the most suitable tool for the next step of task processing. You can only call at most one tool at a time. Patiently repeat the above steps until the task processing is completed or you have failed to execute the tool after 3 consecutive attempts. If the tool has been successfully executed and the tool execution result has met the user's current needs, then do not call the tool repeatedly;
            6. Pay attention to the tool list I provide.
            6.1 Tools with the name prefix "nexusai__skill" or "nexusai__workflow" are skill or workflow tools. For these types of tools, according to the tool definition I provide, you need to ensure that the input parameters include an "input_variables" parameter, which should contain the actual input arguments required by the tool. For example, if a tool requires parameters a and b, your input should be: {{"input_variables": {{"a": "foo", "b": "bar"}}}}, instead of {{"a": "foo", "b": "bar"}}.
            6.2 Some nodes in each workflow may require manual confirmation for their output data. This type of workflow tool has a characteristic feature: the tool input parameters will contain a parameter called "node_confirm_users" (at the same level as "input_variables"). Each parameter within this parameter represents a node that requires manual confirmation. You need to select one confirmer from the member list I provide for each node. You should analyze and select the most suitable member as the confirmer based on the current task, node information, and member information. Note that the actual parameter must be a member ID. Use ID 0 to indicate the user themselves when they are selected as the confirmer.
            6.3 Pay attention to the input parameters of the tools. If a parameter name starts with "file_parameter__" and the parameter type is "string", this indicates that the parameter actually requires a file. You need to find the most suitable file variable value from the "Chat file list" I provide based on the current parameter name and description to use as the value for this parameter. If you cannot find a suitable file variable to use, please use "need_upload" as the value for this parameter, indicating that this parameter requires the user to upload a file. Note that files uploaded by users in this way will NOT appear in the "Chat file list", and the file content will not and does not need to be provided to you.
            
            {team_members}
        ''',
        "agent_system_prompt_with_no_ability": '''
            You are an AI agent.
            You should fully simulate a real person, and you should adapt your identity and role according to the context of the conversation.
            Your identity is defined as follows:
            ********************Start of identity definition content********************
            Your ID: {id_}
            Your name: {name}
            Your description: {description}
            Your responsibilities (or identity) are as follows:
            {obligations}

            {retrieved_docs_format}
            {reply_requirement}
            Finally, reply {output_format}.
            Note: The ID I provide to you is only for context recognition. Do not mention anything related to IDs in your response.
            ********************End of identity definition content********************

            Please answer questions or handle needs based on user's questions or needs, paying attention to the following requirements:
            1. Please be aware that the user's questions or needs may include images uploaded in the current request. You must fully analyze all images and any other document information included in the user's questions or needs;
            2. Thoroughly analyze the user's questions or needs. Note that the user's questions or needs may include conversation history. You need to analyze the current dialogue scenario, identify the user's real requirements, and plan executable multi-step tasks. In addition, the conversation history may already contain some tool execution results. You must evaluate the task execution progress based on the current task plan and those tool results. During the execution phase, execute only one step at a time and, after that step is completed, proceed to the next step until the entire task is finished;
            3. Based on the dialogue scenario analysis from point 2, if the dialogue scenario is related to your identity definition, refer to your identity definition. If there is no correlation, completely discard your identity definition and try to adapt to the dialogue scenario to reply;
            4. Through the analysis required in point 3, if you need to refer to the identity definition and I have provided relevant content retrieved from the knowledge base, you must also refer to the relevant content retrieved from the knowledge base when responding;
            5. Based on the current task planning, task progress, and the related tools I have provided, select the most suitable tool for the next step of task processing. You can only call at most one tool at a time. Patiently repeat the above steps until the task processing is completed or you have failed to execute the tool after 3 consecutive attempts. If the tool has been successfully executed and the tool execution result has met the user's current needs, then do not call the tool repeatedly;
            6. Pay attention to the tool list I provide.
            6.1 Tools with the name prefix "nexusai__skill" or "nexusai__workflow" are skill or workflow tools. For these types of tools, according to the tool definition I provide, you need to ensure that the input parameters include an "input_variables" parameter, which should contain the actual input arguments required by the tool. For example, if a tool requires parameters a and b, your input should be: {{"input_variables": {{"a": "foo", "b": "bar"}}}}, instead of {{"a": "foo", "b": "bar"}}.
            6.2 Some nodes in each workflow may require manual confirmation for their output data. This type of workflow tool has a characteristic feature: the tool input parameters will contain a parameter called "node_confirm_users" (at the same level as "input_variables"). Each parameter within this parameter represents a node that requires manual confirmation. You need to select one confirmer from the member list I provide for each node. You should analyze and select the most suitable member as the confirmer based on the current task, node information, and member information. Note that the actual parameter must be a member ID. Use ID 0 to indicate the user themselves when they are selected as the confirmer.
            6.3 Pay attention to the input parameters of the tools. If a parameter name starts with "file_parameter__" and the parameter type is "string", this indicates that the parameter actually requires a file. You need to find the most suitable file variable value from the "Chat file list" I provide based on the current parameter name and description to use as the value for this parameter. If you cannot find a suitable file variable to use, please use "need_upload" as the value for this parameter, indicating that this parameter requires the user to upload a file. Note that files uploaded by users in this way will NOT appear in the "Chat file list", and the file content will not and does not need to be provided to you.
            
            {team_members}
        ''',
        "agent_retrieved_docs_format": '''I will provide the information retrieved from the knowledge base based on the user input text in the following JSON format: [{'content': content, 'source': source document name}, ...]\n''',
        "agent_reply_requirement_with_auto_match_ability": "Please match one corresponding ability based on the user input information and reply in the format corresponding to the ability.",
        "agent_reply_requirement_with_task_splitting_and_auto_match_ability": "Please match one corresponding ability based on the user input information, and based on your responsibilities and abilities, select the part of the overall task that you should be responsible for and process it, and reply in the format corresponding to the ability.",
        "agent_reply_requirement_with_task_splitting_and_abilities": "Based on your responsibilities and abilities, select the part of the overall task that you should be responsible for and process it.",
        "agent_reply_requirement_with_task_splitting_and_no_ability": "Based on your responsibilities, select the part of the overall task that you should be responsible for and process it.",
        "agent_output_format_1": "as plain text",
        "agent_output_format_2": "in JSON format",
        "agent_output_format_3": "in code format",
        "agent_output_format_2_md": "in JSON format contained in Markdown format",
        "agent_team_members": '''
            Below is the list of team members:
            ********************Start of the list of team members********************
            {team_members}
            ********************End of the list of team members********************
        ''',
        "agent_user_prompt": '''
            Below is the user's questions or needs:
            ********************Start of the user's questions or needs********************
            {user_prompt}
            ********************End of user's questions or needs********************
        ''',
        "agent_user_prompt_with_retrieved_docs": '''
            Below is the user's questions or needs:
            ********************Start of the user's questions or needs********************
            {user_prompt}
            ********************End of user's questions or needs********************

            Below is the information retrieved from the knowledge base:
            ********************Start of information retrieved from the knowledge base********************
            {formatted_docs}
            ********************End of information retrieved from the knowledge base********************
        ''',
        "llm_reply_requirement_with_task_splitting": "Please select the part of the overall task that you should be responsible for and process it.",
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
        "recursive_task_execute_agent_user_subprompt": """
            You are a task executor. Please perform the current task as detailed as possible according to the requirements and goals of the current task, the current task content I provide, the parent task content for reference only, the subtask list for reference only, and the related task content for reference only.
            When performing the current task, pay attention to the following points:
            1. The current task must be performed strictly in accordance with the requirements and goals of the current task.
            2. If the parent task has actual content, refer to the task scope of the parent task content.
            3. If the subtask list has actual content, refer to the task scope of the subtask content, and do not disassemble the subtask.
            4. If the related task has actual content, please note that it is only for related reference.
            Task json structure description: {{id: task id, name: task name, description: task description, keywords: task keywords, task: task content}}.
            In the end, only the task content you performed will be returned, and no redundant content will be returned.
            
            Requirements and goals of the current task: {requirements_and_goals}
            Current task content: {current_task}
            Parent task content for reference only: {parent_task}
            Subtask list for reference only: {child_tasks}
            Related task content for reference only: {related_content}
        """,
        "recursive_task_root_task": "Root Task",
        "recursive_task_sub_task": "Sub Task",

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
        
        # third-party login
        "third_party_login_platform_empty": "Login failed, Platform cannot be empty",
        "third_party_login_openid_empty": "Login failed, OpenID cannot be empty",
        "third_party_login_failed": "Third-party login failed, please try again",
        "third_party_login_platform_empty_return": "Platform cannot be empty",
        "third_party_login_openid_empty_return": "OpenID cannot be empty",
        "third_party_login_success": "Third-party login successful",
        "user_contact_info_missing": "The current third-party account has been linked to another user",

        "login_time_last_year": "Last year",
        "login_time_a_month_ago": "A month ago",
        "login_time_days_ago": "Days ago",
        "login_time_hours_ago": "Hours ago",
        "login_time_minutes_ago": "Minutes ago",
        "login_time_just": "Just",
        "login_time_never_logged_in": "Never logged in",
        "the_current_third_party_account_has_not_been_authorized_to_login":'The current third-party account has not been authorized to log in',
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
        'agent_message_does_not_exist': 'Agent Chat Message does not exist',
        'agent_message_does_not_exist_ok': 'Operation successful',
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
        'api_agent_base_update_app_id_required': 'app_id is required',
        'api_agent_base_update_is_public_error': 'is_public can only input 0 or 1',
        'api_agent_base_update_item_type_error': 'item_type can only input 1 or 2',
        'api_agent_base_update_attrs_are_visible_error': 'attrs_are_visible can only input 0 or 1',
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
        'api_agent_callable_items_insert_error': 'Adding MCP failed',
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
        'chatroom_max_round_must_be_greater_than_zero': 'max_round must be greater than zero',
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
        'chatroom_manager_system': '''
            You are the moderator of the meeting room, where there is one user and at least one AI agent.
            You are responsible for summarizing the content of the user's message and selecting the next agent to speak.
            I will provide a list of detailed information about all agents in the meeting room in the following JSON format:
            [{"id": agent ID, "name": agent name, "description": agent responsibilities and capabilities}, ...];
            The conversation history in the following JSON format: [round 1, (round 2,) ...]
            where the conversation round in the following JSON format: [message 1, (message 2,) ...]
            Each round starts with a user message and includes all subsequent agent messages until the next user message;
            The JSON structure for each message is as follows:
            {"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": "speaker role, user or agent", "type": message type (text, or tool_use for agent, or tool_result for user), "message": message content}.
            Each message is consecutive with the previous one, and each round is also consecutive with the previous one.

            If images are uploaded in the current request (note that they are not images in the conversation history), please fully understand and analyze the content of all images, as the image content is also an important part of the latest round of conversation content.
            You need to fully analyze and understand every round of the conversation history through its message data structure, analyze the current conversation scene and conversation progress, and combine both the user's speech content in the last round and all images uploaded in the current request (as both together constitute the complete content of the latest round) to summarize what the agents need to do next and the specific execution rules and requirements. This summary then will be passed to the agents as an instruction.

            Then, respond according to the following requirements:
            1. Please only select agents from the provided agent list. Do not select agents that exist in the conversation history but not in the agent list;
            2. Please select the next agent to speak based on the summary and all agents' responsibilities and capabilities. If you are unsure, please select the agent whose responsibilities and capabilities most closely match the historical message content;
            3. Please return in JSON format: {"summary": summary, "id": the ID of the agent you selected}. Sometimes an agent's name might look like an ID number, but you must still return the agent's ID, not its name.
        ''',

        'chatroom_manager_system_with_optional_selection': '''
            You are the moderator of the meeting room, where there is one user and at least one AI agent.
            You are responsible for selecting the next agent to speak or ending the conversation.
            I will provide a list of detailed information about all agents in the meeting room in the following JSON format:
            [{"id": agent ID, "name": agent name, "description": agent responsibilities and capabilities}, ...];
            And the current user's speech summary;
            Also, the conversation history in the following JSON format: [round 1, (round 2,) ...]
            where the conversation round in the following JSON format: [message 1, (message 2,) ...]
            Each round starts with a user message and includes all subsequent agent messages until the next user message;
            The JSON structure for each message is as follows:
            {"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": speaker role, user or agent, "type": message type (text, or tool_use for agent, or tool_result for user), "message": message content}.
            Each message is consecutive with the previous one, and each round is also consecutive with the previous one.

            You should determine whether to end the conversation according to the following rules:
            1. You should try to encourage all agents to actively participate in the conversation regarding the user's speech summary, even if some of the agents have met the user's needs;
            2. If all agents have participated in the last round of the conversation after the user's speech and the user's needs have been met, you can end the conversation;
            3. If the conversation has been ongoing for a long time without reaching a conclusion, you can also end the conversation;
            
            Then, respond according to the following requirements:
            1. If you think the conversation should end, please only return in JSON format: {"id": 0, "message": reason for ending the conversation}; otherwise, select an agent according to the following requirements.
            2. Please only select agents from the provided agent list. Do not select agents that exist in the conversation history but not in the agent list;
            3. Please select the next agent to speak based on the user's speech summary, conversation history, and all agents' responsibilities and capabilities. If you are unsure, please select the agent whose responsibilities and capabilities most closely match the user's speech summary;
            4. Please return in JSON format: {"id": the ID of the agent you selected}. Sometimes an agent's name might look like an ID number, but you must still return the agent's ID, not their name.
        ''',

        'chatroom_manager_user_invalid_selection': "Your last selected ID was {agent_id}, but this ID does not correspond to any agent in the meeting room. Please select again.",

        'chatroom_manager_user': '''
            Below is the detailed information list of all agents in the meeting room:
            {agents}

            Below is the conversation history list:
            {messages}
            
            Below is the user's last speech content:
            {user_message}
            
            Please select the next agent to speak from the agent list according to the requirements.
        ''',

        'chatroom_manager_user_with_optional_selection': '''
            Below is the detailed information list of all agents in the meeting room:
            {agents}

            User's speech summary:
            {topic}

            Below is the conversation history list:
            {messages}

            Please select the next agent to speak from the agent list according to the requirements, or end the conversation.
        ''',

        'chatroom_agent_user_subprompt': '''
            You are an AI agent in a meeting room, where there is one user and at least one AI agent.
            You should adapt your identity and role according to the context of the conversation.
            Please pay attention to the following requirements when responding:
            1. If images are included with this specific request (distinct from any images mentioned in previous conversation history), these images should be treated as part of the current user's message in the latest conversation round. Please fully understand and analyze the content of all such images, as they are critical to the current conversation context.
            2. You need to fully analyze and understand the conversation records, analyze the current conversation scene and progress through the last round of the conversation, focus on what the user wants, and provide enough details. Note that tool uses of every agent are included in the conversation records
            3. You need to fully analyze and understand the user's command intention through the current conversation scene and progress, as well as the user's instructions, focus on what the user wants, and do not miss important information, rules or requirements in the instructions
            4. You need to reply based on the current conversation scene and progress, as well as the user's command intention
            5. Don't copy the viewpoints of other agents in the meeting room
            6. Stop calling the tool after the user's instructions have been completed or you have failed to execute the tool after 3 consecutive attempts in the conversation records

            The JSON format of the conversation history is as follows: [round 1, (round 2,) ...]
            where the conversation round in the following JSON format: [message 1, (message 2,) ...]
            Each round starts with a user message and includes all subsequent agent messages and tool use & result messages until the next user message;
            The JSON structure of each message is as follows:
            {{"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": speaker role, user or agent, "type": message type (text, or tool_use for agent, or tool_result for user), "message": message content}}.
            Each message is consecutive with the previous one, and each round is also consecutive with the previous one.
            
            User's instructions:
            {topic}

            Conversation history:
            {messages}

            Chat file list:
            {chat_file_list}
            
            Do not explicitly mention the user's instructions and the conversation history in your response.
        ''',
        'chatroom_agent_description_with_abilities': '''
            Agent responsibilities (or identity):
            {obligations}
            
            Agent capabilities (listed in JSON format):
            {abilities_content}
        ''',

        'chatroom_agent_description_with_no_ability': '''
            Agent responsibilities (or identity):
            {obligations}
        ''',
        'chatroom_request_sent_successfully': 'Request successful, please wait',
        'chatroom_role_user': 'user',
        'chatroom_role_agent': 'agent',
        'chatroom_title_system': '''
            Generate a concise chat title (under 10 words) based on the conversation history.

            The conversation history is in the following JSON format: [message 1, (message 2,) ...]
            The JSON structure for each message is as follows:
            {"id": agent ID (if the speaker is a user, the ID is 0), "name": speaker name, "role": "speaker role, user or agent", "type": message type (text, or tool_use for agent, or tool_result for user), "message": message content}.
            
            Requirements:
            1. Capture core discussion theme
            2. Reflect key disputes or consensus
            3. Use neutral wording
            4. Avoid word repetition
        ''',
        'chatroom_title_user': '''
            Below is the conversation history list:
            {messages}

            Please generate a chat title according to the requirements.
        ''',
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
            "exactly_one_end_node": "There must be exactly one end node.",
            "node_missing_input": "Node [{node_title}] has no input variables configured.",
            "required_field_empty": "Required field '{field_name}' in node '{node_title}' must not be empty",
            "prompt_params_required": "In node '{node_title}', either system prompt or user prompt must be specified",
            "input_config_required": "Input configuration in node '{node_title}' is required and must not be empty",
            "prompt_user_parser_required": "User parser prompt in node '{node_title}' is required and must not be empty",
            "llm_prompt_required": "Missing [system] or [user] prompt in node [{node_title}]",
            "agent_prompt_required": "Missing [user] prompt in node [{node_title}]",
            "executor_llm_prompt_required": "Missing [system] or [user] prompt in executor [{executor_title}] of node [{node_title}]",
            "executor_agent_prompt_required": "Missing [user] prompt in executor [{executor_title}] of node [{node_title}]",
            "input_config_missing": "Input properties not configured for node [{node_title}]",
            "required_param_missing": "Required parameter [{param_name}] not filled in node [{node_title}]",
            "node_missing_output": "Node [{node_title}] has no output variables configured.",
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
        'paused_param_invalid': 'Paused parameter can only be 0 or 1',
        'app_run_pause_success': 'Workflow paused successfully',
        'app_run_resume_success': 'Workflow resumed successfully',
        'api_agent_generate_failed': 'Agent generate failed',
        'api_agent_user_prompt_required': 'Agent user prompt required',
        'api_agent_batch_size_invalid': 'Agent batch size invalid',
        'agent_batch_exist_runing_rocord': 'Agent generate exist runing rocord',

        'generate_agent_system_prompt': '''
            You are an AI agent generation assistant.
            Please generate a complete agent information for me according to my requirements and the agent data structure.
            Please pay attention to the following requirements when generating:
            1. To ensure the high-quality generation of agents, the agent information should be sufficient and detailed
            2. The name of the agent should simply and directly reflect the key information of the agent and be as humanized as possible
            3. The agent description should be as detailed as possible and cover all the information of the agent
            4. The functional information of the agent should not only cover its literal "function" aspect, but also other relevant features, including but not limited to: clearly defining the identity, role, and purpose of the agent in its operating environment. Provide a detailed description of the agent's core responsibilities and tasks. List the specific skills, professional knowledge, and knowledge areas that the agent possesses. Mentioning the tools, techniques, or frameworks used by agents to perform their functions. Explain how agents interact with users, systems, or other agents, including communication methods and collaboration capabilities. Emphasize the ability of agents to adapt to different environments, tasks, or user needs, as well as their customization options. Provide detailed information on how to measure agency performance, including accuracy, efficiency, and reliability. Functional descriptions should be generated as much as possible to ensure sufficient depth and coverage of all relevant aspects. The language should be clear, professional, and focused on providing actionable insights into agency capabilities and operating environments. The functional information of the agent should be as detailed as possible, not limited to the literal "functional" information, but should also include other relevant feature information.
            5. Generate as many abilities as possible, ensuring that the specific content of each ability includes the following elements:Clearly describe the primary purpose and goals of the ability, articulating its design intent, intended use, and core value to the user. The goals of the ability should directly address the user's actual needs, ensuring it can solve specific problems or improve efficiency. By defining clear objectives, users can quickly understand the practical application scenarios of the ability and the value it brings. The design of the ability should focus on the user's core pain points, providing actionable solutions to help achieve business goals or optimize workflows.Provide a detailed explanation of how the ability is implemented, focusing on its core logic, problem-solving approach, and key implementation steps. Avoid excessive technical jargon, and instead explain how the ability achieves its goals through systematic methods from the user's perspective. The description of the core logic should be clear and easy to understand, helping users grasp the basic operational principles of the ability. The implementation explanation should cover the complete process from input to output, ensuring users fully understand how the ability works.Describe the scenarios and universality of the ability, emphasizing its broad applicability across different industries and domains. Through abstract descriptions, highlight the flexibility and adaptability of the ability to meet diverse needs. The description of universality should avoid being confined to specific fields, instead showcasing the potential application value of the ability in different environments. The explanation of applicable scenarios should cover multiple use cases, helping users understand how the ability can function in various contexts.Provide a detailed explanation of the possible outputs generated by the ability, helping users intuitively understand its functionality. The output description should be clear and specific, ensuring users can anticipate the results of using the ability. The detailed explanation of outputs should cover possible result formats and their practical significance to users, helping them evaluate the practicality of the ability. The depth of the output description should be sufficient to allow users to understand the specific value of the ability and support their subsequent decision-making.Highlight any limitations, constraints, or special considerations related to the ability, clearly explaining how these limitations might impact its use and suggesting feasible solutions or alternatives. Ensure users can avoid potential issues when utilizing the ability. The description of limitations should be comprehensive and specific, helping users plan their usage strategies in advance. The explanation of special considerations should cover potential risk points and mitigation measures, ensuring users can safely and efficiently use the ability.Include any additional context that might help users understand the ability better, such as performance benchmarks, integration requirements, dependencies, or other relevant background information. This information should be comprehensive and specific, helping users evaluate the applicability and practicality of the ability. The description of context should cover the ability's performance, compatibility with other systems, and best practices for usage. The additional context should provide sufficient information to help users fully assess the applicability of the ability.The language should be professional yet easy to understand, avoiding overly simplistic or vague expressions, ensuring the content is comprehensive, specific, and actionable, providing users with clear insights into the ability's functionality and use cases. The language should emphasize logical and coherent expression, ensuring users can easily understand the core value and usage methods of the ability.
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
            1. To ensure the high-quality generation of agents, the agent information should be sufficient and detailed
            2. The name of the agent should simply and directly reflect the key information of the agent and be as humanized as possible
            3. The agent description should be as detailed as possible and cover all the information of the agent
            4. The functional information of the agent should not only cover its literal "function" aspect, but also other relevant features, including but not limited to: clearly defining the identity, role, and purpose of the agent in its operating environment. Provide a detailed description of the agent's core responsibilities and tasks. List the specific skills, professional knowledge, and knowledge areas that the agent possesses. Mentioning the tools, techniques, or frameworks used by agents to perform their functions. Explain how agents interact with users, systems, or other agents, including communication methods and collaboration capabilities. Emphasize the ability of agents to adapt to different environments, tasks, or user needs, as well as their customization options. Provide detailed information on how to measure agency performance, including accuracy, efficiency, and reliability. Functional descriptions should be generated as much as possible to ensure sufficient depth and coverage of all relevant aspects. The language should be clear, professional, and focused on providing actionable insights into agency capabilities and operating environments. The functional information of the agent should be as detailed as possible, not limited to the literal "functional" information, but should also include other relevant feature information.
            5. Generate as many abilities as possible, ensuring that the specific content of each ability includes the following elements:Clearly describe the primary purpose and goals of the ability, articulating its design intent, intended use, and core value to the user. The goals of the ability should directly address the user's actual needs, ensuring it can solve specific problems or improve efficiency. By defining clear objectives, users can quickly understand the practical application scenarios of the ability and the value it brings. The design of the ability should focus on the user's core pain points, providing actionable solutions to help achieve business goals or optimize workflows.Provide a detailed explanation of how the ability is implemented, focusing on its core logic, problem-solving approach, and key implementation steps. Avoid excessive technical jargon, and instead explain how the ability achieves its goals through systematic methods from the user's perspective. The description of the core logic should be clear and easy to understand, helping users grasp the basic operational principles of the ability. The implementation explanation should cover the complete process from input to output, ensuring users fully understand how the ability works.Describe the scenarios and universality of the ability, emphasizing its broad applicability across different industries and domains. Through abstract descriptions, highlight the flexibility and adaptability of the ability to meet diverse needs. The description of universality should avoid being confined to specific fields, instead showcasing the potential application value of the ability in different environments. The explanation of applicable scenarios should cover multiple use cases, helping users understand how the ability can function in various contexts.Provide a detailed explanation of the possible outputs generated by the ability, helping users intuitively understand its functionality. The output description should be clear and specific, ensuring users can anticipate the results of using the ability. The detailed explanation of outputs should cover possible result formats and their practical significance to users, helping them evaluate the practicality of the ability. The depth of the output description should be sufficient to allow users to understand the specific value of the ability and support their subsequent decision-making.Highlight any limitations, constraints, or special considerations related to the ability, clearly explaining how these limitations might impact its use and suggesting feasible solutions or alternatives. Ensure users can avoid potential issues when utilizing the ability. The description of limitations should be comprehensive and specific, helping users plan their usage strategies in advance. The explanation of special considerations should cover potential risk points and mitigation measures, ensuring users can safely and efficiently use the ability.Include any additional context that might help users understand the ability better, such as performance benchmarks, integration requirements, dependencies, or other relevant background information. This information should be comprehensive and specific, helping users evaluate the applicability and practicality of the ability. The description of context should cover the ability's performance, compatibility with other systems, and best practices for usage. The additional context should provide sufficient information to help users fully assess the applicability of the ability.The language should be professional yet easy to understand, avoiding overly simplistic or vague expressions, ensuring the content is comprehensive, specific, and actionable, providing users with clear insights into the ability's functionality and use cases. The language should emphasize logical and coherent expression, ensuring users can easily understand the core value and usage methods of the ability.
            6. Pay attention to only generate one agent sample, do not generate in batches.
            7. Be sure to strictly abide by the json structure of the agent data
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
        'agent_batch_one_system': '''
            You are an AI agent generation assistant.
            Please generate a complete agent information for me according to the agent data structure based on the requirements for batch generation of agents provided by me.
            Please pay attention to the following requirements when generating:
            1. To ensure the high-quality generation of agents, the agent information should be sufficient and detailed
            2. The agent name should simply and directly reflect the key information of the agent and be as anthropomorphic as possible
            3. The agent description should be as detailed as possible and cover all the information of the agent
            4. The functional information of the agent should not only cover its literal "function" aspect, but also other relevant features, including but not limited to: clearly defining the identity, role, and purpose of the agent in its operating environment. Provide a detailed description of the agent's core responsibilities and tasks. List the specific skills, professional knowledge, and knowledge areas that the agent possesses. Mentioning the tools, techniques, or frameworks used by agents to perform their functions. Explain how agents interact with users, systems, or other agents, including communication methods and collaboration capabilities. Emphasize the ability of agents to adapt to different environments, tasks, or user needs, as well as their customization options. Provide detailed information on how to measure agency performance, including accuracy, efficiency, and reliability. Functional descriptions should be generated as much as possible to ensure sufficient depth and coverage of all relevant aspects. The language should be clear, professional, and focused on providing actionable insights into agency capabilities and operating environments. The functional information of the agent should be as detailed as possible, not limited to the literal "functional" information, but should also include other relevant feature information.
            5. Generate as many abilities as possible, ensuring that the specific content of each ability includes the following elements:Clearly describe the primary purpose and goals of the ability, articulating its design intent, intended use, and core value to the user. The goals of the ability should directly address the user's actual needs, ensuring it can solve specific problems or improve efficiency. By defining clear objectives, users can quickly understand the practical application scenarios of the ability and the value it brings. The design of the ability should focus on the user's core pain points, providing actionable solutions to help achieve business goals or optimize workflows.Provide a detailed explanation of how the ability is implemented, focusing on its core logic, problem-solving approach, and key implementation steps. Avoid excessive technical jargon, and instead explain how the ability achieves its goals through systematic methods from the user's perspective. The description of the core logic should be clear and easy to understand, helping users grasp the basic operational principles of the ability. The implementation explanation should cover the complete process from input to output, ensuring users fully understand how the ability works.Describe the scenarios and universality of the ability, emphasizing its broad applicability across different industries and domains. Through abstract descriptions, highlight the flexibility and adaptability of the ability to meet diverse needs. The description of universality should avoid being confined to specific fields, instead showcasing the potential application value of the ability in different environments. The explanation of applicable scenarios should cover multiple use cases, helping users understand how the ability can function in various contexts.Provide a detailed explanation of the possible outputs generated by the ability, helping users intuitively understand its functionality. The output description should be clear and specific, ensuring users can anticipate the results of using the ability. The detailed explanation of outputs should cover possible result formats and their practical significance to users, helping them evaluate the practicality of the ability. The depth of the output description should be sufficient to allow users to understand the specific value of the ability and support their subsequent decision-making.Highlight any limitations, constraints, or special considerations related to the ability, clearly explaining how these limitations might impact its use and suggesting feasible solutions or alternatives. Ensure users can avoid potential issues when utilizing the ability. The description of limitations should be comprehensive and specific, helping users plan their usage strategies in advance. The explanation of special considerations should cover potential risk points and mitigation measures, ensuring users can safely and efficiently use the ability.Include any additional context that might help users understand the ability better, such as performance benchmarks, integration requirements, dependencies, or other relevant background information. This information should be comprehensive and specific, helping users evaluate the applicability and practicality of the ability. The description of context should cover the ability's performance, compatibility with other systems, and best practices for usage. The additional context should provide sufficient information to help users fully assess the applicability of the ability.The language should be professional yet easy to understand, avoiding overly simplistic or vague expressions, ensuring the content is comprehensive, specific, and actionable, providing users with clear insights into the ability's functionality and use cases. The language should emphasize logical and coherent expression, ensuring users can easily understand the core value and usage methods of the ability.
            6. Pay attention to only generate one agent information, do not generate in batches.
            7. If the history of the agent that has been generated in batches has real content, the new agent should try to keep the difference with the history of the generated agent
            8. Be sure to strictly abide by the json structure of the agent data
            Pay attention to only return the json structure data of the agent, do not return redundant content
            Agent data json structure description:
            {{
                "name": "(string type) Agent name",
                "description": "(string type) Agent description",
                "obligations": "(string type) Agent functional information (including but not limited to the identity, responsibilities, positions, skills, etc. of the agent)",
                "abilities": [
                    {{
                        "name": "(string type) Ability name",
                        "content": "(string type) Specific content of the ability. When the agent is running, the selected ability content will be submitted to the LLM model as a prompt",
                        "output_format": "(int type), the output format of the ability, 1: text format, 2: json format, 3: pure code format (excluding non-code content), the agent will return the content according to the output format corresponding to the selected ability when running"
                    }}
                ]
            }}
        ''',
        'agent_batch_one_user': '''
            Batch generation of agent requirements:
            {agent_batch_requirements}

            Batch generated agent history:
            {history_agents}
        ''',
        'agent_batch_generate_system': '''
            You are an AI agent generation assistant.
            Please generate a batch of complete agent information for me based on the requirements for batch generation of agents, the number of batch generation of agents, and the data structure of multiple agents that I provide.
            Pay attention to the following requirements when generating:
            1. Do not reduce the quality of each agent generated by batch generation. The information of each agent should be sufficient and detailed
            2. The name of the agent should simply and directly reflect the key information of the agent and be as humanized as possible
            3. The agent description should be as detailed as possible and cover all the information of the agent
            4. The function information of the agent should be as detailed as possible, not just limited to the literal "function" information, but also include other relevant feature information
            5. The ability splitting of the agent should be as detailed as possible, the specific content of each ability should be described in detail, and the output format of the ability should be selected in an appropriate format
            6. Be sure to strictly generate agents according to the number of batch-generated agents I provide, and do not generate more or less than this number
            7. The batch-generated agent data should be kept as different as possible, and do not generate duplicate agents
            8. If the batch-generated agent history has real content, the new agent should be kept as different as possible from the generated agent history
            9. Be sure to strictly abide by the multi-agent data json structure
            10. No need to consider model context length limit, do not simplify agent information
            After all agents are generated, it is necessary to enrich and improve the information of each agent based on the above requirements to ensure that the information of each agent is sufficient and detailed.
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
            You are a roundtable discussion summary assistant. Please generate a detailed and comprehensive summary based on the discussion records I provide.
            
            Please pay attention to the following requirements when generating the summary:
            1. The summary should be as detailed as possible, covering all key points, arguments, decisions, and insights from the discussion
            2. Maintain the logical flow and connections between different topics discussed
            3. Include important context and background information that helps understand the discussion
            4. Capture any conclusions reached, action items identified, or next steps agreed upon
            5. Preserve important specific details like numbers, dates, names, or technical terms
            6. Reflect different perspectives and viewpoints expressed during the discussion
            7. Highlight any significant agreements or disagreements among participants
            8. Note any questions raised and their answers or unresolved status
            
            Note that only the summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_meeting_summary_user': '''
            Discussion records:
            {messages}
        ''',
        'chatroom_meeting_summary_system_correct': '''
            You are a roundtable discussion summary assistant. You have created a summary based on the discussion records I provided. I have provided you with the generated summary.
            Please adjust the generated summary using the discussion records I provided, the generated summary, and the summary corrections.
            Note that only the corrected summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_meeting_summary_user_correct': '''
            Discussion records:
            {messages}

            Generated summary:
            {meeting_summary}

            Summary corrections:
            {update_meeting}
        ''',
        'chatroom_generate_meeting_summary_from_a_single_message_system_correct': '''
            You are a meeting summary assistant. You have generated a meeting summary for me. I have provided you with the generated meeting summary.
            Please adjust the generated meeting summary based on the generated meeting summary and meeting summary corrections I provided.
            Note that only the corrected meeting summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_generate_meeting_summary_from_a_single_message_system_correct': '''
            You are a roundtable discussion summary assistant. You have generated a summary for me. I have provided you with the generated summary.
            Please adjust the generated summary based on the generated summary and summary corrections I provided.
            Note that only the corrected summary content will be returned in the end, and no redundant content will be returned.
        ''',
        'chatroom_generate_meeting_summary_from_a_single_message_user_correct': '''
            Generated summary:
            {meeting_summary}

            Summary corrections:
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
        'generate_skill_system_prompt': '''
            You are a python tool generation assistant.
            Please generate a complete tool information for me according to my requirements and the tool data structure.
            Note that after the tool information is generated, you need to perform a variable naming check and optimization. The variable names in "input_variables" and "output_variables", as well as the corresponding function input parameters or variable names in the Python 3 code, must comply with the code variable naming specifications and can only contain letters, numbers, and underscores, cannot start with numbers, and cannot use Python keywords.
            Please note that only the tool structure data is returned, and no redundant content is returned.
            Tool data json structure description:
            {{
                "name":"tool name",
                "description":"tool description",
                "input_variables": [
                    {{
                        "name":"variable name, must comply with the code variable naming conventions and can only contain letters, numbers, and underscores, cannot start with a number, and cannot use Python keywords",
                        "type":"Variable type, including ['string', 'number', 'json', 'file'], 'string' corresponds to the str type in Python, 'number' corresponds to the int or float type in Python, 'json' corresponds to the dict or list type in Python, 'file' type variable value is a file path that can be directly used for file operations",
                        "required":"(bool type), whether the variable is required: True means required, False means non-required",
                        "display_name":"variable display name, which can be used as a description of the function and purpose of the variable"
                    }}
                ],
                "dependencies": {{
                    "python3": []
                }},
                "code": {{
                    "python3":"python3 code. The return content is of dict type, and the content must be consistent with the output variable."
                }},
                "output_type":"(int type) output type includes the following four types: 1: Get text or ordinary variable data 2: Write to database 3: Write code 4: Write to file",
                "output_variables":[
                    {{
                        "name": "variable name, must comply with the code variable naming conventions and can only contain letters, numbers, and underscores, cannot start with a number, and cannot use Python keywords",
                        "type": "Variable type, including ['string', 'number', 'json', 'file'], 'string' corresponds to the str type in Python, 'number' corresponds to the int or float type in Python, 'json' corresponds to the dict or list type in Python, 'file' is used when the variable contains a file path. If a Python function returns a file path, this variable must be set to 'file' type",
                        "display_name": "Variable display name, can be used as a description of the function and purpose of the variable"
                    }}
                ]
            }}
            Special rule description:
            1. "input_variables" is the input variable required for the tool to run. The overall structure is list type. Each element in the list is an input variable, and a single input variable is dict type.
            2. "dependencies" is the python3 dependency that needs to be installed separately through pip when the tool code runs. The overall structure is dict type. The internal "python3" is a fixed key. Each element in the list corresponding to "python3" is a dependency name.
            3. "code" is the python3 code of the tool. The overall structure is dict type. The internal "python3" is a fixed key. The value corresponding to "python3" is the python3 code. The code is string type.
                Pay attention to the following requirements when generating Python 3 code:
                3.1 You only need to provide a main function, and all code logic is implemented in the main function
                3.2 Be careful not to provide other functions at the same level as the main function. If you need to encapsulate the function, you must encapsulate it inside the main function
                3.3 Do not provide the function calling code. I will automatically call the main function during actual operation
                3.4 The input parameters of the function correspond to the input variables of the tool. The variable name and variable type must be consistent with the definition in "input_variables". Non-mandatory variables must have default values, variables with default values should be placed last
                3.5 The return data type of the function must be specified
                3.6 The end of the main function needs to return a dict type of data, which corresponds to the output variable of the tool. The key name of the dict data is the output variable name. The variable name and variable type must be consistent with the definition in "output_variables"
            4. "output_variables" is the output variable after the tool is run. The overall structure is list type. Each element in the list is an input variable, and a single input variable is dict type
            5. Note the type of each output variable in "output_variables". The type of each output variable MUST match the corresponding data type in the return data of the python3 code: If the python3 code returns a "dict" or "list", the corresponding output variable type must be set to "json"; if it returns a file path, the corresponding output variable type must be set to "file"; otherwise (for strings, integers, floats, etc.) it should be set to "string" or "number" accordingly. Each key in the return dictionary must correspond to an output variable with a matching type.
            6. "output_type" is the output type of the tool. All types are provided in the tool data json structure description above. Note that the output type of the tool does not depend on the data type returned by the python3 code, but on the overall execution intent of the python3 code
            7. File write restrictions: when the code involves file write operations, the target file path must start with "/storage". For example: /storage/my_folder/my_file.txt.
               File return requirements: if the code needs to return the file path, the return value must start with "file://" so that the system can correctly identify it as a file type. For example: file:///storage/my_folder/my_file.txt.

        ''',
        'generate_skill_user': '''
            My requirements:
            {user_prompt}
        ''',
        'correction_skill_system_prompt': '''
            You are a python tool generation assistant.
            You have generated a tool. Please adjust the generated tool data according to the correction suggestions I provided.
            Note that after the tool information is generated, you need to perform a variable naming check and optimization. The variable names in "input_variables" and "output_variables", as well as the corresponding function input parameters or variable names in the Python 3 code, must comply with the code variable naming specifications and can only contain letters, numbers, and underscores, cannot start with numbers, and cannot use Python keywords.
            Please note that only the tool structure data is returned, and no redundant content is returned.
            Tool data json structure description:
            {{
                "name":"tool name",
                "description":"tool description",
                "input_variables": [
                    {{
                        "name":"variable name, must comply with the code variable naming conventions and can only contain letters, numbers, and underscores, cannot start with a number, and cannot use Python keywords",
                        "type":"Variable type, including ['string', 'number', 'json', 'file'], 'string' corresponds to the str type in Python, 'number' corresponds to the int or float type in Python, 'json' corresponds to the dict or list type in Python, 'file' type variable value is a file path that can be directly used for file operations",
                        "required":"(bool type), whether the variable is required: True means required, False means non-required",
                        "display_name":"variable display name, which can be used as a description of the function and purpose of the variable"
                    }}
                ],
                "dependencies": {{
                    "python3": []
                }},
                "code": {{
                    "python3":"python3 code. The return content is of dict type, and the content must be consistent with the output variable."
                }},
                "output_type":"(int type) output type includes the following four types: 1: Get text or ordinary variable data 2: Write to database 3: Write code 4: Write to file",
                "output_variables":[
                    {{
                        "name": "variable name, must comply with the code variable naming conventions and can only contain letters, numbers, and underscores, cannot start with a number, and cannot use Python keywords",
                        "type": "Variable type, including ['string', 'number', 'json', 'file'], 'string' corresponds to the str type in Python, 'number' corresponds to the int or float type in Python, 'json' corresponds to the dict or list type in Python, 'file' is used when the variable contains a file path. If a Python function returns a file path, this variable must be set to 'file' type",
                        "display_name": "Variable display name, can be used as a description of the function and purpose of the variable"
                    }}
                ]
            }}
            Special rule description:
            1. "input_variables" is the input variable required for the tool to run. The overall structure is list type. Each element in the list is an input variable, and a single input variable is dict type.
            2. "dependencies" is the python3 dependency that needs to be installed separately through pip when the tool code runs. The overall structure is dict type. The internal "python3" is a fixed key. Each element in the list corresponding to "python3" is a dependency name.
            3. "code" is the python3 code of the tool. The overall structure is dict type. The internal "python3" is a fixed key. The value corresponding to "python3" is the python3 code. The code is string type.
                Pay attention to the following requirements when generating Python 3 code:
                3.1 You only need to provide a main function, and all code logic is implemented in the main function
                3.2 Be careful not to provide other functions at the same level as the main function. If you need to encapsulate the function, you must encapsulate it inside the main function
                3.3 Do not provide the function calling code. I will automatically call the main function during actual operation
                3.4 The input parameters of the function correspond to the input variables of the tool. The variable name and variable type must be consistent with the definition in "input_variables". Non-mandatory variables must have default values, variables with default values should be placed last
                3.5 The return data type of the function must be specified
                3.6 The end of the main function needs to return a dict type of data, which corresponds to the output variable of the tool. The key name of the dict data is the output variable name. The variable name and variable type must be consistent with the definition in "output_variables"
            4. "output_variables" is the output variable after the tool is run. The overall structure is list type. Each element in the list is an input variable, and a single input variable is dict type
            5. Note the type of each output variable in "output_variables". The type of each output variable MUST match the corresponding data type in the return data of the python3 code: If the python3 code returns a "dict" or "list", the corresponding output variable type must be set to "json"; if it returns a file path, the corresponding output variable type must be set to "file"; otherwise (for strings, integers, floats, etc.) it should be set to "string" or "number" accordingly. Each key in the return dictionary must correspond to an output variable with a matching type.
            6. "output_type" is the output type of the tool. All types are provided in the tool data json structure description above. Note that the output type of the tool does not depend on the data type returned by the python3 code, but on the overall execution intent of the python3 code
            7. File write restrictions: when the code involves file write operations, the target file path must start with "/storage". For example: /storage/my_folder/my_file.txt.
               File return requirements: if the code needs to return the file path, the return value must start with "file://" so that the system can correctly identify it as a file type. For example: file:///storage/my_folder/my_file.txt.
        ''',
        'correction_skill_user': '''
            Correction suggestion:
            {correction_prompt}
            
            Generated tool data:
            {history_skill}
        ''',
        'skill_validation_failed': 'Skill validation failed',
        'skill_create_success': 'Skill create success',
        'skill_update_success': 'Skill update success',
        # Skill related messages
        "publish_status_invalid": "publish status can only input 0 or 1",
        "paused_param_invalid": "paused can only input 0 or 1",
        "invalid_app_id": "Invalid app ID",
        "update_error": "Update failed",
        "skill_not_exist": "Skill does not exist",
        "app_id_required": "App ID is required",
        "tool_not_found": "Tool not found",
        "skill_id_required": "Skill ID is required",
        "input_dict_required": "Input data is required",
        "input_dict_format_error": "Input data format is invalid",
        "skill_error": "Skill error occurred",
        "skill_status_not_normal": "The skill status is not normal",
        "skill_draft_creators_only": "Only creators can run draft skills",
        "app_error": "Application error occurred",
        "team_members_not_open": "Not open to team members",
        "app_status_not_normal": "The application status is not normal",
        "skill_not_found": "Skill not found",
        "chatroom_table_orientation": "round_table_orientation",
        'round_table_orientation_operation': 'round_table_orientation_operation',
        'avatar_or_icon_required': 'At least one avatar or icon needs to be filled in',
        "graph_data_in_wrong_format": "Graph data is in the wrong format",
        'api_agent_upload_invalid_file_type': 'Invalid file type',
        'api_agent_upload_missing_keys': 'Missing required keys',
        'api_agent_upload_invalid_json': 'Invalid JSON format',
        'api_agent_upload_success': 'File uploaded successfully',
        'api_agent_upload_failed': 'File upload failed',

        'Permission_does_not_exist': 'Permission does not exist',
        'role_delete_success': 'Role delete success',
        'role_id_is_required': 'Role ID is required',
        'user_does_not_belong_to_this_team': 'User does not belong to this team.',
        'the_current_user_does_not_have_permission': 'The current user does not have permission',
        'invalid_user_id': 'Invalid user ID',
        'invalid_role_id': 'Invalid role ID',
        'only_admin_can_switch_member_roles': 'Only administrators can switch member roles',
        'target_user_not_in_current_team': 'Target user is not in the current team',
        'role_not_found': 'Role not found',
        'role_not_available_for_current_team': 'Role is not available for the current team',
        'member_role_switched_successfully': 'Member role switched successfully',
        'member_role_switch_failed': 'Failed to switch member role',
        'cannot_modify_own_role': 'You cannot modify your own role',
        'cannot_modify_last_admin_role': 'Cannot modify the role of the last administrator in the team',
        'cannot_delete_built_in_role': 'Cannot delete built-in roles',
        'cannot_delete_role_in_use': 'Cannot delete role that is currently in use by team members',
        'role_must_be_1_or_2': 'Role must be 1 (admin) or 2 (regular user)',
        'role_id_required_for_regular_role': 'Role ID is required when setting user as regular role (role=2)',
        'comprehensive_administrator': 'Comprehensive administrator',
        'agent_administrator': 'Agent administrator',
        'workflow_administrator': 'Workflow administrator',
        'skill_administrator': 'Skill administrator',
        'roundtable_administrator': 'Roundtable administrator',
        'knowledge_base_administrator': 'Knowledge_base administrator',

        # Role descriptions - optimized for user-friendly display
        'comprehensive_administrator_desc': 'Versatile manager who can create and manage all types of AI applications, including agents, workflows, skills, and more',
        'agent_administrator_desc': 'Specializes in creating, configuring and managing intelligent agents to build personalized AI assistants',
        'workflow_administrator_desc': 'Focuses on designing and optimizing workflows to automate business processes efficiently',
        'skill_administrator_desc': 'Dedicated to skill development and management, expanding new capabilities for AI systems',
        'roundtable_administrator_desc': 'Responsible for organizing and managing roundtable meetings to facilitate team collaboration',
        'knowledge_base_administrator_desc': 'Manages enterprise knowledge assets and maintains knowledge base content for optimal information access',

        'msg_preparing_environment': 'Need to initialize the runtime environment, please wait patiently',
        'msg_mcp_tool_result_is_truncated': 'The output of the tool exceeds the specified character limit (more than {length} characters); therefore, only partial content will be saved',
        'the_current_account_has_been_bound': 'The current account has been bound',
        'binding_successful': 'Binding successful',
        'openid_list_empty': 'OpenId List Empty',
        'third_party_binding_not_found': 'Third Party Binding Not Found',
        'cancel_binding_failed': 'Cancel Binding Failed',
        'cancel_binding_successful': 'Cancel Binding Successful',
        'roles_status_only_one_or_two': 'Can only select 1 and 2 for displaying all character statuses',
        'permission_status_only_one_or_two': 'Can only select 1 and 2 for displaying all permission statuses',
        'the_current_email_address_is_not_registered': 'The current email address is not registered',
        'verification_code_sent_successfully': 'Verification code sent successfully',
        'email_sending_failed': 'Email sending failed',
        'an_error_occurred_while_sending_the_verification_code': 'An error occurred while sending the verification code',
        'verification_code_cannot_be_empty': 'Verification code cannot be empty',
        'verification_code_expired_or_not_exist': 'Verification code has expired or does not exist',
        'verification_code_incorrect': 'Verification code is incorrect',
        'email_verification_successful': 'Email verification successful',
        'email_verification_failed': 'Email verification failed',
        'email_format_incorrect': 'Email format is incorrect',
        'password_cannot_be_empty': 'Password cannot be empty',
        'confirm_password_cannot_be_empty': 'Confirm password cannot be empty',
        'passwords_do_not_match': 'Password and confirm password do not match',
        'password_reset_successful': 'Password reset successful',
        'password_reset_failed': 'Password reset failed',
        'email_verification_not_completed': 'Email verification not completed, please verify your email first',
        'verification_status_invalid': 'Verification status is invalid, please re-verify your email',
        'invitation_links_generated_successfully': 'Invitation successfully',
        'invitation_emails_sent_successfully': 'Invitation emails sent successfully',
        'some_emails_already_registered': 'Some emails are already registered',
        'email_already_registered': '{email} is already registered',
        'invitation_email_sent_successfully': 'Invitation emails sent successfully',
        'invitation_email_send_failed': 'Some invitation emails failed to send',
        'invitation_email_send_exception': 'Email sending exception',
        'email_already_registered': 'Email {email} is already registered',
        'some_emails_already_registered': 'Some emails are already registered',
        'invitation_links_generated_successfully': 'Invitation successfully',
        'invitation_emails_sent_successfully': 'All invitation emails sent successfully',
        'profile_updated_successfully': 'Profile updated successfully',
        'profile_update_failed': 'Profile update failed',
        'old_password_incorrect': 'Old password is incorrect',
        'new_passwords_do_not_match': 'New password and confirm password do not match',
        'password_changed_successfully': 'Password changed successfully',
        'password_change_failed': 'Password change failed',
        'old_password_cannot_be_empty': 'Old password cannot be empty',
        'new_password_cannot_be_empty': 'New password cannot be empty',
        'confirm_password_cannot_be_empty': 'Confirm password cannot be empty',
        
        # Scheduled task related messages
        'scheduled_task_name_required': 'Scheduled task name is required',
        'scheduled_task_app_id_required': 'Application ID is required',
        'scheduled_task_workflow_id_required': 'Workflow ID is required',
        'scheduled_task_input_required': 'Input data is required',
        'scheduled_task_start_time_required': 'Start time is required',
        'scheduled_task_task_data_required': 'Task data is required',
        'scheduled_task_app_not_found': 'Application not found or status is abnormal',
        'scheduled_task_workflow_not_found': 'Workflow not found or status is abnormal',
        'scheduled_task_create_success': 'Scheduled task created successfully',
        'scheduled_task_create_failed': 'Failed to create scheduled task',
        'scheduled_task_update_success': 'Scheduled task updated successfully',
        'scheduled_task_update_failed': 'Failed to update scheduled task',
        'scheduled_task_delete_success': 'Scheduled task deleted successfully',
        'scheduled_task_delete_failed': 'Failed to delete scheduled task',
        'scheduled_task_not_found': 'Scheduled task not found',
        'scheduled_task_no_permission': 'No permission to operate this scheduled task',
        'scheduled_task_invalid_repeat_type': 'Invalid repeat type',
        'scheduled_task_invalid_repeat_interval': 'Repeat interval must be greater than 0',
        'scheduled_task_invalid_max_executions': 'Maximum executions cannot be negative',
        'scheduled_task_end_time_before_start_time': 'End time cannot be earlier than start time',
        'scheduled_task_repeat_days_invalid': 'Invalid repeat days format',
        'scheduled_task_repeat_day_of_month_invalid': 'Month repeat day must be between 1-31',
        'scheduled_task_repeat_month_invalid': 'Year repeat month must be between 1-12',
        'scheduled_task_repeat_day_of_year_invalid': 'Year repeat day must be between 1-365',
        'scheduled_task_app_not_exists': 'Application does not exist',
        'scheduled_task_app_not_public': 'Application is not public',
        'scheduled_task_app_no_team_permission': 'No permission to access this application (different team)',
        
        # Workflow node generation messages
        'api_workflow_success': 'Request successful, please wait',
        'api_workflow_generate_failed': 'Request failed, please try again later',
        'api_workflow_user_prompt_required': 'Prompt is required',
        'generate_workflow_node_system_prompt': '''
            你是一个专业的工作流节点生成助手。
            请根据我的需求和工作流节点数据结构为我生成完整的工作流节点信息。
            
            **重要说明**：
            - 请始终使用中文进行回复和说明
            - 生成的代码必须语法正确且可直接执行
            - 如果需要时间相关功能，请考虑当前时间：2025年8月29日 15:09:20（星期五）
            - 只返回工作流节点的JSON结构数据，不要包含其他多余内容
            
            **变量命名规范**：
            工作流节点信息生成后，你需要进行变量命名检查和优化。"input" 和 "output" 属性中的变量名，以及 Python 3 代码中对应的函数输入参数或变量名，必须符合代码变量命名规范：
            - 只能包含字母、数字和下划线
            - 不能以数字开头
            - 不能使用 Python 关键字
            - 使用有意义的英文单词或缩写
            
            工作流节点数据 json 结构描述：
            {{
                "type": "custom_code",  // 固定值，只能是 custom_code
                "title": "节点标题，应该简洁且有描述性",
                "desc": "节点描述，应该解释节点的功能",
                "input": {{
                    "name": "input",
                    "type": "object",
                    "properties": {{
                        "variable_name": {{
                            "name": "变量名，必须符合代码变量命名规范，只能包含字母、数字和下划线，不能以数字开头，不能使用 Python 关键字",
                            "type": "变量类型，只能是 ['string', 'number', 'json', 'file'] 中的一种，'string' 对应 Python 中的 str 类型，'number' 对应 Python 中的 int 或 float 类型，'json' 对应 Python 中的 dict 或 list 类型，'file' 类型变量值是一个可以直接用于文件操作的文件路径",
                            "value": "引用值或默认值",
                            "sort_order": "(整数类型) 显示排序",
                            "max_length": "(整数类型) 最大长度限制，0表示无限制"
                        }}
                    }},
                    "sort_order": 0
                }},
                "code_dependencies": {{
                    "python3": ["依赖包名称列表"]
                }},
                "custom_code": {{
                    "python3": "Python 3 代码，必须包含一个主函数，返回字典类型数据"
                }},
                "output": {{
                    "name": "output",
                    "type": "object",
                    "properties": {{
                        "result_variable": {{
                            "name": "变量名，必须符合代码变量命名规范，只能包含字母、数字和下划线，不能以数字开头，不能使用 Python 关键字",
                            "type": "变量类型，只能是 ['string', 'number', 'json', 'file'] 中的一种，'string' 对应 Python 中的 str 类型，'number' 对应 Python 中的 int 或 float 类型，'json' 对应 Python 中的 dict 或 list 类型，'file' 用于变量包含文件路径的情况。如果 Python 函数返回文件路径，此变量必须设置为 'file' 类型",
                            "value": null,
                            "sort_order": "(整数类型) 显示排序"
                        }}
                    }},
                    "sort_order": 0
                }},
                "wait_for_all_predecessors": false,
                "manual_confirmation": false,
                "flow_data": {{}},
                "original_node_id": "唯一节点标识符，可以是 UUID 格式"
            }}
            
            特殊规则说明：
            1. "type" 字段必须且只能是 "custom_code"，不要生成其他类型的节点。
            2. "input" 定义节点的输入变量。整体结构为对象类型。"properties" 包含所有输入变量，每个输入变量为字典类型。
            3. "code_dependencies" 是节点代码运行时需要通过 pip 单独安装的 python3 依赖。整体结构为字典类型。内部的 "python3" 是固定键。"python3" 对应列表中的每个元素都是一个依赖名称。
            4. "custom_code" 是节点的 python3 代码。整体结构为字典类型。内部的 "python3" 是固定键。"python3" 对应的值是 python3 代码。代码为字符串类型。
                **Python 3 代码生成规范**：
                4.1 只提供一个主函数（main函数），所有代码逻辑都在主函数中实现
                4.2 不要提供与主函数同级的其他函数。如果需要封装函数，必须在主函数内部定义
                4.3 不要提供函数调用代码。系统会自动调用主函数
                4.4 函数的输入参数对应节点的输入变量。变量名和变量类型必须与 "input" 属性中的定义完全一致
                4.5 非必需变量必须有默认值，有默认值的变量应放在参数列表最后
                4.6 必须明确指定函数的返回数据类型为 -> dict
                4.7 主函数结尾必须返回字典类型的数据，对应节点的输出变量。字典数据的键名是输出变量名
                
                **严格禁止条款（防止TypeError错误）**：
                4.8 严禁在代码中使用条件判断语句（if/elif/else）、循环语句（for/while）、异常处理（try/except）
                4.9 严禁使用字符串检查操作（in、not in、startswith、endswith、contains）
                4.10 严禁使用复杂逻辑操作（三元运算符、逻辑运算符组合、列表推导式）
                4.11 严禁使用任何对整数类型进行迭代操作的代码
                4.12 只使用简单的数据处理操作：直接赋值、函数调用、数学运算、字符串方法（replace、upper、lower、split、join、strip等）
            5. "output" 定义节点运行后的输出变量。整体结构为对象类型。"properties" 包含所有输出变量，每个输出变量为字典类型。
            6. 注意输出变量的类型。每个输出变量的类型必须与 python3 代码返回数据中对应的数据类型严格匹配：如果 python3 代码返回 "dict" 或 "list"，对应的输出变量类型必须设置为 "json"；如果返回文件路径，对应的输出变量类型必须设置为 "file"；否则（对于字符串、整数、浮点数等）应相应设置为 "string" 或 "number"。返回字典中的每个键都必须对应一个类型匹配的输出变量。
            
            **输出质量保证**：
            - 返回的JSON结构必须语法正确，可直接解析和使用
            - 所有变量名必须符合Python命名规范
            - 生成的Python代码必须能够直接执行且不产生错误
            - 严格遵守禁止条款，防止TypeError和其他运行时错误
            - 只返回符合格式要求的完整JSON结构，无其他内容
        ''',
        'generate_workflow_node_user': '''
            我的需求：
            {user_prompt}
        '''
    },
    "zh": {
        "agent_run_type_1": "调试运行",
        "agent_run_type_2": "工作流：{app_name} 调用",
        "agent_run_type_3": "圆桌：{app_name} 调用",
        "agent_run_type_4": "圆桌：{app_name} 导向执行",
        
        # Virtual environment check messages
        "venv_exists_true": "虚拟环境已存在于缓存中",
        "venv_exists_false": "虚拟环境在缓存中不存在",
        "venv_check_failed": "检查虚拟环境失败",

        "recursive_task_root_task": "根任务",
        "recursive_task_sub_task": "子任务",
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
        
        # third-party login
        "third_party_login_platform_empty": "登录失败，平台标识不能为空",
        "third_party_login_openid_empty": "登录失败，OpenID不能为空",
        "third_party_login_platform_empty_return": "平台标识不能为空",
        "third_party_login_openid_empty_return": "OpenID不能为空",
        "third_party_login_failed": "第三方登录失败，请重试",
        "third_party_login_success": "第三方登录成功",
        "user_contact_info_missing": "当前三方账号已绑定其他的用户",

        "login_time_last_year": "年前",
        "login_time_a_month_ago": "月前",
        "login_time_days_ago": "天前",
        "login_time_hours_ago": "小时前",
        "login_time_minutes_ago": "分钟前",
        "login_time_just": "刚刚",
        "login_time_never_logged_in": "从未登录",
        "the_current_third_party_account_has_not_been_authorized_to_login":'当前三方账号未进行授权登录',

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
        'agent_message_does_not_exist': '智能体聊天消息不存在！',
        'agent_message_does_not_exist_ok': '清除聊天消息成功',
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
        'api_agent_base_update_app_id_required': '应用ID是必传的',
        'api_agent_base_update_is_public_error': '是否团队可见只能输入0或1',
        'api_agent_base_update_item_type_error': 'item_type只能输入1或2',
        'api_agent_base_update_attrs_are_visible_error': '是否属性可见只能输入0或1',
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
        'api_agent_callable_items_insert_error': '添加MCP失败',
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
        'chatroom_max_round_must_be_greater_than_zero': '最大回合数必须大于0',
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
            "exactly_one_end_node": "必须有且只有一个结束节点。",
            "node_missing_input": "节点[{node_title}]未配置输入变量。",
            "required_field_empty": "节点 '{node_title}' 中的必填字段 '{field_name}' 不能为空",
            "prompt_params_required": "节点 '{node_title}' 中的系统提示词或用户提示词必须指定其中之一",
            "input_config_required": "节点 '{node_title}' 的输入配置为必填项且不能为空",
            "prompt_user_parser_required": "节点 '{node_title}' 的用户提示词解析器为必填项且不能为空",
            "llm_prompt_required": "未填写[{node_title}]的[system]或[user]部分提示词",
            "agent_prompt_required": "未填写[{node_title}]的[user]部分提示词",
            "executor_llm_prompt_required": "未填写[{node_title}]下执行器[{executor_title}]的[system]或[user]部分提示词",
            "executor_agent_prompt_required": "未填写[{node_title}]下执行器[{executor_title}]的[user]部分提示词",
            "input_config_missing": "未配置[{node_title}]的输入属性",
            "required_param_missing": "未填写[{node_title}]的必填参数[{param_name}]",
            "node_missing_output": "节点[{node_title}]未配置输出变量。",
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
        'chatroom_request_sent_successfully': '请求成功，请等待',

        'app_run_error': 'app运行记录不存在',
        'paused_param_invalid': 'paused参数只能为0或1',
        'app_run_pause_success': '工作流暂停成功',
        'app_run_resume_success': '工作流恢复成功',
        'api_agent_generate_failed': 'agent生成记录失败',
        'api_agent_user_prompt_required': '提示词不能为空',
        'api_agent_batch_size_invalid': '批量生成数量有误',
        'agent_batch_exist_runing_rocord': '存在正在执行的记录',
        'api_agent_supplement_prompt_required': '补充提示词不能为空',
        'api_agent_save_record_error': '保存记录失败',
        'api_agent_record_error': '记录不存在',
        
        'api_skill_success': '请求成功，请等待',
        'api_skill_generate_failed': '请求失败，请稍后再试',
        'api_skill_correction_failed': '请求失败，请稍后再试',
        'api_skill_user_prompt_required': '提示词不能为空',
        'skill_validation_failed': '技能验证失败',
        'skill_create_success': '技能创建成功',
        'skill_update_success': '技能更新成功',
        # Skill related messages 
        "publish_status_invalid": "发布状态只能输入0或1",
        "invalid_app_id": "无效的应用ID",
        "update_error": "更新失败",
        "skill_not_exist": "技能不存在",
        "app_id_required": "应用ID不能为空",
        "tool_not_found": "未找到工具",
        "skill_id_required": "技能ID不能为空",
        "input_dict_required": "输入数据不能为空",
        "input_dict_format_error": "输入数据格式无效",
        "skill_error": "技能错误",
        "skill_status_not_normal": "技能状态不正常",
        "skill_draft_creators_only": "只有创建者可以运行草稿技能",
        "app_error": "应用程序错误",
        "team_members_not_open": "未向团队成员开放",
        "app_status_not_normal": "应用状态不正常",
        "skill_not_found": "未找到技能",
        "chatroom_table_orientation": "圆桌导向",
        'round_table_orientation_operation': '圆桌导向运行',
        'avatar_or_icon_required': '头像或图标至少需要填写一个',
        "graph_data_in_wrong_format": "图数据格式错误",
        'api_agent_upload_invalid_file_type': '无效的文件类型',
        'api_agent_upload_missing_keys': '缺少必要的字段',
        'api_agent_upload_invalid_json': '无效的JSON格式',
        'api_agent_upload_success': '文件上传成功',
        'api_agent_upload_failed': '文件上传失败',

        'Permission_does_not_exist': '权限不存在',
        'role_delete_success': '角色删除成功',
        'role_id_is_required': '角色ID不能为空',
        'user_does_not_belong_to_this_team': '用户不属于该团队，无法进行切换',
        'the_current_user_does_not_have_permission': '当前用户暂无权限',
        'invalid_user_id': '无效的用户ID',
        'invalid_role_id': '无效的角色ID',
        'only_admin_can_switch_member_roles': '只有管理员才能切换成员角色',
        'target_user_not_in_current_team': '目标用户不在当前团队中',
        'role_not_found': '角色不存在',
        'role_not_available_for_current_team': '该角色不适用于当前团队',
        'member_role_switched_successfully': '成员角色切换成功',
        'member_role_switch_failed': '成员角色切换失败',
        'cannot_modify_own_role': '您不能修改自己的角色',
        'cannot_modify_last_admin_role': '不能修改团队中最后一个管理员的角色',
        'cannot_delete_built_in_role': '不能删除内置角色',
        'cannot_delete_role_in_use': '不能删除正在被团队成员使用的角色',
        'role_must_be_1_or_2': '角色类型必须是1（管理员）或2（普通用户）',
        'role_id_required_for_regular_role': '设置为普通用户角色（role=2）时，必须提供角色ID',
        'comprehensive_administrator': '综合管理员',
        'agent_administrator': '智能体管理员',
        'workflow_administrator': '工作流管理员',
        'skill_administrator': '技能管理员',
        'roundtable_administrator': '圆桌管理员',
        'knowledge_base_administrator': '知识库管理员',

        # 角色描述 - 用户友好的显示文案
        'comprehensive_administrator_desc': '全能型管理者，可以创建和管理所有类型的AI应用，包括智能体、工作流、技能等',
        'agent_administrator_desc': '专注于智能体的创建、配置和管理，打造个性化的AI助手',
        'workflow_administrator_desc': '专门负责工作流的设计和优化，高效自动化业务流程',
        'skill_administrator_desc': '专注于技能开发和管理，为AI系统扩展新能力',
        'roundtable_administrator_desc': '负责圆桌会议的组织和管理，促进团队协作交流',
        'knowledge_base_administrator_desc': '专门管理企业知识资产，维护和优化知识库内容，提供最佳信息获取体验',

        'msg_preparing_environment': '需要初始化运行环境，请耐心等待',
        'msg_mcp_tool_result_is_truncated': '工具输出内容过长（字符数大于{length}），因此只会保存部分内容',
        'the_current_account_has_been_bound': '当前账号已绑定',
        'binding_successful': '绑定成功',
        'openid_list_empty': 'OpenId列表为空',
        'third_party_binding_not_found': '未找到第三方绑定',
        'cancel_binding_failed': '取消绑定失败',
        'cancel_binding_successful': '取消绑定成功',
        'roles_status_only_one_or_two': '是否显示全部角色状态只能选择1和2',
        'permission_status_only_one_or_two': '是否显示全部权限状态只能选择1和2',
        'the_current_email_address_is_not_registered': '当前邮箱未注册',
        'verification_code_sent_successfully': '验证码发送成功',
        'email_sending_failed': '邮件发送失败',
        'an_error_occurred_while_sending_the_verification_code': '发送验证码时发生错误',
        'verification_code_cannot_be_empty': '验证码不能为空',
        'verification_code_expired_or_not_exist': '验证码已过期或不存在',
        'verification_code_incorrect': '验证码错误',
        'email_verification_successful': '邮箱验证成功',
        'email_verification_failed': '邮箱验证失败',
        'email_format_incorrect': '邮箱格式不正确',
        'password_cannot_be_empty': '密码不能为空',
        'confirm_password_cannot_be_empty': '确认密码不能为空',
        'passwords_do_not_match': '密码和确认密码不一致',
        'password_reset_successful': '密码重置成功',
        'password_reset_failed': '密码重置失败',
        'email_verification_not_completed': '邮箱验证未完成，请先进行邮箱验证',
        'verification_status_invalid': '验证状态无效，请重新进行邮箱验证',
        'invitation_links_generated_successfully': '邀请成功',
        'invitation_emails_sent_successfully': '邀请邮件发送成功',
        'some_emails_already_registered': '部分邮箱已注册',
        'email_already_registered': '{email} 已注册',
        'invitation_email_sent_successfully': '邀请邮件发送成功',
        'invitation_email_send_failed': '部分邀请邮件发送失败',
        'invitation_email_send_exception': '邮件发送异常',
        'email_already_registered': '邮箱 {email} 已经注册过了',
        'some_emails_already_registered': '部分邮箱已经注册过了',
        'invitation_links_generated_successfully': '邀请成功',
        'invitation_emails_sent_successfully': '所有邀请邮件发送成功',
        'profile_updated_successfully': '个人资料更新成功',
        'profile_update_failed': '个人资料更新失败',
        'old_password_incorrect': '旧密码不正确',
        'new_passwords_do_not_match': '新密码和确认密码不一致',
        'password_changed_successfully': '密码修改成功',
        'password_change_failed': '密码修改失败',
        'old_password_cannot_be_empty': '旧密码不能为空',
        'new_password_cannot_be_empty': '新密码不能为空',
        'confirm_password_cannot_be_empty': '确认密码不能为空',
        
        # 定时任务相关提示
        'scheduled_task_name_required': '定时任务名称不能为空',
        'scheduled_task_app_id_required': '应用ID不能为空',
        'scheduled_task_workflow_id_required': '工作流ID不能为空',
        'scheduled_task_input_required': '输入数据不能为空',
        'scheduled_task_start_time_required': '开始时间不能为空',
        'scheduled_task_task_data_required': '任务数据不能为空',
        'scheduled_task_app_not_found': '应用不存在或状态异常',
        'scheduled_task_workflow_not_found': '工作流不存在或状态异常',
        'scheduled_task_create_success': '定时任务创建成功',
        'scheduled_task_create_failed': '定时任务创建失败',
        'scheduled_task_update_success': '定时任务更新成功',
        'scheduled_task_update_failed': '定时任务更新失败',
        'scheduled_task_delete_success': '定时任务删除成功',
        'scheduled_task_delete_failed': '定时任务删除失败',
        'scheduled_task_not_found': '定时任务不存在',
        'scheduled_task_no_permission': '没有权限操作此定时任务',
        'scheduled_task_invalid_repeat_type': '无效的重复类型',
        'scheduled_task_invalid_repeat_interval': '重复间隔必须大于0',
        'scheduled_task_invalid_max_executions': '最大执行次数不能为负数',
        'scheduled_task_end_time_before_start_time': '结束时间不能早于开始时间',
        'scheduled_task_repeat_days_invalid': '重复天数格式无效',
        'scheduled_task_repeat_day_of_month_invalid': '月重复日期必须在1-31之间',
        'scheduled_task_repeat_month_invalid': '年重复月份必须在1-12之间',
        'scheduled_task_repeat_day_of_year_invalid': '年重复日期必须在1-365之间',
        'scheduled_task_app_not_exists': '应用不存在',
        'scheduled_task_app_not_public': '应用未公开',
        'scheduled_task_app_no_team_permission': '无权限访问此应用（不同团队）',
        
        # 工作流节点生成相关提示
        'api_workflow_success': '请求成功，请等待',
        'api_workflow_generate_failed': '请求失败，请稍后再试',
        'api_workflow_user_prompt_required': '提示词不能为空',
        'generate_workflow_node_user': '''
            我的需求：
            {user_prompt}
        '''
    }
}

# Dictionary to store all prompt keys (ordered)
prompt_keys = [
    "agent_system_prompt_with_auto_match_ability",
    "agent_system_prompt_with_auto_match_ability_direct_output",
    "agent_system_prompt_with_abilities",
    "agent_system_prompt_with_no_ability",
    "agent_retrieved_docs_format",
    "agent_reply_requirement_with_auto_match_ability",
    "agent_reply_requirement_with_task_splitting_and_auto_match_ability",
    "agent_reply_requirement_with_task_splitting_and_abilities",
    "agent_reply_requirement_with_task_splitting_and_no_ability",
    "agent_output_format_1",
    "agent_output_format_2",
    "agent_output_format_3",
    "agent_output_format_2_md",
    "agent_team_members",
    "agent_user_prompt",
    "agent_user_prompt_with_retrieved_docs",
    
    "chatroom_manager_system",
    "chatroom_manager_system_with_optional_selection",
    "chatroom_manager_user",
    "chatroom_manager_user_with_optional_selection",
    "chatroom_manager_user_invalid_selection",
    "chatroom_agent_description_with_abilities",
    "chatroom_agent_description_with_no_ability",
    "chatroom_agent_user_subprompt",
    "chatroom_role_user",
    "chatroom_role_agent",
    "chatroom_title_system",
    "chatroom_title_user",
    "chatroom_meeting_summary_system",
    "chatroom_meeting_summary_user",
    "chatroom_meeting_summary_system_correct",
    "chatroom_meeting_summary_user_correct",
    "chatroom_generate_meeting_summary_from_a_single_message_system_correct",
    "chatroom_generate_meeting_summary_from_a_single_message_user_correct",
    "chatroom_conference_orientation_system",
    "chatroom_conference_orientation_user",
    "chatroom_conference_orientation_system_correct",
    "chatroom_conference_orientation_user_correct",
    
    "requirement_category",
    "llm_reply_requirement_with_task_splitting",
    "recursive_task_generation",
    "recursive_task_assign",
    "recursive_task_execute",
    "recursive_task_execute_agent_user_subprompt",
    
    "generate_agent_system_prompt",
    "generate_agent_user",
    "regenerate_agent_system",
    "regenerate_agent_user",
    "agent_supplement_system",
    "agent_supplement_user",
    "agent_batch_sample_system",
    "agent_batch_sample_user",
    "agent_batch_one_system",
    "agent_batch_one_user",
    "agent_batch_generate_system",
    "agent_batch_generate_user",
    
    "generate_skill_system_prompt",
    "generate_skill_user",
    "correction_skill_system_prompt",
    "correction_skill_user",
    
    "generate_workflow_node_system_prompt",
    "generate_workflow_node_user"
]

# Dictionary to store prompt function descriptions
prompt_descriptions = {
    "en": [
        {
            "group_name": "Agent",
            "prompts": {
                "agent_system_prompt_with_auto_match_ability": "Agent System Prompt (Auto-Match Ability - JSON Output with Ability ID)",
                "agent_system_prompt_with_auto_match_ability_direct_output": "Agent System Prompt (Auto-Match Ability - Text Output without Ability ID)",
                "agent_system_prompt_with_abilities": "Agent System Prompt (Specify One or All Abilities)",
                "agent_system_prompt_with_no_ability": "Agent System Prompt (No Ability)",
                "agent_retrieved_docs_format": "Agent Retrieved Knowledge Base Content Format [Sub]",
                "agent_reply_requirement_with_auto_match_ability": "Agent Reply Requirement (Auto-Match Ability) [Sub]",
                # "agent_reply_requirement_with_task_splitting_and_auto_match_ability": "Agent Reply Requirement with Task Splitting and Auto-Match Ability",
                # "agent_reply_requirement_with_task_splitting_and_abilities": "Agent Reply Requirement with Task Splitting and Abilities",
                # "agent_reply_requirement_with_task_splitting_and_no_ability": "Agent Reply Requirement with Task Splitting (No Ability)",
                # "agent_output_format_1": "Agent Output Format: Plain Text",
                # "agent_output_format_2": "Agent Output Format: JSON",
                # "agent_output_format_3": "Agent Output Format: Code",
                # "agent_output_format_2_md": "Agent Output Format: JSON in Markdown",
                "agent_team_members": "Team Members List [Sub]",
                "agent_user_prompt": "Agent User Prompt (Not Bound to Knowledge Base)",
                "agent_user_prompt_with_retrieved_docs": "Agent User Prompt (With Knowledge Base Retrieval)"
            }
        },
        {
            "group_name": "Round Table",
            "prompts": {
                "chatroom_manager_system": "Round Table Manager System Prompt (Must Select Next Speaking Agent)",
                "chatroom_manager_system_with_optional_selection": "Round Table Manager System Prompt (Optional Selection of Next Agent or End Conversation)",
                "chatroom_manager_user": "Round Table Manager User Prompt (Must Select Next Speaking Agent)",
                "chatroom_manager_user_with_optional_selection": "Round Table Manager User Prompt (Optional Selection of Next Agent or End Conversation)",
                "chatroom_manager_user_invalid_selection": "Round Table Manager User Prompt (Previous Selection Invalid, Reselect) [Sub]",
                "chatroom_agent_description_with_abilities": "Round Table Manager User Prompt (Agent with Abilities) [Sub]",
                "chatroom_agent_description_with_no_ability": "Round Table Manager User Prompt (Agent without Ability) [Sub]",
                "chatroom_agent_user_subprompt": "Agent User Prompt in Round Table [Sub]",
                # "chatroom_role_user": "Chatroom User Role",
                # "chatroom_role_agent": "Chatroom Agent Role",
                "chatroom_title_system": "Round Table Title Generator System Prompt",
                "chatroom_title_user": "Round Table Title Generator User Prompt"
            }
        },
        {
            "group_name": "Round Table Orientation",
            "prompts": {
                "chatroom_meeting_summary_system": "Round Table Discussion Summary System Prompt",
                "chatroom_meeting_summary_user": "Round Table Discussion Summary User Prompt",
                "chatroom_meeting_summary_system_correct": "Round Table Discussion Summary Correction System Prompt",
                "chatroom_meeting_summary_user_correct": "Round Table Discussion Summary Correction User Prompt",
                "chatroom_generate_meeting_summary_from_a_single_message_system_correct": "Round Table Discussion Summary System Prompt (Single Message)",
                "chatroom_generate_meeting_summary_from_a_single_message_user_correct": "Round Table Discussion Summary User Prompt (Single Message)",
                "chatroom_conference_orientation_system": "Round Table Orientation Data Generation System Prompt",
                "chatroom_conference_orientation_user": "Round Table Orientation Data Generation User Prompt",
                "chatroom_conference_orientation_system_correct": "Round Table Orientation Data Correction System Prompt",
                "chatroom_conference_orientation_user_correct": "Round Table Orientation Data Correction User Prompt"
            }
        },
        {
            "group_name": "Workflow Nodes",
            "prompts": {
                "requirement_category": "Problem Classifier Node Prompt",
                # "llm_reply_requirement_with_task_splitting": "LLM Reply Requirement with Task Splitting",
                "recursive_task_generation": "Recursive Task Generation Node Prompt",
                "recursive_task_assign": "Recursive Task Assignment Prompt",
                "recursive_task_execute": "Recursive Task Execution Node Prompt",
                "recursive_task_execute_agent_user_subprompt": "Recursive Task Execution Corresponding Agent User Prompt [Sub]"
            }
        },
        {
            "group_name": "AI Generate Agent",
            "prompts": {
                "generate_agent_system_prompt": "AI Generate Agent System Prompt",
                "generate_agent_user": "AI Generate Agent User Prompt",
                "regenerate_agent_system": "AI Regenerate Agent System Prompt",
                "regenerate_agent_user": "AI Regenerate Agent User Prompt",
                "agent_supplement_system": "AI Correct Agent System Prompt",
                "agent_supplement_user": "AI Correct Agent User Prompt",
                "agent_batch_sample_system": "AI Generate Sample Agent System Prompt",
                "agent_batch_sample_user": "AI Generate Sample Agent User Prompt",
                "agent_batch_one_system": "AI Batch Generate Agent System Prompt",
                "agent_batch_one_user": "AI Batch Generate Agent User Prompt"
                # "agent_batch_generate_system": "AI Batch Generate Agent System Prompt",
                # "agent_batch_generate_user": "AI Batch Generate Agent User Prompt",
            }
        },
        {
            "group_name": "AI Generate Skill",
            "prompts": {
                "generate_skill_system_prompt": "AI Generate Skill System Prompt",
                "generate_skill_user": "AI Generate Skill User Prompt",
                "correction_skill_system_prompt": "AI Correct Skill System Prompt",
                "correction_skill_user": "AI Correct Skill User Prompt"
            }
        },
        {
            "group_name": "AI Generate Workflow Node",
            "prompts": {
                "generate_workflow_node_system_prompt": "AI Generate Workflow Node System Prompt",
                "generate_workflow_node_user": "AI Generate Workflow Node User Prompt"
            }
        }
    ],
    "zh": [
        {
            "group_name": "智能体",
            "prompts": {
                "agent_system_prompt_with_auto_match_ability": "智能体系统提示词（自动匹配能力-带能力ID的JSON结构输出）",
                "agent_system_prompt_with_auto_match_ability_direct_output": "智能体系统提示词（自动匹配能力-不带能力ID的文本输出）",
                "agent_system_prompt_with_abilities": "智能体系统提示词（指定一个或全部能力）",
                "agent_system_prompt_with_no_ability": "智能体系统提示词（无能力）",
                "agent_retrieved_docs_format": "智能体检索知识库内容格式【子】",
                "agent_reply_requirement_with_auto_match_ability": "智能体回复要求（自动匹配能力）【子】",
                # "agent_reply_requirement_with_task_splitting_and_auto_match_ability": "智能体回复要求（任务拆分和自动匹配能力）",
                # "agent_reply_requirement_with_task_splitting_and_abilities": "智能体回复要求（任务拆分和能力）",
                # "agent_reply_requirement_with_task_splitting_and_no_ability": "智能体回复要求（任务拆分-无能力）",
                # "agent_output_format_1": "智能体输出格式：纯文本【子】",
                # "agent_output_format_2": "智能体输出格式：JSON【子】",
                # "agent_output_format_3": "智能体输出格式：代码【子】",
                # "agent_output_format_2_md": "智能体输出格式：Markdown形式的JSON【子】",
                "agent_team_members": "团队成员列表【子】",
                "agent_user_prompt": "智能体用户提示词（未绑定知识库）",
                "agent_user_prompt_with_retrieved_docs": "智能体用户提示词（检索知识库）"
            }
        },
        {
            "group_name": "圆桌",
            "prompts": {
                "chatroom_manager_system": "圆桌管理员系统提示词（必选下一个发言的智能体）",
                "chatroom_manager_system_with_optional_selection": "圆桌管理员系统提示词（可选下一个发言的智能体或结束对话）",
                "chatroom_manager_user": "圆桌管理员用户提示词（必选下一个发言的智能体）",
                "chatroom_manager_user_with_optional_selection": "圆桌管理员用户提示词（可选下一个发言的智能体或结束对话）",
                "chatroom_manager_user_invalid_selection": "圆桌管理员用户提示词（上一次选择无效，重新选择）【子】",
                "chatroom_agent_description_with_abilities": "圆桌管理员用户提示词（智能体有能力）【子】",
                "chatroom_agent_description_with_no_ability": "圆桌管理员用户提示词（智能体无能力）【子】",
                "chatroom_agent_user_subprompt": "圆桌中智能体的用户提示词【子】",
                # "chatroom_role_user": "聊天室用户角色",
                # "chatroom_role_agent": "聊天室智能体角色",
                "chatroom_title_system": "圆桌标题生成器系统提示词",
                "chatroom_title_user": "圆桌标题生成器用户提示词"
            }
        },
        {
            "group_name": "圆桌导向",
            "prompts": {
                "chatroom_meeting_summary_system": "圆桌讨论总结系统提示词",
                "chatroom_meeting_summary_user": "圆桌讨论总结用户提示词",
                "chatroom_meeting_summary_system_correct": "圆桌讨论总结修正系统提示词",
                "chatroom_meeting_summary_user_correct": "圆桌讨论总结修正用户提示词",
                "chatroom_generate_meeting_summary_from_a_single_message_system_correct": "圆桌讨论总结系统提示词（单条消息）",
                "chatroom_generate_meeting_summary_from_a_single_message_user_correct": "圆桌讨论总结用户提示词（单条消息）",
                "chatroom_conference_orientation_system": "圆桌导向数据生成系统提示词",
                "chatroom_conference_orientation_user": "圆桌导向数据生成用户提示词",
                "chatroom_conference_orientation_system_correct": "圆桌导向数据修正系统提示词",
                "chatroom_conference_orientation_user_correct": "圆桌导向数据修正用户提示词"
            }
        },
        {
            "group_name": "工作流节点",
            "prompts": {
                "requirement_category": "问题分类器节点提示词",
                # "llm_reply_requirement_with_task_splitting": "LLM回复要求（任务拆分）",
                "recursive_task_generation": "递归任务生成节点提示词",
                "recursive_task_assign": "递归任务分配提示词",
                "recursive_task_execute": "递归任务执行节点提示词",
                "recursive_task_execute_agent_user_subprompt": "递归任务执行对应的智能体用户提示词【子】"
            }
        },
        {
            "group_name": "AI生成智能体",
            "prompts": {
                "generate_agent_system_prompt": "AI生成智能体系统提示词",
                "generate_agent_user": "AI生成智能体用户提示词",
                "regenerate_agent_system": "AI重新生成智能体系统提示词",
                "regenerate_agent_user": "AI重新生成智能体用户提示词",
                "agent_supplement_system": "AI修正智能体系统提示词",
                "agent_supplement_user": "AI修正智能体用户提示词",
                "agent_batch_sample_system": "AI生成样例智能体系统提示词",
                "agent_batch_sample_user": "AI生成样例智能体用户提示词",
                "agent_batch_one_system": "AI批量生成智能体系统提示词",
                "agent_batch_one_user": "AI批量生成智能体用户提示词"
                # "agent_batch_generate_system": "AI批量生成智能体系统提示词",
                # "agent_batch_generate_user": "AI批量生成智能体用户提示词",
            }
        },
        {
            "group_name": "AI生成技能",
            "prompts": {
                "generate_skill_system_prompt": "AI生成技能系统提示词",
                "generate_skill_user": "AI生成技能用户提示词",
                "correction_skill_system_prompt": "AI修正技能系统提示词",
                "correction_skill_user": "AI修正技能用户提示词"
            }
        },
        {
            "group_name": "AI生成工作流节点",
            "prompts": {
                "generate_workflow_node_system_prompt": "AI生成工作流节点系统提示词",
                "generate_workflow_node_user": "AI生成工作流节点用户提示词"
            }
        }
    ]
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

    try:
        from api.utils.auth import get_current_language
        actual_uid = uid if uid > 0 else int(os.getenv('ACTUAL_USER_ID', 0))
        current_language = get_current_language(actual_uid)
    except:
        current_language = "en"
    
    keys = key.split('.')

    if key in prompt_keys:
        # Check if prompt.py exists in current directory
        prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt.py')
        
        if not os.path.exists(prompt_file_path):
            # If not exists, create prompt.py file
            _create_prompt_file()
        
        # Dynamic import of prompt.py
        try:
            # If module already imported, reload to get latest content
            if 'prompt' in sys.modules:
                prompt_module = importlib.reload(sys.modules['prompt'])
            else:
                import prompt as prompt_module
            
            if hasattr(prompt_module, 'PROMPTS') and key in prompt_module.PROMPTS:
                content = prompt_module.PROMPTS[key]
            else:
                # If no corresponding key in prompt.py, fallback to language_packs
                content = language_packs.get("en", {})
                for k in keys:
                    if isinstance(content, dict):
                        content = content.get(k, None)
                    else:
                        return None
        except ImportError:
            # If import fails, fallback to language_packs
            content = language_packs.get("en", {})
            for k in keys:
                if isinstance(content, dict):
                    content = content.get(k, None)
                else:
                    return None
        
        if append_ret_lang_prompt:
            # Get detailed time information
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            year = now.year
            month = now.month
            day = now.day
            hour = now.hour
            minute = now.minute
            second = now.second
            weekday = now.strftime("%A")  # Full weekday name
            weekday_num = now.weekday()  # Monday is 0, Sunday is 6
            week_number = now.isocalendar()[1]  # ISO week number
            day_of_year = now.timetuple().tm_yday
            
            return_language_prompt = f"""

=== IMPORTANT CONTEXT ===
CURRENT DATE AND TIME: {current_time}
DETAILED TIME INFORMATION:
- Year: {year}
- Month: {month}
- Day: {day}
- Hour: {hour}
- Minute: {minute}
- Second: {second}
- Weekday: {weekday} (Day {weekday_num + 1} of the week)
- Week Number: {week_number} (ISO week)
- Day of Year: {day_of_year}

Always consider the current date and time when providing responses, especially for time-sensitive questions or tasks.

Please note that the language of the returned content should be {language_names[current_language]}, unless the user explicitly specifies the language of the returned content in a subsequent instruction.

If the user requests any type of chart, diagram, graph, or visual representation (including but not limited to flowcharts, sequence diagrams, Gantt charts, pie charts, bar charts, line graphs, mind maps, organizational charts, network diagrams, etc.), you MUST respond with complete Mermaid diagram code.
The Mermaid code must be fully valid and syntactically correct, so that it can be directly rendered in any Mermaid-compatible viewer without errors.
Always enclose the Mermaid code in proper fenced code blocks using the mermaid language tag.
If multiple diagram types are possible, choose the one that best fits the user’s request.
Double-check the logic, structure, and syntax to ensure correctness and renderability before responding.
=== END CONTEXT ==="""
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


def _create_prompt_file():
    """
    Create prompt.py file containing all prompt_keys content
    """
    prompt_file_path = os.path.join(os.path.dirname(__file__), 'prompt.py')
    
    # Build PROMPTS dictionary
    prompts_dict = {}
    
    for key in prompt_keys:
        keys = key.split('.')
        content = language_packs.get("en", {})
        
        for k in keys:
            if isinstance(content, dict):
                content = content.get(k, None)
            else:
                content = None
                break
        
        if content is not None:
            prompts_dict[key] = content
    
    # Generate file content
    file_content = '''# -*- coding: utf-8 -*-
"""
Dynamically generated prompt file
This file is automatically generated by the system and contains all built-in prompts
You can directly modify the prompt content in this file, and the system will dynamically load the latest content
"""

PROMPTS = {
'''
    
    for key, value in prompts_dict.items():
        if isinstance(value, str):
            # Use triple quotes to preserve original formatting
            file_content += f'    "{key}": """{value}""",\n'
        elif isinstance(value, dict):
            # Format dict with proper indentation and triple quotes for string values
            file_content += f'    "{key}": {{\n'
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    file_content += f'        "{sub_key}": """{sub_value}""",\n'
                else:
                    file_content += f'        "{sub_key}": {repr(sub_value)},\n'
            file_content += '    },\n'
    
    file_content += '}\n'
    
    # Write to file
    with open(prompt_file_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    print(f"Created prompt.py file at: {prompt_file_path}")