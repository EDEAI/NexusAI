from fastapi import APIRouter
from api.utils.common import *
from api.utils.jwt import *
from api.schema.node import *
from core.database.models import (AppNodeExecutions, AppRuns, UploadFiles)
from core.workflow import (
    create_variable_from_dict,
    create_context_from_dict,
    flatten_variable_with_values,
    replace_value_in_variable_with_new_value
)
from core.workflow.nodes import create_node_from_dict, llm_correctable_node_types, UPLOAD_FILES_KEY
from languages import get_language_content
from datetime import datetime
import json
from copy import deepcopy

from celery_app import import_output_variable_to_knowledge_base

router = APIRouter()
node_model = AppNodeExecutions()
app_run_model = AppRuns()

@router.get("/backlog_list", response_model = ResBackListSchema)
async def backlog_list(page: int = 1, page_size: int = 10, need_human_confirm: int = None, userinfo: TokenData = Depends(get_current_user)):
    """
    backlog list

    """
    user_id = userinfo.uid
    # team_id = userinfo.team_id
    # role = userinfo.role

    result = app_run_model.get_backlogs_list({"user_id": user_id, "page_size": page_size, "page": page, "need_human_confirm": need_human_confirm})
    # print(result)
    # if result['list']:
    #     for item in result['list']:
    #         app_node = node_model.select_one(
    #             columns=['node_name', 'id AS exec_id'],
    #             conditions=[{'column': 'node_id', 'value': item['node_id']}]
    #         )
    #         item['node_name'] = app_node['node_name']
    #         item['exec_id'] = app_node['exec_id']
            # if app_node['node_graph']:
            #     app_node['node_graph'] = json.dumps(app_node['node_graph'])
            #     result_dict = json.loads(app_node['node_graph'])
            #     item['node_title'] = result_dict['data']['title']
            #     item['node_desc'] = result_dict['data']['desc']

    return response_success(result)


@router.get("/node_info/{exec_id}", response_model = ResNodeInfoSchema)
async def get_node_by_id(exec_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    node info

    """
    uid = userinfo.uid
    team_id = userinfo.team_id

    result = node_model.get_node_info(exec_id, uid, team_id)
    if result["status"] != 1:
        return response_error(result["message"])
    
    if inputs := result['data'].get('inputs'):
        inputs = create_variable_from_dict(inputs)
        inputs = flatten_variable_with_values(inputs)
        if upload_files := inputs.pop(UPLOAD_FILES_KEY, None):
            upload_files_ids = upload_files.values()
            upload_files_names = []
            for file_id in upload_files_ids:
                file_data = UploadFiles().get_file_by_id(file_id)
                upload_files_names.append(file_data['name'] + file_data['extension'])
            inputs[get_language_content('upload_files')] = upload_files_names
        result['data']['inputs'] = inputs
    if outputs := result['data'].get('outputs'):
        outputs = create_variable_from_dict(outputs)
        result['data']['outputs'] = flatten_variable_with_values(outputs)

    if result["data"]["correct_prompt"]:
        result["data"]["correct_llm_history"] = node_model.get_correct_llm_history(result["data"]["app_run_id"], result["data"]["level"], result["data"]["edge_id"])
    else:
        result["data"]["correct_llm_history"] = []
    
    prompt_data = []
    if result["data"]["model_data"]:
        messages = result["data"]["model_data"]["messages"]
        for message in messages:
            prompt_data.append({message[0]: message[1]["value"]})
    result["data"]["prompt_data"] = prompt_data
    result["data"].pop("model_data")

    return response_success(result["data"])


@router.put("/node_update/{exec_id}", response_model = ResNodeUpdateSchema)
async def node_update(exec_id: int, data: ReqNodeUpdateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    node update

    operation: 0: confirm 1: correct llm ouput
    correct_prompt: operation = 1 is required
    outputs: confirm node is required
    inputs: human confirm node is required

    """
    uid = userinfo.uid
    team_id = userinfo.team_id

    if exec_id <= 0:
        return response_error("exec_id is required")

    result = node_model.get_node_info(exec_id, uid, team_id)
    if result["status"] != 1:
        return response_error(result["message"])

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    app_run_update_data = {}
    execute_celery_task = False

    node_info = result["data"]

    if node_info['status'] == 4:
        exec_id = node_info['exec_id']

        node_update_res = node_model.update({"column": "id", "value": exec_id}, {"correct_output": 1})
        if not node_update_res:
            return response_error("node update error")

        if not node_model.has_human_confirm_node(node_info['app_run_id']):
            app_run_update_res = app_run_model.update({"column": "id", "value": node_info['app_run_id']}, {"status": 1, "need_human_confirm": 0})
            if not app_run_update_res:
                return response_error("app run update error")

        return response_success({"exec_id": exec_id})
    else:
        if node_info['node_type'] == "human":
            if not data.inputs:
                return response_error("input is required")

            exec_id = node_info['exec_id']
            try:
                human_input_dict = data.inputs
                knowledge_base_mapping = data.knowledge_base_mapping
                human_input_var = create_variable_from_dict(human_input_dict)

                human_node_for_context = create_node_from_dict(node_info['node_graph'])
                human_node_for_node_update = deepcopy(human_node_for_context)
                human_node_for_context.data['input'] = human_node_for_context.data['output'] = human_input_var
                context = create_context_from_dict(node_info['context'])
                context.add_node(node_info['level'], human_node_for_context)
                human_node_for_node_update.data['knowledge_base_mapping'] = knowledge_base_mapping if knowledge_base_mapping else {}
                app_run_update_data['context'] = context.to_dict()

                # update node
                node_update_data = {
                    "node_graph": human_node_for_node_update.to_dict(),
                    "inputs": human_input_dict,
                    "outputs": human_input_dict,
                    "need_human_confirm": 0,
                    "finished_time": current_time
                }
                node_update_res = node_model.update({"column": "id", "value": exec_id}, node_update_data)
                if not node_update_res:
                    return response_error("node update error")

            except:
                return response_error("node update except")
        else:
            if node_info['node_type'] in llm_correctable_node_types and data.operation == 1:
                if not data.correct_prompt:
                    return response_error("correct_prompt is required")

                if not node_info['task_id']:
                    if node_info['completed_steps'] > 0:
                        app_run_update_data['completed_steps'] = node_info['completed_steps'] - 1
                        app_run_update_data['actual_completed_steps'] = node_info['actual_completed_steps'] - 1

                    if node_info['app_run_status'] == 1 and node_info['app_run_level'] > 0:
                        app_run_update_data['level'] = node_info['app_run_level'] - 1

                    if node_info['completed_edges']:
                        completed_edges = node_info['completed_edges']
                        if node_info['edge_id'] in completed_edges:
                            completed_edges.remove(node_info['edge_id'])
                        app_run_update_data['completed_edges'] = completed_edges
                    
                app_run_update_data['need_correct_llm'] = 1

                new_node_data = {
                    "workflow_id": node_info['workflow_id'],
                    "app_run_id": node_info['app_run_id'],
                    "user_id": node_info['exec_user_id'],
                    "type": node_info['type'],
                    "level": node_info['level'],
                    "child_level": node_info['child_level'],
                    "edge_id": node_info['edge_id'],
                    "pre_node_id": node_info['pre_node_id'],
                    "node_id": node_info['node_id'],
                    "node_type": node_info['node_type'],
                    "node_name": node_info['node_name'],
                    "node_graph": node_info['node_graph'],
                    "correct_prompt": data.correct_prompt,
                    "status": 2,
                }
            else:
                if not data.outputs:
                    return response_error("outputs is required")
                
                variable = create_variable_from_dict(node_info['outputs'])
                variable_dict = variable.to_dict()
                replace_value_in_variable_with_new_value(variable, data.outputs)
                
                node_for_context = create_node_from_dict(node_info['node_graph'])
                node_for_context_updated = deepcopy(node_for_context)
                node_for_importing_to_kb = deepcopy(node_for_context)
                node_for_context.data['output'] = variable
                context = create_context_from_dict(node_info['context'])
                context.add_node(node_info['level'], node_for_context)
                app_run_update_data['context'] = context.to_dict()

                new_node_data = {
                    "workflow_id": node_info['workflow_id'],
                    "app_run_id": node_info['app_run_id'],
                    "user_id": node_info['exec_user_id'],
                    "type": node_info['type'],
                    "level": node_info['level'],
                    "child_level": node_info['child_level'],
                    "edge_id": node_info['edge_id'],
                    "pre_node_id": node_info['pre_node_id'],
                    "node_id": node_info['node_id'],
                    "node_type": node_info['node_type'],
                    "node_name": node_info['node_name'],
                    "node_graph": node_for_context_updated.to_dict(),
                    "inputs": node_info['inputs'],
                    "model_data": node_info['model_data'],
                    "task_id": node_info['task_id'],
                    "status": node_info['status'],
                    "condition_id": node_info['condition_id'],
                    "outputs": variable_dict,
                    "output_type": node_info['output_type'],
                    "elapsed_time": node_info['elapsed_time'],
                    "prompt_tokens": node_info['prompt_tokens'],
                    "completion_tokens": node_info['completion_tokens'],
                    "total_tokens": node_info['total_tokens'],
                    "embedding_tokens": node_info['embedding_tokens'],
                    "reranking_tokens": node_info['reranking_tokens'],
                    "created_time": node_info['created_time'],
                    "finished_time": node_info['finished_time']
                }
                if node_info['correct_prompt']:
                    new_node_data['correct_prompt'] = node_info['correct_prompt']

            if new_node_data:
                try:
                    # copy node
                    exec_id = node_model.insert(new_node_data)
                    if not exec_id:
                        return response_error("node insert error")

                except:
                    return response_error("node insert except")

                org_node_update_res = node_model.update({"column": "id", "value": node_info['exec_id']}, {"correct_output": 1})
                if not org_node_update_res:
                    return response_error("org node update error")
                
                if (
                    not data.operation
                    and node_info['node_type'] in llm_correctable_node_types + ['recursive_task_execution']
                    and node_for_context.data['import_to_knowledge_base'].get('output', False)
                ):
                    import_output_variable_to_knowledge_base.delay(
                        node_for_importing_to_kb.to_dict(),
                        variable_dict,
                        node_for_context.data['knowledge_base_mapping'].get('output', {}),
                        node_info['app_run_id'],
                        exec_id
                    )
                    execute_celery_task = True

        if not execute_celery_task and not node_model.has_human_confirm_node(node_info['app_run_id']):
            app_run_update_data['need_human_confirm'] = 0
            
        if app_run_update_data:
            app_run_update_res = app_run_model.update({"column": "id", "value": node_info['app_run_id']}, app_run_update_data)
            if not app_run_update_res:
                return response_error("app run update error")
            
        return response_success({"exec_id": exec_id})