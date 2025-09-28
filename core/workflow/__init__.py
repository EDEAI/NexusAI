import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent))

from typing import Dict, List, Optional, Any
from celery.exceptions import TimeoutError as CeleryTimeoutError
from .variables import *
from .edges import *
from .graph import *
from .context import *
from .recursive_task import *
from core.database.models.chatroom_driven_records import ChatroomDrivenRecords
from core.database.models import Apps, Workflows, AppRuns, AppNodeUserRelation

def start_workflow(
    team_id: int, 
    user_id: int, 
    app_id: int, 
    run_type: int, 
    run_name: str, 
    inputs: dict,
    knowledge_base_mapping: Optional[Dict[str, Any]] = None,
    node_confirm_users: Optional[Dict[str, List[int]]] = None,
    data_source_run_id: Optional[int] = 0
) -> None:
    """
    Start the workflow.
    
    Args:
        team_id (int): Team ID.
        user_id (int): User ID.
        app_id (int): App ID.
        run_type (int): Run type.
        run_name (str): Run name.
        inputs (dict): Inputs.
        node_confirm_users (Optional[Dict[str, List[int]]], optional): Node confirm users. Defaults to None.
    """
    from celery_app import asr
    from core.database.models import NonLLMRecords, UploadFiles

    if run_type not in [0, 1]:
        raise Exception('Run type error.')
    run_type = run_type + 1
    app_runs = AppRuns()
    
    workflow = Workflows().workflow_info(app_id, run_type, team_id)
    
    # Check permissions:
    # 1. The user who created the workflow can run the workflow.
    # 2. The team member can run the workflow if the workflow is public.
    if (
        workflow['user_id'] != user_id
        and (
            workflow['team_id'] != team_id
            or workflow['is_public'] == 0
        )
    ):
        raise Exception("You are not authorized to run this workflow.")
    
    # if app_runs.get_workflow_running_count(workflow_id=workflow['id']) > 0:
    #     raise Exception("Workflow is already running.")
    
    if not inputs:
        raise ValueError(get_language_content("graph_validation_errors.inputs_cannot_be_empty"))
    
    inputs_var = create_variable_from_dict(inputs)
    validate_required_variable(inputs_var)

    for input_var in inputs_var.properties.values():
        if input_var.type == 'file' and isinstance(input_var.value, int):
            file_id = input_var.value
            file_data = UploadFiles().get_file_by_id(file_id)
            if not file_data:
                raise Exception(f"File ID {file_id} not found.")
            if (
                file_data['extension'] in ['.mp3', '.ogg', '.m4a', '.flac', '.wav']
                and NonLLMRecords().get_record_by_input_file_id(file_id) is None
            ):
                task = asr.delay(user_id, team_id, input_var.value)
                try:
                    task.get(timeout=60)
                except CeleryTimeoutError:
                    raise Exception(f"ASR task for file {file_data['name'] + file_data['extension']} timed out.")

    graph = create_graph_from_dict(workflow['graph'])
    graph.validate()

    app_run_data = {
        'user_id': user_id,
        'app_id': app_id,
        'workflow_id': workflow['id'],
        'type': run_type,
        'name': run_name,
        'graph': graph.to_dict(),
        'inputs': inputs,
        'status': 1,
        'total_steps': graph.get_total_steps()
    }
    if knowledge_base_mapping is not None:
        app_run_data['knowledge_base_mapping'] = knowledge_base_mapping
    app_run_id = app_runs.insert(app_run_data)
    if data_source_run_id > 0:
        chatroomdriven_info = ChatroomDrivenRecords().get_data_by_data_source_run_id(data_source_run_id)
        if chatroomdriven_info:
            ChatroomDrivenRecords().update_data_driven_run_id(chatroomdriven_info['id'],data_source_run_id, app_run_id)
    if node_confirm_users:
        AppNodeUserRelation().create_data(app_run_id, node_confirm_users)
    
    Apps().increment_execution_times(app_id)
    
    return {'app_id': app_id, 'workflow_id': workflow['id'], 'app_run_id': app_run_id}

__all__ = [
    "VariableTypes",
    "Variable",
    "ArrayVariable",
    "ObjectVariable",
    "create_variable_from_dict",
    "validate_required_variable",
    "replace_value_in_variable",
    "replace_value_in_variable_with_new_value",
    "get_first_variable_value",
    "flatten_variable",
    "flatten_variable_with_values",
    "convert_to_fastapi_model",
    "create_object_variable_from_list",
    
    "Edge",
    "Edges",
    "create_edge_from_dict",
    "create_edges_from_list",
    
    "Graph",
    "create_graph_from_dict",
    
    "Context",
    "create_context_from_dict",
    "replace_variable_value_with_context",
    
    "RecursiveTaskCategory",
    "create_recursive_task_category_from_dict",
    "merge_recursive_task_categories",
    
    "start_workflow"
]