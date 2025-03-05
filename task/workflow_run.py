"""
This script is designed to execute node tasks within a workflow.
"""
import json, os, sys, time, threading, traceback
os.environ['DATABASE_AUTO_COMMIT'] = 'True'
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from typing import Dict, Optional, Any
from log import Logger
from core.database import redis
from core.database.models import AppRuns, AppNodeExecutions, AppNodeUserRelation, UploadFiles
from core.workflow import *
from core.workflow.nodes import *
from celery_app import run_workflow_node
from core.helper import push_to_websocket_queue, get_websocket_queue_length
from languages import get_language_content
from api.utils.common import extract_file_list_from_skill_output

logger = Logger.get_logger('workflow_run')

task_timeout = 60  # Timeout for Celery task execution
global_tasks = [] # List to store tasks
running = True  # Global flag to control thread loops
level_tasks = {}  # Dictionary to store tasks status for each level

# Database models
app_run = AppRuns()
app_node_exec = AppNodeExecutions()
app_node_user_relation = AppNodeUserRelation()

def update_app_run(app_run_id: int, data: dict) -> bool:
    """
    Updates an app run record in the database.
    
    :param app_run_id: The ID of the app run record.
    :param data: A dictionary containing the data to update.
    :return: True if the record was updated successfully, False otherwise.
    """
    data_copy = data.copy()
    if data_copy.get('need_human_confirm', None) == 0 and app_node_exec.has_human_confirm_node(app_run_id):
        data_copy.pop('need_human_confirm')
    return app_run.update(conditions={'column': 'id', 'value': app_run_id}, data=data_copy)

def update_node_exec(exec_id: int, data: dict) -> bool:
    """
    Updates a node execution record in the database.
    
    :param exec_id: The ID of the node execution record.
    :param data: A dictionary containing the data to update.
    :return: True if the record was updated successfully, False otherwise.
    """
    return app_node_exec.update(conditions={'column': 'id', 'value': exec_id}, data=data)

def should_skip_node(node_id, edge_maps, skipped_edges):
    """
    Determines if all edges leading to the node are skipped or not.

    :param node_id: The ID of the node to check.
    :param edge_maps: A dictionary containing incoming and outgoing edges for each node.
    :param skipped_edges: A list of already skipped edges' IDs.
    :return: True if the node should be skipped, False otherwise.
    """
    for edge in edge_maps.get("incoming", {}).get(node_id, []):
        if edge.id not in skipped_edges:
            return False
    return True

def skip_edges_from_node(node_id, edge_maps, skipped_edges):
    """
    Recursively skip edges starting from a given node, with a check to stop skipping if necessary.

    :param node_id: The ID of the node to start skipping from.
    :param edge_maps: A dictionary containing incoming and outgoing edges for each node.
    :param skipped_edges: A list of already skipped edges' IDs.
    """
    for edge in edge_maps.get("outgoing", {}).get(node_id, []):
        if edge.id not in skipped_edges:
            skipped_edges.append(edge.id)
            if should_skip_node(edge.target_node_id, edge_maps, skipped_edges):
                logger.debug(f"Recursively skipping edge: {edge.id} from node: {node_id}")
                skip_edges_from_node(edge.target_node_id, edge_maps, skipped_edges)
            else:
                logger.debug(f"Can not skip node:{edge.target_node_id} as there are other edges leading to it not skipped")
                
def create_celery_task(
    team_id: int,
    app_id: int,
    app_name: str,
    icon: str,
    icon_background: str,
    workflow_id: int,
    app_user_id: int,
    user_id: int,
    app_run_id: int,
    run_type: int,
    run_name: str,
    exec_id: int,
    edge: Optional[Edge],
    node: Node,
    task_level: int = 0,
    task_data: Optional[Dict[str, Any]] = None,
    task_operation: str = '', 
    parent_exec_id: int = 0,
    context: Optional[Context] = None,
    ancestor_context: Optional[Context] = None,
    correct_llm_output: bool = False
):
    """
    Creates a Celery task to execute a node asynchronously.
    
    :param team_id: The ID of the team.
    :param app_id: The ID of the app.
    :param app_name: The name of the app.
    :param workflow_id: The ID of the workflow.
    :param app_user_id: The ID of the app user.
    :param user_id: The ID of the user.
    :param app_run_id: The ID of the app run.
    :param run_type: The type of the run.
    :param run_name: The name of the run.
    :param exec_id: The ID of the node execution record.
    :param edge: The edge object.
    :param node: The node object.
    :param task_level: The level of the task.
    :param task_data: A dictionary containing task-specific information.
    :param task_operation: The task operation.
    :param parent_exec_id: The ID of the parent node execution record.
    :param context: The context object.
    :param ancestor_context: The ancestor context object.
    :param correct_llm_output: Flag to indicate if correct LLM output is found.
    """
    level = edge.level if edge else 0
    # Execute the node asynchronously using Celery
    task = run_workflow_node.delay(
        node_dict=node.to_dict(), 
        context_dict=ancestor_context.to_dict() if ancestor_context else None, 
        app_id=app_id,
        workflow_id=workflow_id,
        user_id=user_id,
        app_run_id=app_run_id,
        type=run_type,
        node_exec_id=exec_id,
        edge_id=edge.id if edge else None,
        source_node_type=edge.source_node_type if edge else None,
        level=level,
        task_level=task_level,
        task=task_data,
        correct_llm_output=correct_llm_output
    )
    # Add task to global tasks list
    global_tasks.append((task, team_id, app_user_id, app_name, icon, icon_background, app_run_id, run_name, level, edge if edge else None, node, context if context else None, exec_id, task_operation, parent_exec_id))
    # Add task to level tasks dictionary
    if app_run_id not in level_tasks:
        level_tasks[app_run_id] = {}
    if level not in level_tasks[app_run_id]:
        level_tasks[app_run_id][level] = []
    level_tasks[app_run_id][level].append(task.id)
    logger.info(f"Task added for run:{app_run_id} level:{level} node:{node.id}:{node.data['type']}:{node.data['title']} task_id:{task.id}")
    
def remove_task_cache(item):
    """
    Removes a task from the global tasks list and level tasks dictionary.
    
    :param item: The task item to remove.
    """
    global_tasks.remove(item)  # Remove task from global tasks list
    task, _, _, _, _, _, app_run_id, _, level, _, _, _, _, _, _ = item
    # Remove task from level tasks dictionary
    level_tasks[app_run_id][level].remove(task.id)
    if not level_tasks[app_run_id][level]:
        del level_tasks[app_run_id][level]
        if not level_tasks[app_run_id]:
            del level_tasks[app_run_id]
    
def push_workflow_debug_message(
    user_id: int,
    app_id: int,
    workflow_id: int,
    app_run_id: int,
    run_type: int,
    level: int,
    edge: Optional[Edge],
    node: Node,
    status: int,
    error: Optional[str],
    completed_steps: int,
    actual_completed_steps: int,
    need_human_confirm: int,
    elapsed_time: float,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    embedding_tokens: int,
    reranking_tokens: int,
    total_steps: int,
    created_time: Optional[datetime],
    finished_time: Optional[datetime],
    node_exec_id: int,
    parent_exec_id: int,
    first_task_exec_id: int,
    node_exec_data: dict
):
    """
    Pushes a workflow debug message to the WebSocket message queue.
    
    :param user_id: The ID of the user.
    :param app_id: The ID of the app.
    :param workflow_id: The ID of the workflow.
    :param app_run_id: The ID of the app run.
    :param run_type: The type of the run.
    :param level: The level of the run.
    :param edge: The edge object.
    :param node: The node object.
    :param status: The status of the run.
    :param error: The error message.
    :param completed_steps: The number of completed steps.
    :param actual_completed_steps: The number of actual completed steps.
    :param need_human_confirm: Flag to indicate if human confirmation is needed.
    :param elapsed_time: The elapsed time.
    :param prompt_tokens: The number of prompt tokens.
    :param completion_tokens: The number of completion tokens.
    :param total_tokens: The total number of tokens.
    :param embedding_tokens: The number of embedding tokens.
    :param reranking_tokens: The number of reranking tokens.
    :param total_steps: The total number of steps.
    :param created_time: The created time.
    :param finished_time: The finished time.
    :param node_exec_id: The ID of the node execution record.
    :param parent_exec_id: The ID of the parent node execution record.
    :param first_task_exec_id: The ID of the first task execution record.
    :param node_exec_data: A dictionary containing the node execution data.
    """
    if run_type != 1:
        return
    
    model_data = node_exec_data.pop('model_data', None)
    prompt_data = []
    if model_data:
        for message in model_data["messages"]:
            prompt_data.append({message[0]: message[1]["value"]})
    node_exec_data["prompt_data"] = prompt_data
    if inputs := node_exec_data.get('inputs'):
        inputs = create_variable_from_dict(inputs)
        inputs = flatten_variable_with_values(inputs)
        if upload_files := inputs.pop(UPLOAD_FILES_KEY, None):
            upload_files_ids = upload_files.values()
            upload_files_names = []
            for file_id in upload_files_ids:
                file_data = UploadFiles().get_file_by_id(file_id)
                upload_files_names.append(file_data['name'] + file_data['extension'])
            inputs[get_language_content('upload_files')] = upload_files_names
        node_exec_data['inputs'] = inputs
    if outputs := node_exec_data.get('outputs'):
        node_exec_data['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
        if node.data['type'] in ['llm', 'agent']:
            node_exec_data['outputs_md'] = get_first_variable_value(create_variable_from_dict(outputs))
        elif node.data['type'] in ['recursive_task_generation', 'recursive_task_execution']:
            task_dict = json.loads(get_first_variable_value(create_variable_from_dict(outputs)))
            node_exec_data['outputs_md'] = create_recursive_task_category_from_dict(task_dict).to_markdown()
        elif node.data['type'] in ['skill', 'custom_code', 'end']:
            file_list = extract_file_list_from_skill_output(node_exec_data['outputs'], node.data['output'].to_dict())
            # skill_output = node_exec_data['outputs']
            # storage_url = f"{os.getenv('STORAGE_URL', '')}/file"
            # output_vars = create_variable_from_dict(node.data['output'].to_dict())
            # file_vars = output_vars.extract_file_variables()
            # for var in file_vars.properties.values():
            #     if var.name in skill_output:
            #         file_path = skill_output[var.name]
            #         if file_path:
            #             if not file_path.startswith('/'):
            #                 file_path = '/' + file_path
            #             file_name = file_path.split('/')[-1]
            #             full_path = f"{storage_url}{file_path}"
            #             file_list.append({
            #                 "file_name": file_name,
            #                 "file_path": full_path
            #             })
            node_exec_data['file_list'] = file_list
    
    queue_data = {
        'user_id': user_id,
        'type': 'workflow_run_debug', 
        'data': {
            'app_id': app_id,
            'workflow_id': workflow_id,
            'app_run_id': app_run_id,
            'type': run_type,
            'level': level,
            'status': status,
            'error': error,
            'completed_steps': completed_steps,
            'actual_completed_steps': actual_completed_steps,
            'need_human_confirm': need_human_confirm,
            'elapsed_time': elapsed_time,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'embedding_tokens': embedding_tokens,
            'reranking_tokens': reranking_tokens,
            'total_steps': total_steps,
            'created_time': created_time,
            'finished_time': finished_time,
            'node_exec_data': {
                'node_exec_id': node_exec_id,
                'parent_exec_id': parent_exec_id,
                'first_task_exec_id': first_task_exec_id,
                'level': level,
                'edge_id': edge.id if edge else None,
                'pre_node_id': edge.source_node_id if edge else None,
                'node_id': node.id,
                'node_type': node.data['type'],
                'node_name': node.data['title'],
                **node_exec_data
            }
        }
    }
    push_to_websocket_queue(queue_data)
    logger.info(f"Debug message pushed for run:{app_run_id} node:{node.id}:{node.data['type']}:{node.data['title']} exec_id:{node_exec_id} data:{queue_data} queue_length:{get_websocket_queue_length()}")
    
def push_workflow_progress_message(
    app_user_id: int, 
    user_id: int, 
    app_id: int, 
    app_name: str, 
    icon: str, 
    icon_background: str, 
    workflow_id: int, 
    app_run_id: int, 
    run_type: int, 
    run_name: str,
    run_status: int, 
    created_time: Optional[datetime], 
    total_steps: int, 
    elapsed_time: float, 
    completed_steps: int,
    need_human_confirm: int
):
    """
    Pushes a workflow progress message to the websocket queue for the specified users.
    Args:
        app_user_id (int): The ID of the application user.
        user_id (int): The ID of the user.
        app_id (int): The ID of the application.
        app_name (str): The name of the application.
        icon (str): The icon URL of the application.
        icon_background (str): The background color of the icon.
        workflow_id (int): The ID of the workflow.
        app_run_id (int): The ID of the application run.
        run_type (int): The type of the run.
        run_name (str): The name of the run.
        run_status (int): The status of the run.
        created_time (Optional[datetime]): The creation time of the run.
        total_steps (int): The total number of steps in the workflow.
        elapsed_time (float): The elapsed time of the run in seconds.
        completed_steps (int): The number of completed steps in the workflow.
    Returns:
        None
    """
    user_ids = list(set([app_user_id, user_id]))
    for user_id in user_ids:
        queue_data = {
            'user_id': user_id,
            'type': 'workflow_run_progress',
            'data': {
                'app_id': app_id,
                'app_name': app_name,
                'icon': icon,
                'icon_background': icon_background,
                'workflow_id': workflow_id,
                'app_run_id': app_run_id,
                'type': run_type,
                'run_name': run_name,
                'status': run_status,
                'created_time': created_time,
                'elapsed_time': elapsed_time,
                'completed_progress': f"{int((completed_steps / total_steps) * 100)}%",
                'need_human_confirm': need_human_confirm
            }
        }
        push_to_websocket_queue(queue_data)
        logger.info(f"Progress message pushed for user_id:{user_id} run:{app_run_id} data:{queue_data} queue_length:{get_websocket_queue_length()}")

def push_human_confirm_message(
    user_id: int,
    app_id: int,
    app_name: str,
    icon: str,
    icon_background: str,
    workflow_id: int,
    app_run_id: int,
    run_type:int,
    run_name: str,
    edge: Optional[Edge],
    node: Node,
    exec_id: int,
    run_status: int = 2,
    parent_exec_id: int = 0,
    first_task_exec_id: int = 0
):
    """
    Pushes a human confirmation message to the WebSocket message queue.

    :param user_id: The ID of the user.
    :param app_id: The ID of the app.
    :param app_name: The name of the app.
    :param icon: The icon of the app.
    :param icon_background: The icon background of the app.
    :param workflow_id: The ID of the workflow.
    :param app_run_id: The ID of the app run.
    :param run_type: The type of the run.
    :param run_name: The name of the run.
    :param edge: The edge object.
    :param node_id: The ID of the node.
    :param node_type: The type of the node.
    :param node_name: The name of the node.
    :param exec_id: The ID of the node execution record.
    :param run_status: The status of the run.
    :param parent_exec_id: The ID of the parent node execution record.
    :param first_task_exec_id: The ID of the first task execution record.
    """
    user_ids = [user_id] if run_type == 1 else app_node_user_relation.get_node_user_ids(app_run_id, node.id)
    if run_status == 4 and user_id not in user_ids:
        user_ids.append(user_id)
    for uid in user_ids:
        data = {
            'user_id': uid,
            'type': 'workflow_need_human_confirm',
            'data': {
                'app_id': app_id,
                'app_name': app_name,
                'icon': icon,
                'icon_background': icon_background,
                'workflow_id': workflow_id,
                'app_run_id': app_run_id,
                'type': run_type,
                'run_name': run_name,
                'node_exec_data': {
                    'node_exec_id': exec_id,
                    'level': edge.level,
                    'edge_id': edge.id if edge else None,
                    'node_id': node.id,
                    'node_type': node.data['type'],
                    'node_name': node.data['title'],
                    'parent_exec_id': parent_exec_id,
                    'first_task_exec_id': first_task_exec_id
                }
            }
        }
        push_to_websocket_queue(data)
        logger.info(f"Human confirm message pushed for user_id:{uid} run:{app_run_id} node:{node.id}:{node.data['type']}:{node.data['title']} exec_id:{exec_id} data:{data} queue_length:{get_websocket_queue_length()}")

def push_remove_human_confirm_message(
    user_id: int,
    app_id: int,
    workflow_id: int,
    app_run_id: int,
    exec_id: int
):
    """
    Pushes a remove human confirmation message to the WebSocket message queue.

    :param user_id: The ID of the user.
    :param app_id: The ID of the app.
    :param workflow_id: The ID of the workflow.
    :param app_run_id: The ID of the app run.
    :param exec_id: The ID of the node execution record.
    """
    data = {
        'user_id': user_id,
        'type': 'workflow_remove_human_confirm',
        'data': {
            'app_id': app_id,
            'workflow_id': workflow_id,
            'app_run_id': app_run_id,
            'node_exec_data': {
                'node_exec_id': exec_id
            }
        }
    }
    push_to_websocket_queue(data)
    logger.info(f"Remove human confirm message pushed for user_id:{user_id} run:{app_run_id} exec_id:{exec_id} data:{data} queue_length:{get_websocket_queue_length()}")

def task_delay_thread():
    """
    Thread to process runnable workflow runs and execute node tasks.
    """
    global running
    while running:
        runs = app_run.get_runnable_workflow_runs()  # Retrieve runnable workflow runs from the database
        # logger.debug(f"Runnable runs:{runs}")
        for run in runs:
            logger.info(f"Processing run id:{run['app_run_id']} type:{run['type']} level:{run['level']} completed_steps:{run['completed_steps']} actual_completed_steps:{run['actual_completed_steps']}")
            try:
                team_id = run['team_id']  # Get the team ID
                app_user_id = run['app_user_id']  # Get the app user ID
                user_id = run['user_id']  # Get the user ID
                app_id = run['app_id']  # Get the app ID
                workflow_id = run['workflow_id']  # Get the workflow ID
                app_run_id = run['app_run_id']  # Get the app run ID
                run_type = run['type']  # Get the run type
                level = run['level']  # Get the run level
                graph = create_graph_from_dict(run['graph'])  # Create a graph from the run's graph dictionary
                completed_edges = run['completed_edges'] if run['completed_edges'] else []  # Get completed edges
                skipped_edges = run['skipped_edges'] if run['skipped_edges'] else []  # Get skipped edges
                completed_steps = run['completed_steps']  # Get completed steps
                actual_completed_steps = run['actual_completed_steps']  # Get actual completed steps
                app_run_status = run['status']  # Get app run status
                need_human_confirm = run['need_human_confirm']  # Get need human confirm flag
                # Create a context object from the run's context dictionary
                context = create_context_from_dict(run['context']) if run['context'] else Context()
                edge_maps = graph.edges.build_edge_maps()  # Build edge maps for the graph
                current_level_edge_count = 0  # Initialize the current level edge count
                current_level_completed_edge_count = 0  # Initialize the current level completed edge count

                if level == 0: # start node
                    target_node = graph.nodes.nodes[0]  # Get the target node

                    # Prepare data for node execution record
                    node_exec_data = {
                        'workflow_id': workflow_id,
                        'user_id': user_id,
                        'app_run_id': app_run_id,
                        'type': run_type,
                        'node_id': target_node.id,
                        'node_type': target_node.data['type'],
                        'node_name': target_node.data['title'],
                        'node_graph': target_node.to_dict(),
                        'status': 2,  # Status indicating the node execution has started
                    }
                    exec_id = app_node_exec.insert(node_exec_data)  # Insert node execution record into the database

                    # Update app run status to indicate it is running and increment the level
                    update_app_run(app_run_id, {'level': level + 1, 'status': 2})

                    # Update target node with input variable
                    target_node.data['input'] = target_node.data['output'] = create_variable_from_dict(run['inputs'])
                    if (
                        (knowledge_base_mapping := run['knowledge_base_mapping'])
                        and (knowledge_base_mapping_for_input := knowledge_base_mapping.get('input'))
                        and (knowledge_base_mapping_for_upload_files := knowledge_base_mapping_for_input.get(UPLOAD_FILES_KEY))
                    ):
                        target_node.data['knowledge_base_mapping']['input'][UPLOAD_FILES_KEY] = knowledge_base_mapping_for_upload_files

                    # Execute the node asynchronously using Celery
                    create_celery_task(team_id, app_id, run['app_name'], run['icon'], run['icon_background'], workflow_id, app_user_id, user_id, app_run_id, run_type, run['run_name'], exec_id, None, target_node)

                    continue

                for edge in graph.edges.edges: # Iterate over edges starting from the completed steps
                    if edge.level != level: # Check if the source node level matches the run level
                        continue
                    current_level_edge_count += 1

                    if edge.id in completed_edges: # Check if the edge has been completed
                        current_level_completed_edge_count += 1
                        logger.debug(f"Edge already completed for run:{app_run_id} edge:{edge.id}")
                        continue

                    if edge.id in skipped_edges: # Check if the edge has been skipped
                        completed_edges.append(edge.id)
                        completed_steps += 1
                        update_app_run(app_run_id, {'completed_edges': completed_edges, 'completed_steps': completed_steps})
                        logger.debug(f"Edge already skipped for run:{app_run_id} edge:{edge.id}")
                        continue

                    logger.info(f"Processing edge:{edge.to_dict()}")
                    target_node = None # target node for the edge
                    all_predecessors_executed = True # Flag to indicate if all predecessors have been executed
                    parent_node = None # parent node for the executor node
                    task_level = 0 # Initialize the task level
                    task_data = None # task data
                    task_operation = '' # task operation
                    parent_exec_id = 0 # parent node execution ID

                    source_node_execution = app_node_exec.get_node_successful_execution(app_run_id, edge.source_node_id)
                    if not source_node_execution: # Check if the source node execution record exists
                        logger.error(f"Source node execution record not found for run {app_run_id} edge {edge.id}")
                        raise Exception(f"Source node execution record not found for run {app_run_id} edge {edge.id}")

                    if edge.is_logical_branch:
                        if not edge.condition_id or not source_node_execution['condition_id']: # Check if condition ID is missing
                            logger.error(f"Condition ID is missing run {app_run_id} edge {edge.id}")
                            raise Exception(f"Condition ID is missing run {app_run_id} edge {edge.id}")
                        if edge.condition_id != source_node_execution['condition_id']: # Check if condition IDs match
                            logger.debug(f"Condition IDs do not match for run:{app_run_id} edge:{edge.id}")
                            skipped_edges.append(edge.id)
                            # Skip all edges leading to the target node
                            if should_skip_node(edge.target_node_id, edge_maps, skipped_edges):
                                skip_edges_from_node(edge.target_node_id, edge_maps, skipped_edges)
                            else:
                                logger.debug(f"Can not skip node:{edge.target_node_id} as there are other edges leading to it not skipped")
                            # Update app run record to skip the edge
                            completed_edges.append(edge.id)
                            completed_steps += 1
                            update_app_run(app_run_id, {'completed_edges': completed_edges, 'skipped_edges': skipped_edges, 'completed_steps': completed_steps})
                            continue

                    # Get the task assignment level or task execution node
                    if edge.target_node_type == 'recursive_task_execution':
                        task_condition = app_node_exec.get_recursive_task_condition(app_run_id, level, edge.target_node_id)
                        logger.debug(f"Recursive task condition:{task_condition}")
                        task_level = task_condition['child_level']
                        task_operation = task_condition['status']
                        if task_operation == 'assign_task':
                            target_node = graph.nodes.get_node(edge.target_node_id)
                        else:
                            parent_node = graph.nodes.get_node(edge.target_node_id)
                            target_node = parent_node.data['executor_list'].get_node(task_condition['executor_id'])
                            if parent_node.data['import_to_knowledge_base'].get('output', False):
                                parent_output_mapping = parent_node.data['knowledge_base_mapping'].get('output', {})
                                if parent_output_mapping:
                                    target_node.data['import_to_knowledge_base'] = {'input': False, 'output': True}
                                    target_node.data['knowledge_base_mapping'] = {'input': {}, 'output': {'text': parent_output_mapping['output']}}
                            parent_output = create_variable_from_dict(task_condition['parent_output'])
                            task_data = json.loads(parent_output.properties['task'].value)
                            parent_exec_id = task_condition['first_execution_id']
                    else:
                        target_node = graph.nodes.get_node(edge.target_node_id)

                    if not target_node:  # Check if the target node exists
                        logger.error(f"Target node not found for run {app_run_id} edge {edge.id}")
                        raise Exception(f"Target node not found for run {app_run_id} edge {edge.id}")
                    target_node_dict = target_node.to_dict()  # Convert the target node to a dictionary

                    # Check if the target node waits for all predecessors
                    for e in graph.edges.edges:
                        if e.level >= level and e.id != edge.id and e.target_node_id == target_node.id and e.id not in skipped_edges and e.id not in completed_edges:
                            if e.level > level or app_node_exec.get_node_successful_execution(app_run_id, e.source_node_id):
                                logger.debug(f"Wait edge:{e.id} for target node:{target_node.id}")
                                all_predecessors_executed = False
                                break
                            else:
                                logger.debug(f"Predecessor not executed for edge:{e.id}")
                                skipped_edges.append(e.id)
                                update_app_run(app_run_id, {'skipped_edges': skipped_edges})
                    if not all_predecessors_executed:
                        completed_edges.append(edge.id)
                        completed_steps += 1
                        update_app_run(app_run_id, {'completed_edges': completed_edges, 'completed_steps': completed_steps})
                        continue

                    # Create a context object from the run's context dictionary and filter records based on the ancestor node IDs
                    ancestor_node_ids = graph.edges.get_all_ancestor_node_ids(parent_node.id if parent_node else target_node.id)
                    ancestor_context = context.get_related_records(level, ancestor_node_ids)
                    # logger.debug(f"Context for ancestor_node_ids:{ancestor_node_ids} records:{context.to_dict()}")

                    if app_run_status == 1:
                        update_app_run(app_run_id, {'status': 2}) # Update app run status to indicate it is running
                        app_run_status = 2

                    correct_llm_output = False # Flag to indicate if correct LLM output is found
                    if target_node.data['type'] in llm_correctable_node_types: # Check if the target node type is correctable
                        correct_llm_output_execution_id, last_llm_execution_id = app_node_exec.get_correct_llm_output_execution_ids(app_run_id, level, edge.id)
                        if correct_llm_output_execution_id and last_llm_execution_id:
                            correct_llm_output = True
                            exec_id = correct_llm_output_execution_id
                            logger.debug(f"Correct LLM output found for run:{app_run_id} edge:{edge.id} node:{target_node.id} exec_id:{exec_id}")
                            # Push remove human confirmation message
                            push_remove_human_confirm_message(user_id, app_id, workflow_id, app_run_id, last_llm_execution_id)

                    """
                    Status of the human confirmation node execution.
                    0: Non-human confirmation node
                    1: Initialize human confirmation node execution record
                    2: Waiting for human data supplementation
                    3: Human data supplemented, start running
                    """
                    human_node_run_status = 0
                    if target_node.data['type'] == 'human':
                        human_result = app_node_exec.get_human_node_exec(app_run_id, level, target_node.id)
                        if human_result:
                            if human_result['inputs']:
                                human_node_run_status = 3
                                exec_id = human_result['id']
                                target_node = create_node_from_dict(human_result['node_graph'])
                                target_node.data['input'] = target_node.data['output'] = create_variable_from_dict(human_result['inputs'])
                            else:
                                human_node_run_status = 2
                                exec_id = human_result['id']
                        else:
                            human_node_run_status = 1
                            need_human_confirm = 1
                            update_app_run(app_run_id, {'status': 1, 'need_human_confirm': 1}) # Update app run record to indicate human confirmation is needed
                        logger.debug(f"Human node run status:{human_node_run_status}")

                    if not (correct_llm_output or (target_node.data['type'] == 'human' and human_node_run_status != 1)):
                        # Prepare data for node execution record
                        need_human_confirm = 1 if target_node.data['type'] == 'human' else 0
                        node_exec_data = {
                            'workflow_id': workflow_id,
                            'user_id': user_id,
                            'app_run_id': app_run_id,
                            'type': run_type,
                            'level': level,
                            'child_level': task_level,
                            'edge_id': edge.id,
                            'pre_node_id': parent_node.id if parent_node else edge.source_node_id,
                            'node_id': target_node.id,
                            'node_type': target_node.data['type'],
                            'node_name': target_node.data['title'],
                            'node_graph': target_node_dict,
                            'status': 2,  # Status indicating the node execution has started
                            'need_human_confirm': need_human_confirm
                        }
                        exec_id = app_node_exec.insert(node_exec_data)  # Insert node execution record into the database

                    if target_node.data['type'] == 'human' and human_node_run_status == 1:
                        need_human_confirm = 1
                        # Push a workflow debug message to the WebSocket message queue
                        push_workflow_debug_message(user_id, app_id, workflow_id, app_run_id, run_type, level, edge, target_node, 1, None, completed_steps, actual_completed_steps, 1,
                            run['elapsed_time'], run['prompt_tokens'], run['completion_tokens'], run['total_tokens'], run['embedding_tokens'], run['reranking_tokens'],
                            run['total_steps'], run['created_time'], run['finished_time'], exec_id, 0, 0, {'status': 2, 'error': None, 'need_human_confirm': 1})
                        # Push human confirmation message to the WebSocket message queue
                        push_human_confirm_message(user_id, app_id, run['app_name'], run['icon'], run['icon_background'], workflow_id, app_run_id, run_type, run['run_name'], edge, target_node, exec_id)

                    # Execute the node asynchronously using Celery
                    if not (target_node.data['type'] == 'human' and human_node_run_status != 3):
                        create_celery_task(team_id, app_id, run['app_name'], run['icon'], run['icon_background'], workflow_id, app_user_id, user_id, app_run_id, run_type, run['run_name'],
                            exec_id, edge, target_node, task_level, task_data, task_operation, parent_exec_id, context, ancestor_context, correct_llm_output)

                        if not (correct_llm_output or target_node.data['type'] == 'end' or (task_operation == 'assign_task' and task_level > 0)):
                            # Push a workflow debug message to the WebSocket message queue
                            push_workflow_debug_message(user_id, app_id, workflow_id, app_run_id, run_type, level, edge, target_node, 1, None, completed_steps, actual_completed_steps, 0,
                                run['elapsed_time'], run['prompt_tokens'], run['completion_tokens'], run['total_tokens'], run['embedding_tokens'], run['reranking_tokens'],
                                run['total_steps'], run['created_time'], run['finished_time'], exec_id, parent_exec_id, 0, {'status': 2, 'error': None, 'need_human_confirm': 0})

                if current_level_edge_count == 0:
                    logger.error(f"No edges found for run:{app_run_id} level:{level}")
                    update_app_run(app_run_id, {'status': 4, 'error': f'No edges found for run:{app_run_id} level:{level}'})
                    continue

                if need_human_confirm == 0 and current_level_edge_count == current_level_completed_edge_count: # Check if all edges for the level have been completed
                    logger.debug(f"All edges completed for run:{app_run_id} level:{level}")
                    update_app_run(app_run_id, {'level': level + 1})
            except:
                logger.error(f"Error processing run:{app_run_id} {traceback.format_exc()}")

        time.sleep(1)

def task_callback_thread():
    """
    Handles task callbacks in a separate thread.
    """
    global running
    while running:
        for item in list(global_tasks):
            task, team_id, app_user_id, app_name, icon, icon_background, app_run_id, run_name, level, edge, target_node, context, exec_id, task_operation, parent_exec_id = item
            if task.ready():
                try:
                    context = context if context else Context()  # Create a new context object if it does not exist
                    result = task.get(timeout=task_timeout)  # Wait for the task to complete with a timeout
                    current_time = datetime.now()  # Current timestamp
                    logger.info(f"Task completed for run:{app_run_id} level:{level} node:{target_node.id}:{target_node.data['type']}:{target_node.data['title']} task_result:{result}")

                    run = app_run.get_running_app_run(app_run_id)  # Retrieve the running app run record
                    if not run:
                        logger.error(f"App run not found for run:{app_run_id}")
                        remove_task_cache(item)
                        continue
                    completed_edges = run['completed_edges'] if run['completed_edges'] else []  # Get completed edges
                    completed_steps = run['completed_steps']  # Get completed steps
                    actual_completed_steps = run['actual_completed_steps']  # Get actual completed steps

                    if result['status'] == 'success':
                        # Process successful execution result
                        inputs = result['data'].get('inputs', None)
                        task_id = result['data'].get('task_id', None)
                        outputs = result['data'].get('outputs', None)
                        elapsed_time = float(result['data'].get('elapsed_time', 0))
                        prompt_tokens = result['data'].get('prompt_tokens', 0)
                        completion_tokens = result['data'].get('completion_tokens', 0)
                        total_tokens = result['data'].get('total_tokens', 0)
                        embedding_tokens = result['data'].get('embedding_tokens', 0)
                        reranking_tokens = result['data'].get('reranking_tokens', 0)

                        if edge:
                            if inputs:
                                # Create input variable from input dictionary
                                input = create_variable_from_dict(inputs)
                                target_node.data['input'] = input  # Update target node with input variable
                            if outputs:
                                # Create output variable from result dictionary
                                output = create_variable_from_dict(outputs)
                                target_node.data['output'] = output  # Update target node with output variable
                            if not task_operation or (task_operation == 'assign_task' and not task_id):
                                completed_edges.append(edge.id)  # Add edge to completed edges
                                completed_steps += 1  # Increment completed steps
                                actual_completed_steps += 1  # Increment actual completed steps

                        if (not task_operation or (task_operation == 'assign_task' and not task_id)) and (target_node.data.get('input') or target_node.data.get('output')):
                            context.add_node(level, target_node)  # Add node to context

                        need_human_confirm = 1 if target_node.data['type'] != 'human' and \
                            not (task_operation == 'assign_task' and task_id) and \
                            target_node.data.get('manual_confirmation', False) else 0
                        node_exec_data = {'status': 3, 'error': None, 'need_human_confirm': need_human_confirm, 'finished_time': current_time, **result['data']}
                        app_run_data = {
                            'context': context.to_dict(),
                            'completed_edges': completed_edges,
                            'completed_steps': completed_steps,
                            'actual_completed_steps': actual_completed_steps,
                            'need_human_confirm': need_human_confirm,
                            'error': None,
                            'elapsed_time': float(run['elapsed_time']) + elapsed_time,
                            'prompt_tokens': run['prompt_tokens'] + prompt_tokens,
                            'completion_tokens': run['completion_tokens'] + completion_tokens,
                            'total_tokens': run['total_tokens'] + total_tokens,
                            'embedding_tokens': run['embedding_tokens'] + embedding_tokens,
                            'reranking_tokens': run['reranking_tokens'] + reranking_tokens
                        }
                        if target_node.data['type'] == 'end':
                            # If the target node is an end node, update the app run record with completion details
                            app_run_data['outputs'] = outputs
                            app_run_data['status'] = 3  # Status indicating the app run has completed successfully
                            app_run_data['finished_time'] = current_time
                            redis.lpush(f'app_run_{app_run_id}_result', json.dumps({'status': 'success', 'data': outputs}))
                            redis.expire(f'app_run_{app_run_id}_result', 1)
                        elif run['status'] == 2 and len(level_tasks[app_run_id][level]) == 1:  # Check if all tasks for the level have completed
                            app_run_data['status'] = 1  # Status indicating the app run is still running
                            app_run_data['need_correct_llm'] = 0 # Reset the need correct LLM flag
                            if not task_operation or (task_operation == 'assign_task' and not task_id):
                                app_run_data['level'] = level + 1 # Increment the level
                    else:
                        task_id = None
                        node_exec_data = {'status': 4, 'error': result['message'], 'need_human_confirm': 1}
                        app_run_data = {'status': 4, 'error': result['message'], 'need_human_confirm': 1}
                        redis.lpush(f'app_run_{app_run_id}_result', json.dumps({'status': 'failed', 'message': result['message']}))
                        redis.expire(f'app_run_{app_run_id}_result', 1)
                        if run['type'] == 2:
                            app_node_user_relation.add_node_user_relation(app_run_id, target_node.id, team_id, run['user_id'])

                    update_node_exec(exec_id, node_exec_data) # Update the node execution record with the new data
                    update_app_run(app_run_id, app_run_data) # Update the app run record with the new data

                    if target_node.data['type'] != 'human' and not (task_operation == 'assign_task' and task_id):
                        # External running status 1: Running 2: Running successfully 3: Running failed
                        run_status = app_run_data.get('status', run['status'])
                        run_status = run_status if run_status == 1 else run_status - 1

                        if task_operation == 'assign_task' and not task_id:
                            first_task_exec_id = app_node_exec.get_first_recursive_task_execution_id(app_run_id, level, target_node.id)
                            node_exec_data['elapsed_time'] = app_node_exec.get_task_total_data(app_run_id, level, target_node.id)['total_elapsed_time']
                        else:
                            first_task_exec_id = 0

                        # Push a workflow debug message to the WebSocket message queue
                        push_workflow_debug_message(run['user_id'], run['app_id'], run['workflow_id'], app_run_id, run['type'], level, edge, target_node, run_status,
                            app_run_data['error'], app_run_data.get('completed_steps', completed_steps), app_run_data.get('actual_completed_steps', actual_completed_steps), app_run_data['need_human_confirm'],
                            app_run_data.get('elapsed_time', run['elapsed_time']), app_run_data.get('prompt_tokens', run['prompt_tokens']),
                            app_run_data.get('completion_tokens', run['completion_tokens']), app_run_data.get('total_tokens', run['total_tokens']),
                            app_run_data.get('embedding_tokens', run['embedding_tokens']), app_run_data.get('reranking_tokens', run['reranking_tokens']), run['total_steps'],
                            run['created_time'], app_run_data.get('finished_time', run['finished_time']), exec_id, parent_exec_id, first_task_exec_id, node_exec_data)

                        # if not task_operation or (task_operation == 'assign_task' and not task_id):
                        # Push workflow progress websocket message
                        push_workflow_progress_message(app_user_id, run['user_id'], run['app_id'], app_name, icon, icon_background, run['workflow_id'], app_run_id, run['type'], run_name,
                            run_status, run['created_time'], run['total_steps'], app_run_data.get('elapsed_time', run['elapsed_time']), app_run_data.get('completed_steps', completed_steps),app_run_data['need_human_confirm'])

                        # Push a workflow need human confirm message to the WebSocket message queue
                        if (task_operation != 'assign_task' or (task_operation == 'assign_task' and not task_id)) and app_run_data['need_human_confirm'] == 1:
                            push_human_confirm_message(run['user_id'], run['app_id'], app_name, icon, icon_background, run['workflow_id'], app_run_id, run['type'], run_name, edge, target_node, 
                                exec_id, node_exec_data['status'], parent_exec_id, first_task_exec_id)
                except Exception as e:
                    logger.error(f"Error processing run:{app_run_id} {traceback.format_exc()}")
                    # Update records with failure status and error message if an exception occurred
                    redis.lpush(f'app_run_{app_run_id}_result', json.dumps({'status': 'failed', 'message': result['message']}))
                    redis.expire(f'app_run_{app_run_id}_result', 1)
                    update_app_run(app_run_id, {'status': 4, 'error': str(e), 'need_human_confirm': 1})
                    
                remove_task_cache(item)
                
        time.sleep(1)

if __name__ == '__main__':
    delay_thread = threading.Thread(target=task_delay_thread)
    delay_thread.start()
    
    callback_thread = threading.Thread(target=task_callback_thread)
    callback_thread.start()
    
    try:
        delay_thread.join()
        callback_thread.join()
    except KeyboardInterrupt:
        logger.debug("Stopping threads...")
        running = False
        delay_thread.join()
        callback_thread.join()
        logger.debug("Program exited gracefully")