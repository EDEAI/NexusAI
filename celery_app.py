import os, json

os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from datetime import datetime
from typing import List, Dict, Any, Literal, Optional

from celery import Celery
from langchain_core.documents import Document

from config import settings
from core.database.models import Agents, AppNodeExecutions, AppRuns, Apps, CustomTools, Datasets, UploadFiles, Workflows

from core.dataset import DatasetManagement, DatasetRetrieval
from core.workflow import (
    ObjectVariable,
    VariableTypes,
    create_variable_from_dict,
    Context,
    create_context_from_dict,
    create_recursive_task_category_from_dict,
    flatten_variable_with_values,
    get_first_variable_value
)
from core.workflow.nodes import AgentNode, SkillNode, create_node_from_dict, UPLOAD_FILES_KEY
from core.workflow.nodes.base.import_to_kb_base import ImportToKBBaseNode
from core.llm.prompt import create_prompt_from_dict
from languages import get_language_content
from log import Logger

redis_url = f'redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}'

# Initialize a Celery application with the given name, broker, and backend
celery_app = Celery('celery_app', broker=redis_url, backend=redis_url)


# Define a Celery task to run a workflow node
# This task takes two dictionaries and additional keyword arguments:
# - node_dict: A dictionary representing a node
# - context_dict: A dictionary representing the context
# It creates the node and the context from these dictionaries, then runs the node with the context and any additional keyword arguments
@celery_app.task
def run_workflow_node(
    node_dict: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    context_dict = kwargs.pop('context_dict', None)
    if context_dict:
        kwargs['context'] = create_context_from_dict(context_dict)
        
    task = kwargs['task']
    if task:
        task['current'] = create_recursive_task_category_from_dict(task['current']) if task['current'] else None
        task['parent'] = create_recursive_task_category_from_dict(task['parent']) if task['parent'] else None
        
    user_id = kwargs.get('user_id', 0)
    os.environ['ACTUAL_USER_ID'] = str(user_id)
        
    return create_node_from_dict(node_dict).run(**kwargs)


@celery_app.task
def run_app(
    app_type: Literal['agent', 'skill'],
    id_: int,
    user_id: int,
    input_dict: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    os.environ['ACTUAL_USER_ID'] = str(user_id)
    input_: ObjectVariable = create_variable_from_dict(input_dict)
    match app_type:
        case 'agent':
            agent = Agents().get_agent_by_id(id_)
            app_id = agent['app_id']
            run_type = 1 if agent['publish_status'] == 0 else 2
            app = Apps().get_app_by_id(app_id)
            node = AgentNode(
                title=app['name'],
                desc=app['description'],
                input=input_,
                agent_id=id_,
                ability_id=kwargs['ability_id'],
                prompt=create_prompt_from_dict(kwargs['prompt']),
            )
        case 'skill':
            skill = CustomTools().get_skill_by_id(id_)
            app_id = skill['app_id']
            run_type = 1 if skill['publish_status'] == 0 else 2
            app = Apps().get_app_by_id(app_id)
            node = SkillNode(
                title=app['name'],
                desc=app['description'],
                input=input_,
                skill_id=id_
            )
        case _:
            raise ValueError(f'Invalid app type: {app_type}')
        
    # App validation
    # try:
    #     node.validate()
    # except Exception as e:
    #     return {
    #         'status': 'failed',
    #         'message': str(e)
    #     }
    
    # Run app
    result = node.run(
        Context(),
        app_id=app_id,
        user_id=user_id,
        type=run_type,
        **kwargs
    )
    outputs = result['data'].get('outputs')
    result['data']['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
    if app_type == 'agent':
        result['data']['outputs_md'] = get_first_variable_value(create_variable_from_dict(outputs))
    else:
        result['data']['outputs_md'] = None
    return result


@celery_app.task
def run_dataset(
    dataset_id: int,
    user_id: int,
    user_input: str,
    **kwargs
) -> Dict[str, Any]:
    logger = Logger.get_logger('dataset')
    try:
        os.environ['ACTUAL_USER_ID'] = str(user_id)
        retrieval, retrieval_result, _ = DatasetRetrieval.single_retrieve(
            dataset_id, 0, 0, user_id, 1
        )
        retrieval.invoke(user_input)
        return {
            'status': 'success',
            'message': 'Dataset executed successfully.',
            'data': [
                {
                    'index_id': str(segment.metadata['index_id']),
                    'score': segment.metadata.get('score', 0.0),
                    'reranking_score': segment.metadata.get('relevance_score', 0.0)
                }
                for segment in retrieval_result
            ]
        }
    except Exception as e:
        logger.exception('ERROR!!')
        return {
            'status': 'failed',
            'message': str(e)
        }


@celery_app.task
def run_node(
    node_dict: Dict[str, Any],
    node_input: Optional[Dict[str, Any]],
    user_id: int,
    workflow_id: int,
    context: Optional[List[Dict[str, Any]]],
    **kwargs
) -> Dict[str, Any]:
    os.environ['ACTUAL_USER_ID'] = str(user_id)
    app_node_exec = AppNodeExecutions()
    node = create_node_from_dict(node_dict)
    if node_input:
        node.data['input'] = create_variable_from_dict(node_input)
    workflow = Workflows().select_one(
        columns=['app_id', 'publish_status'],
        conditions=[{'column': 'id', 'value': workflow_id}]
    )
    assert workflow, 'Invalid workflow ID!'
    run_type = 1 if workflow['publish_status'] == 0 else 2
    exec_id = app_node_exec.insert(
        {
            'workflow_id': workflow_id,
            'user_id': user_id,
            'app_run_id': 0,
            'type': run_type,
            'node_id': node.id,
            'node_type': node.data['type'],
            'node_name': node.data['title'],
            'node_graph': node.to_dict(),
            'status': 2,  # Status indicating the node execution has started
        }
    )
    result = node.run(
        create_context_from_dict(context) if context else Context(),
        app_id=workflow['app_id'],
        workflow_id=workflow_id,
        user_id=user_id,
        type=run_type,
        **kwargs
    )
    if result['status'] == 'success':
        now = datetime.now()
        app_node_exec.update(
            {'column': 'id', 'value': exec_id},
            {
                'status': 3,
                'finished_time': now,
                **result['data']
            }
        )
        result['data']['finished_time'] = str(now.replace(microsecond=0))

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
            result['data']['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
            if node.data['type'] in ['llm', 'agent']:
                result['data']['outputs_md'] = get_first_variable_value(create_variable_from_dict(outputs))
            elif node.data['type'] in ['recursive_task_generation', 'recursive_task_execution']:
                task_dict = json.loads(get_first_variable_value(create_variable_from_dict(outputs)))
                result['data']['outputs_md'] = create_recursive_task_category_from_dict(task_dict).to_markdown()
            else:
                result['data']['outputs_md'] = None
    else:
        app_node_exec.update(
            {'column': 'id', 'value': exec_id},
            {
                'status': 4,
                'error': result['message']
            }
        )
    return result

@celery_app.task
def reindex_dataset(dataset_id: int, new_embeddings_config_id: int):
    DatasetManagement.reindex_dataset(dataset_id, new_embeddings_config_id)

@celery_app.task
def import_output_variable_to_knowledge_base(
    node: Dict[str, Any],
    new_variable: Dict[str, Any],
    knowledge_base_mapping: Dict[str, int],
    app_run_id: int,
    new_node_exec_id: int,
    source_string: Optional[str] = None
):
    node: ImportToKBBaseNode = create_node_from_dict(node)
    node.import_variables_to_knowledge_base(
        create_variable_from_dict(new_variable),
        knowledge_base_mapping,
        app_run_id,
        new_node_exec_id,
        False,
        source_string
    )
    AppRuns().update(
        {'column': 'id', 'value': app_run_id},
        {'need_human_confirm': 0}
    )


# Update Celery application configuration
# Set the expiration time of task results to 3600 seconds (1 hour)
celery_app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    celery_app.worker_main(
        argv=[
            'worker',
            '--loglevel=info',
            f'--concurrency={settings.CELERY_WORKERS}'
        ]
    )