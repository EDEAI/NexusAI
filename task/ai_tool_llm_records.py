"""
This script executes application prompt words using AI
"""
import json, os, sys, time, threading, traceback
os.environ['DATABASE_AUTO_COMMIT'] = 'True'
from datetime import datetime
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent))

from typing import Dict, Optional, Any
from log import Logger
from core.database import redis
from core.database.models import AppRuns, AppNodeExecutions, AppNodeUserRelation, UploadFiles, AIToolLLMRecords
from core.workflow import *
from core.workflow.nodes import *
from celery_app import run_workflow_node
from core.helper import push_to_websocket_queue, get_websocket_queue_length
from languages import get_language_content
from celery_app import run_llm_tool

logger = Logger.get_logger('ai_tool_llm_records_run')

task_timeout = 60  # Timeout for Celery task execution
global_tasks = [] # List to store tasks
running = True  # Global flag to control thread loops
level_tasks = {}  # Dictionary to store tasks status for each level

# Database models
app_run = AppRuns()
ai_tool_llm_records = AIToolLLMRecords()
# app_node_exec = AppNodeExecutions()
# app_node_user_relation = AppNodeUserRelation()

def update_app_run(app_run_id: int, data: dict) -> bool:
    """
    Updates an app run record in the database.

    :param app_run_id: The ID of the app run record.
    :param data: A dictionary containing the data to update.
    :return: True if the record was updated successfully, False otherwise.
    """
    return app_run.update(conditions={'column': 'id', 'value': app_run_id}, data=data)

def update_ai_run(id: int, data: dict) -> bool:
    """
    Updates an app run record in the database.

    :param id: The ID of the ai record.
    :param data: A dictionary containing the data to update.
    :return: True if the record was updated successfully, False otherwise.
    """
    return ai_tool_llm_records.update(conditions={'column': 'id', 'value': id}, data=data)

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
    # team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output
    app_run_id: int,
    id: int,
    prompt_dict: Optional[Dict[str, Any]] = None,
    return_json: bool = False,
    correct_llm_output: bool = False
):
    """
    Creates a Celery task to execute a node asynchronously.

    :param app_run_id: The name of the app run.
    :param prompt_dict: cue word.
    :param return_json: Whether to return a JSON string.
    :param correct_llm_output: Flag to indicate if correct LLM output is found.
    :param id: The ID of the ai_tool_llm_records.

    """
    app_run_info = app_run.get_search_app_run_team_id(app_run_id)
    team_id = app_run_info['team_id']
    user_id = app_run_info['user_id']
    task = run_llm_tool.delay(
        team_id=team_id,
        user_id=user_id,
        app_run_id=app_run_id,
        prompt_dict=prompt_dict,
        return_json=return_json,
        correct_llm_output=correct_llm_output
    )
    # Add task to global tasks list
    global_tasks.append((task, team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output, id))
    logger.info(f"Task added for run:{app_run_id} id:{id} task_id:{task.id}")

def remove_task_cache(item):
    """
    Removes a task from the global tasks list and level tasks dictionary.

    :param item: The task item to remove.
    """
    global_tasks.remove(item)  # Remove task from global tasks list

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
    completed_steps: int
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
    Thread to process can run AI and execute.
    """
    global running
    while running:
        runs = ai_tool_llm_records.get_pending_ai_tool_tasks()  # Retrieve runnable records from the database
        # print(runs)
        # exit()
        for run in runs:
            logger.info(f"Processing run id:{run['app_run_id']} ai_tool_llm_records_table_id:{run['id']} ai_tool_type:{run['ai_tool_type']} id:{run['id']}")
            try:
                # team_id = AppRuns().get_search_app_run_team_id(run['app_run_id'])  # Get the team ID
                # user_id = run['user_id']  # Get the user ID
                app_run_id = run['app_run_id']  # Get the app run ID
                id = run['id']  # AI Tool Llm Records Table ID
                ai_tool_type = run['ai_tool_type']  # AI tool type 0: Regular APP (not an AI tool) 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator
                inputs = run['inputs']  # system prompt + user prompt
                correct_prompt = run['correct_prompt'] # Prompt for correcting LLM output results
                if ai_tool_type == 1:
                    return_json = True
                elif ai_tool_type == 2:
                    return_json = True
                elif ai_tool_type == 3:
                    return_json = False
                elif ai_tool_type == 4:
                    return_json = True
                else:
                    return_json = True

                if inputs is None:
                    prompt_dict = correct_prompt
                    correct_llm_output = True
                else:
                    prompt_dict = inputs
                    correct_llm_output = False

                update_app_run(app_run_id, {'status': 2})
                update_ai_run(id, {'status': 2})

                create_celery_task(app_run_id, id, prompt_dict, return_json, correct_llm_output)
                logger.debug(f"Task assigned completed and the App Run table ID is:{app_run_id}")
                continue
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
            task, team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output, id = item
            if task.ready():
                try:
                    result = task.get(timeout=task_timeout)  # Wait for the task to complete with a timeout
                    logger.info(f"Task completed for run:{app_run_id} id:{id} task_result:{result}")
                    run = app_run.get_running_app_run_ai(app_run_id)  # Retrieve the running app run record
                    if not run:
                        logger.error(f"App run not found for run:{app_run_id}")
                        remove_task_cache(item)
                        continue

                    if result['status'] == 'success':
                        elapsed_time = float(result['data'].get('elapsed_time', 0))
                        prompt_tokens = result['data'].get('prompt_tokens', 0)
                        completion_tokens = result['data'].get('completion_tokens', 0)
                        total_tokens = result['data'].get('total_tokens', 0)

                        end_time = time.time()
                        end_time = datetime.fromtimestamp(end_time)
                        app_run_data = {
                            'status': 3,
                            'outputs': result['data']['outputs'],
                            'elapsed_time': float(run['elapsed_time']) + elapsed_time,
                            'prompt_tokens': run['prompt_tokens'] + prompt_tokens,
                            'completion_tokens': run['completion_tokens'] + completion_tokens,
                            'total_tokens': run['total_tokens'] + total_tokens,
                            'finished_time': end_time
                        }
                        update_app_run(app_run_id, app_run_data)
                        app_ai_run_data = {
                            'status': 3,
                            'model_data': result['data']['model_data'],
                            'outputs': result['data']['outputs'],
                            'elapsed_time': elapsed_time,
                            'prompt_tokens': prompt_tokens,
                            'completion_tokens': completion_tokens,
                            'total_tokens': total_tokens,
                            'finished_time': end_time
                        }
                        update_ai_run(id, app_ai_run_data)
                        redis.lpush(f'app_run_{app_run_id}_result', json.dumps({'status': result['message'], 'data': result['data']['outputs']}))
                        redis.expire(f'app_run_{app_run_id}_result', 1)
                    else:
                        update_app_run(app_run_id, {'status': 4, 'error': result['message']})
                        update_ai_run(id, {'status': 4, 'error': result['message']})
                        redis.lpush(f'app_run_{app_run_id}_result', json.dumps({'status': result['message'], 'data': result['data']['outputs']}))
                        redis.expire(f'app_run_{app_run_id}_result', 1)
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