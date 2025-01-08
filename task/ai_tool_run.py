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
from core.database.models import AppRuns, AIToolLLMRecords, Agents
from core.workflow.variables import create_object_variable_from_list
from core.helper import push_to_websocket_queue
from celery_app import run_llm_tool

logger = Logger.get_logger('ai_tool_run')

task_timeout = 60  # Timeout for Celery task execution
global_tasks = []  # List to store tasks
running = True  # Global flag to control thread loops

# Database models
app_run = AppRuns()
ai_tool_llm_records = AIToolLLMRecords()
agents = Agents()


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


def push_websocket_message(
        user_id: int,
        ai_tool_type: str,
        app_run_id: int,
        status: int,
        error: str,
        elapsed_time: float,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        created_time: datetime,
        finished_time: datetime,
        exec_id: int,
        ai_status: int,
        ai_error: str,
        outputs: Dict[str, Any],
        ai_elapsed_time: float,
        ai_prompt_tokens: int,
        ai_completion_tokens: int,
        ai_total_tokens: int,
        run_ai_tool_type,
        loop_id
):
    """
    Push messages to websocket.

    :param user_id: The ID of the user.
    :param ai_tool_type: Message Type.
    :param app_run_id: The ID of the app run.
    :param status: Execute status 0: Cannot execute 1: Can execute 2: Executing 3: Successfully executed 4: Failed to execute.
    :param error: Error message.
    :param elapsed_time: Elapsed time.
    :param prompt_tokens: Prompt tokens.
    :param completion_tokens: Completion tokens.
    :param total_tokens: Total tokens.
    :param created_time: Run created time.
    :param finished_time: Run finished time.
    :param exec_id: The ID of the ai tool llm records.
    :param ai_status: The status of the ai tool llm records.
    :param ai_error: The error of the ai tool llm records.
    :param outputs: The outputs of the ai tool llm records.
    :param ai_elapsed_time: Elapsed time.
    :param ai_prompt_tokens: Prompt tokens.
    :param ai_completion_tokens: Completion tokens.
    :param ai_total_tokens: Total tokens.
    :param run_ai_tool_type: Run AI tool type, identify the type of AI tool being run this time.
    :param loop_id: Loop ID, identifying the loop ID of this run.
    """
    if run_ai_tool_type == 1 and ai_tool_type == 'generate_agent_batch':
        data = {
            'user_id': user_id,
            'type': ai_tool_type,
            'data': {
                'app_run_id': app_run_id,
                'status': status,
                'error': error,
                'elapsed_time': elapsed_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'created_time': created_time,
                'finished_time': finished_time,
                'exec_data': {
                    'exec_id': exec_id,
                    'loop_id': loop_id,
                    'status': ai_status,
                    'error': ai_error,
                    'outputs': outputs,
                    'elapsed_time': ai_elapsed_time,
                    'prompt_tokens': ai_prompt_tokens,
                    'completion_tokens': ai_completion_tokens,
                    'total_tokens': ai_total_tokens,
                }
            }
        }
    else:
        data = {
            'user_id': user_id,
            'type': ai_tool_type,
            'data': {
                'app_run_id': app_run_id,
                'status': status,
                'error': error,
                'elapsed_time': elapsed_time,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'created_time': created_time,
                'finished_time': finished_time,
                'exec_data': {
                    'exec_id': exec_id,
                    'status': ai_status,
                    'error': ai_error,
                    'outputs': outputs,
                    'elapsed_time': ai_elapsed_time,
                    'prompt_tokens': ai_prompt_tokens,
                    'completion_tokens': ai_completion_tokens,
                    'total_tokens': ai_total_tokens,
                }
            }
        }
    push_to_websocket_queue(data)
    logger.info(
        f"Push results generated through AI:{user_id} run:{app_run_id} ai_tool_type:{ai_tool_type}:{status}:{error} exec_id:{exec_id} data:{data}")


def create_celery_task(
    # team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output
    app_run_id: int,
    id: int,
    ai_tool_type: str,
    loop_id: int,
    loop_limit: int,
    loop_count: int,
    run_ai_tool_type: int,
    prompt_dict: Optional[Dict[str, Any]] = None,
    return_json: bool = False,
    correct_llm_output: bool = False,
):
    """
    Creates a Celery task to execute a node asynchronously.

    :param app_run_id: The name of the app run.
    :param loop_limit: Number of cycles.
    :param loop_count: Number of cycles.
    :param loop_id: id of cycles.
    :param run_ai_tool_type: AI tool type 0: Regular APP (not an AI tool).
    :param prompt_dict: cue word.
    :param return_json: Whether to return a JSON string.
    :param correct_llm_output: Flag to indicate if correct LLM output is found.
    :param id: The ID of the ai_tool_llm_records.
    :param ai_tool_type: The ai_tool_type of the app run.
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
    global_tasks.append((task, team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output, id, ai_tool_type, loop_count, loop_id, run_ai_tool_type, loop_limit))
    logger.info(f"Task added for run:{app_run_id} id:{id} task_id:{task.id}")


def remove_task_cache(item):
    """
    Removes a task from the global tasks list and level tasks dictionary.

    :param item: The task item to remove.
    """
    global_tasks.remove(item)  # Remove task from global tasks list


def task_delay_thread():
    """
    Thread to process can run AI and execute.
    """
    global running
    while running:
        runs = ai_tool_llm_records.get_pending_ai_tool_tasks()  # Retrieve runnable records from the database
        for run in runs:
            logger.info(f"Processing run id:{run['app_run_id']} ai_tool_llm_records_table_id:{run['id']} ai_tool_type:{run['ai_tool_type']} id:{run['id']}")
            try:
                app_run_id = run['app_run_id']  # Get the app run ID
                id = run['id']  # AI Tool Llm Records Table ID
                ai_tool_type = run['ai_tool_type']  # AI tool type 0: Regular APP (not an AI tool) 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator
                inputs = run['inputs']  # system prompt + user prompt
                correct_prompt = run['correct_prompt'] # Prompt for correcting LLM output results
                # run_type  Run type 1: First generation 2: Regeneration 3: AI correction 4: Batch generation
                if run['run_type'] == 1:
                    run_type = 'first'
                elif run['run_type'] == 2:
                    run_type = 'again'
                elif run['run_type'] == 3:
                    run_type = 'correct'
                else:
                    run_type = 'batch'

                if ai_tool_type == 1:
                    return_json = True
                    ai_tool_type = 'generate_agent_'+run_type
                elif ai_tool_type == 2:
                    return_json = True
                    ai_tool_type = 'generate_skill_'+run_type
                elif ai_tool_type == 3:
                    return_json = False
                    ai_tool_type = 'generate_meeting_summary_'+run_type
                elif ai_tool_type == 4:
                    return_json = True
                    ai_tool_type = 'generate_meeting_action_items_'+run_type
                else:
                    return_json = True

                if inputs is None:
                    prompt_dict = correct_prompt
                    correct_llm_output = True
                else:
                    prompt_dict = inputs
                    correct_llm_output = False
                # if run['loop_count'] > 0:
                    # ai_tool_status = ai_tool_llm_records.get_search_record(app_run_id, run['ai_tool_type'], 4, run['loop_id'])
                    # if ai_tool_status is None:
                    #     inputs_new = ai_tool_llm_records.inputs_append_history_outputs(app_run_id, run['loop_id'])
                    #     ai_tool_llm_records.initialize_execution_record(app_run_id, run['ai_tool_type'], 4, run['loop_id'], run['loop_count'], inputs_new, run['correct_prompt'])
                # loop_count = run['loop_count']
                # if loop_count > 0:
                #     loop_count = max(loop_count - 1, 0)
                update_app_run(app_run_id, {'status': 2})
                update_ai_run(id, {'status': 2})

                create_celery_task(app_run_id, id, ai_tool_type, run['loop_id'], run['loop_limit'], run['loop_count'], run['ai_tool_type'], prompt_dict, return_json, correct_llm_output)
                logger.debug(f"Task assigned completed and the App Run table ID is:{app_run_id}")
                continue

            except:
                logger.error(f"Error processing run:{run['app_run_id']} {traceback.format_exc()}")
        
        time.sleep(1)


def task_callback_thread():
    """
    Handles task callbacks in a separate thread.
    """
    global running
    while running:
        for item in list(global_tasks):
            task, team_id, user_id, app_run_id, prompt_dict, return_json, correct_llm_output, id, ai_tool_type, loop_count, loop_id, run_ai_tool_type, loop_limit = item
            if task.ready():
                try:
                    result = task.get(timeout=task_timeout)  # Wait for the task to complete with a timeout
                    logger.info(f"Task completed for run:{app_run_id} id:{id} task_result:{result}")
                    run = app_run.get_running_app_run_ai(app_run_id)  # Retrieve the running app run record
                    # ai_tool_llm = ai_tool_llm_records.get_ai_tool_llm_record(app_run_id)
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

                        if run_ai_tool_type == 1 and ai_tool_type == 'generate_agent_batch':
                            value_str = result['data']['outputs']['value']
                            json_load_value = json.loads(value_str)
                            return_agent = agents.create_agent_with_configs(
                                data=json_load_value,
                                user_id=user_id,
                                team_id=team_id
                            )
                            if return_agent['status'] == 1:
                                logger.info(f"Batch generate agent returns:{return_agent}")
                                result['data']['outputs']['id'] = return_agent['app_id']
                            else:
                                logger.error(f"ERROR Batch generate agent returns:{return_agent}")
                        elif run_ai_tool_type == 4:
                            value_str = result['data']['outputs']['value']
                            json_load_value = json.loads(value_str)
                            json_load_value = [json_load_value]
                            test_var_obj = create_object_variable_from_list(
                                data=json_load_value,
                                name="inputs",
                                display_name="Inptus"
                            )
                            test_var_obj = test_var_obj.to_dict()
                            result['data']['outputs']['value'] = json.dumps(test_var_obj, ensure_ascii=False)

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

                        app_run_elapsed_time = float(run['elapsed_time']) + elapsed_time
                        app_run_prompt_tokens = run['prompt_tokens'] + prompt_tokens
                        app_run_completion_tokens = run['completion_tokens'] + completion_tokens
                        app_run_total_tokens = run['total_tokens'] + total_tokens
                        if loop_count > 0:
                            inputs_new = ai_tool_llm_records.inputs_append_history_outputs(app_run_id, loop_id)
                            ai_tool_llm_records.initialize_execution_record(app_run_id, run_ai_tool_type, 4, loop_id, loop_limit, loop_count, inputs_new)
                            app_run_data = {
                                'status': 1
                            }
                        else:
                            app_run_data = {
                                'status': 3,
                                'outputs': result['data']['outputs'],
                                'elapsed_time': app_run_elapsed_time,
                                'prompt_tokens': app_run_prompt_tokens,
                                'completion_tokens': app_run_completion_tokens,
                                'total_tokens': app_run_total_tokens,
                                'finished_time': end_time
                            }
                        update_app_run(app_run_id, app_run_data)

                        push_websocket_message(user_id, ai_tool_type, app_run_id, 3, '', app_run_elapsed_time, app_run_prompt_tokens, app_run_completion_tokens, app_run_total_tokens, run['created_time'], end_time, id, 3, '', result['data']['outputs'], elapsed_time, prompt_tokens, completion_tokens, total_tokens, run_ai_tool_type, loop_id)
                    else:
                        update_app_run(app_run_id, {'status': 4, 'error': result['message']})
                        update_ai_run(id, {'status': 4, 'error': result['message']})
                        end_time = time.time()
                        end_time = datetime.fromtimestamp(end_time)
                        push_websocket_message(user_id, ai_tool_type, app_run_id, 4, result['message'], 0, 0, 0, 0, run['created_time'], end_time, id, 4, result['message'], {}, 0, 0, 0, 0, run_ai_tool_type, loop_id)
                except Exception as e:
                    logger.error(f"Error processing run:{app_run_id} {traceback.format_exc()}")
                    # Update records with failure status and error message if an exception occurred
                    update_app_run(app_run_id, {'status': 4, 'error': str(e), 'need_human_confirm': 1})
                    end_time = time.time()
                    end_time = datetime.fromtimestamp(end_time)
                    push_websocket_message(user_id, ai_tool_type, app_run_id, 4, str(e), 0, 0, 0, 0, end_time, end_time, id, 4, str(e), {}, 0, 0, 0, 0, 0, 0)

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