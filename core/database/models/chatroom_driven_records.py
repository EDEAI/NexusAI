from core.database import MySQL
from core.database.models.ai_tool_llm_records import AIToolLLMRecords
from core.database.models.app_runs import AppRuns
from core.database.models.apps import Apps
from core.database.models.workflows import Workflows
from core.workflow.variables import create_variable_from_dict
import math


class ChatroomDrivenRecords(MySQL):
    """
    A database model class for managing chatroom driven records.
    Inherits from MySQL base class to handle database operations.

    This class provides an interface to interact with the chatroom_driven_records table,
    which stores the relationships between data source runs and data driven runs.
    """

    table_name = "chatroom_driven_records"
    """
    The name of the database table this model interacts with.
    """

    have_updated_time = False
    """
    Configuration flag indicating that this table doesn't track update timestamps.
    Set to False to disable automatic update_time management.
    """

    def get_data_by_data_source_run_id(self, data_source_run_id: int):
        """
        Retrieve record information based on the data source run ID.

        Args:
            data_source_run_id (int): The unique identifier of the data source run

        Returns:
            dict: A dictionary containing the record information with fields:
                - id: The record's unique identifier
                - data_source_run_id: The associated data source run ID
                - data_driven_run_id: The associated data driven run ID

        Note:
            Returns None if no matching record is found.
        """
        info = self.select_one(
            columns=[
                'id', 'data_source_run_id', 'data_driven_run_id'
            ],
            conditions=[
                {"column": "data_source_run_id", "value": data_source_run_id},
            ]
        )
        return info

    def update_data_driven_run_id(self, id: int, data_source_run_id: int, data_driven_run_id: int):
        """
        Update the data_driven_run_id for a specific record identified by data_source_run_id.

        Args:
            data_source_run_id (int): The identifier of the data source run to update
            data_driven_run_id (int): The new data driven run ID to set

        Returns:
            bool: True if the update was successful, False otherwise

        Note:
            This method updates a single record matching the data_source_run_id.
        """
        update_data = {
            "data_driven_run_id": data_driven_run_id
        }
        info = self.update(
            [
                {"column": "data_source_run_id", "value": data_source_run_id},
                {"column": "id", "value": id}
            ], update_data
        )
        return info

    def get_history_by_chatroom_id(self, chatroom_id: int, page: int = 1, page_size: int = 10):
        """Get chat room history with pagination"""
        driven_records = self.select(
            columns=[
                'id', 'data_source_run_id', 'data_driven_run_id', 'chatroom_id'
            ],
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
            ],
            order_by='id DESC',
            limit=page_size,
            offset=(page - 1) * page_size
        )

        # Get total count for pagination
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
            ]
        )['count_id']

        history_list = []
        if driven_records:
            for record in driven_records:
                record_data = {
                    'source_run': None,
                    'source_corrections': [],
                    'target_run': None,
                    'target_details': None
                }

                # Handle source run
                if record['data_source_run_id']:
                    source_run = AppRuns().select_one(
                        columns=[
                            'id', 'name', 'status', 'created_time', 'finished_time',
                            'elapsed_time', 'total_tokens'
                        ],
                        conditions=[
                            {"column": "id", "value": record['data_source_run_id']}
                        ]
                    )

                    summary_records = AIToolLLMRecords().select(
                        columns=[
                            'id', 'run_type', 'inputs', 'outputs', 'correct_prompt',
                            'created_time', 'status','user_prompt'
                        ],
                        conditions=[
                            {"column": "app_run_id", "value": record['data_source_run_id']},
                            {"column": "ai_tool_type", "value": 3}
                        ],
                        order_by='id ASC'
                    )

                    if summary_records:
                        first_record = summary_records[0]
                        # Parse original summary outputs using variables
                        summary = None
                        if first_record.get('outputs'):
                            try:
                                if isinstance(first_record['outputs'], dict):
                                    variable = create_variable_from_dict(first_record['outputs'])
                                    summary = variable.value
                            except:
                                pass

                        record_data['source_run'] = {
                            **source_run,
                            'summary': summary
                        }

                        # Handle corrections
                        for rec in summary_records[1:]:
                            correction = {
                                'created_time': rec['created_time'],
                                'user_prompt': rec['user_prompt'],
                                'correct_prompt': None,
                                'corrected_summary': None
                            }

                            # Parse correct_prompt
                            if rec.get('correct_prompt'):
                                try:
                                    correction['correct_prompt'] = rec['correct_prompt']
                                except:
                                    pass

                            # Parse corrected summary outputs
                            if rec.get('outputs'):
                                try:
                                    variable = create_variable_from_dict(rec['outputs'])
                                    correction['corrected_summary'] = variable.value
                                except:
                                    pass

                            record_data['source_corrections'].append(correction)

                # Handle target run
                if record['data_driven_run_id']:
                    # Get target run info
                    target_run = AppRuns().select_one(
                        columns=[
                            'id', 'app_id', 'agent_id', 'workflow_id', 'name',
                            'status', 'created_time', 'finished_time', 'elapsed_time',
                            'completed_steps', 'total_steps', 'inputs', 'outputs',
                            'total_tokens'
                        ],
                        conditions=[
                            {"column": "id", "value": record['data_driven_run_id']}
                        ]
                    )

                    if target_run:
                        app = Apps().select_one(
                            columns=['id', 'name', 'mode'],
                            conditions=[{"column": "id", "value": target_run['app_id']}]
                        )

                        # Process status
                        if target_run['status'] in (1, 2):
                            target_run['status'] = 1
                        elif target_run['status'] == 3:
                            target_run['status'] = 2
                        elif target_run['status'] == 4:
                            target_run['status'] = 3

                        # Calculate progress percentage
                        completed = target_run.get('completed_steps', 0) or 0
                        total = target_run.get('total_steps', 0) or 0
                        target_run['percentage'] = int((completed / total * 100) if total > 0 else 0)

                        # Parse inputs using variables
                        if target_run.get('inputs'):
                            try:
                                print(target_run['inputs'])
                                target_run['inputs'] = target_run['inputs']
                            except:
                                target_run['inputs'] = None

                        # Parse outputs using variables
                        if target_run.get('outputs'):
                            try:
                                target_run['outputs'] = target_run['outputs']
                            except:
                                target_run['outputs'] = ModuleNotFoundError
                        target_run['app'] = app
                        record_data['target_run'] = target_run

                        # Add type-specific details
                        if app and app['mode'] == 1:  # Agent
                            agent_details = AIToolLLMRecords().select_one(
                                columns=['inputs', 'outputs'],
                                conditions=[
                                    {"column": "app_run_id", "value": record['data_driven_run_id']},
                                    {"column": "ai_tool_type", "value": 0}
                                ]
                            )
                            if agent_details:
                                # Parse agent inputs
                                if agent_details.get('inputs'):
                                    try:
                                        agent_details['inputs'] = agent_details['inputs']
                                    except:
                                        agent_details['inputs'] = None

                                # Parse agent outputs
                                if agent_details.get('outputs'):
                                    try:
                                        agent_details['outputs'] = agent_details['outputs']
                                    except:
                                        agent_details['outputs'] = None

                                record_data['target_details'] = agent_details

                        elif app and app['mode'] == 2:  # Workflow
                            workflow = Workflows().select_one(
                                columns=['id', 'graph'],
                                conditions=[{"column": "id", "value": target_run['workflow_id']}]
                            )
                            if workflow:
                                record_data['target_details'] = {
                                    'workflow': workflow,
                                    'run_details': {
                                        'name': target_run['name'],
                                        'apps_name': app['name'],
                                        'status': target_run['status'],
                                        'created_time': target_run['created_time'],
                                        'finished_time': target_run['finished_time'],
                                        'elapsed_time': target_run['elapsed_time'],
                                        'completed_steps': target_run['completed_steps'],
                                        'total_steps': target_run['total_steps'],
                                        'percentage': target_run['percentage']
                                    }
                                }

                history_list.append(record_data)

        return {
            "list": history_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def get_history_by_chatroom_id_single(self, chatroom_id: int, app_run_id: int):
        """Get chat room history with pagination"""
        driven_records = self.select(
            columns=[
                'id', 'data_source_run_id', 'data_driven_run_id', 'chatroom_id'
            ],
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
                {"column": "data_source_run_id", "value": app_run_id}
            ],
            order_by='id DESC'
        )

        history_list = []
        if driven_records:
            for record in driven_records:
                record_data = {
                    'source_run': None,
                    'source_corrections': [],
                    'target_run': None,
                    'target_details': None
                }

                # Handle source run
                if record['data_source_run_id']:
                    source_run = AppRuns().select_one(
                        columns=[
                            'id', 'name', 'status', 'created_time', 'finished_time',
                            'elapsed_time', 'total_tokens'
                        ],
                        conditions=[
                            {"column": "id", "value": record['data_source_run_id']}
                        ]
                    )

                    summary_records = AIToolLLMRecords().select(
                        columns=[
                            'id', 'run_type', 'inputs', 'outputs', 'correct_prompt',
                            'created_time', 'status', 'user_prompt'
                        ],
                        conditions=[
                            {"column": "app_run_id", "value": record['data_source_run_id']},
                            {"column": "ai_tool_type", "value": 3}
                        ],
                        order_by='id Asc'
                    )

                    if summary_records:
                        first_record = summary_records[0]
                        # Parse original summary outputs using variables
                        summary = None
                        if first_record.get('outputs'):
                            try:
                                if isinstance(first_record['outputs'], dict):
                                    variable = create_variable_from_dict(first_record['outputs'])
                                    summary = variable.value
                            except:
                                pass

                        record_data['source_run'] = {
                            **source_run,
                            'summary': summary
                        }

                        # Handle corrections
                        for rec in summary_records[1:]:
                            correction = {
                                'created_time': rec['created_time'],
                                'user_prompt': rec['user_prompt'],
                                'correct_prompt': None,
                                'corrected_summary': None
                            }

                            # Parse correct_prompt
                            if rec.get('correct_prompt'):
                                try:
                                    correction['correct_prompt'] = rec['correct_prompt']
                                except:
                                    pass

                            # Parse corrected summary outputs
                            if rec.get('outputs'):
                                try:
                                    variable = create_variable_from_dict(rec['outputs'])
                                    correction['corrected_summary'] = variable.value
                                except:
                                    pass

                            record_data['source_corrections'].append(correction)

                # Handle target run
                if record['data_driven_run_id']:
                    # Get target run info
                    target_run = AppRuns().select_one(
                        columns=[
                            'id', 'app_id', 'agent_id', 'workflow_id', 'name',
                            'status', 'created_time', 'finished_time', 'elapsed_time',
                            'completed_steps', 'total_steps', 'inputs', 'outputs',
                            'total_tokens'
                        ],
                        conditions=[
                            {"column": "id", "value": record['data_driven_run_id']}
                        ]
                    )

                    if target_run:
                        app = Apps().select_one(
                            columns=['id', 'name', 'mode'],
                            conditions=[{"column": "id", "value": target_run['app_id']}]
                        )

                        # Process status
                        if target_run['status'] in (1, 2):
                            target_run['status'] = 1
                        elif target_run['status'] == 3:
                            target_run['status'] = 2
                        elif target_run['status'] == 4:
                            target_run['status'] = 3

                        # Calculate progress percentage
                        completed = target_run.get('completed_steps', 0) or 0
                        total = target_run.get('total_steps', 0) or 0
                        target_run['percentage'] = int((completed / total * 100) if total > 0 else 0)

                        # Parse inputs using variables
                        if target_run.get('inputs'):
                            try:
                                print(target_run['inputs'])
                                target_run['inputs'] = target_run['inputs']
                            except:
                                target_run['inputs'] = None

                        # Parse outputs using variables
                        if target_run.get('outputs'):
                            try:
                                target_run['outputs'] = target_run['outputs']
                            except:
                                target_run['outputs'] = ModuleNotFoundError
                        target_run['app'] = app
                        record_data['target_run'] = target_run

                        # Add type-specific details
                        if app and app['mode'] == 1:  # Agent
                            agent_details = AIToolLLMRecords().select_one(
                                columns=['inputs', 'outputs'],
                                conditions=[
                                    {"column": "app_run_id", "value": record['data_driven_run_id']},
                                    {"column": "ai_tool_type", "value": 0}
                                ]
                            )
                            if agent_details:
                                # Parse agent inputs
                                if agent_details.get('inputs'):
                                    try:
                                        agent_details['inputs'] = agent_details['inputs']
                                    except:
                                        agent_details['inputs'] = None

                                # Parse agent outputs
                                if agent_details.get('outputs'):
                                    try:
                                        agent_details['outputs'] = agent_details['outputs']
                                    except:
                                        agent_details['outputs'] = None

                                record_data['target_details'] = agent_details

                        elif app and app['mode'] == 2:  # Workflow
                            workflow = Workflows().select_one(
                                columns=['id', 'graph'],
                                conditions=[{"column": "id", "value": target_run['workflow_id']}]
                            )
                            if workflow:
                                record_data['target_details'] = {
                                    'workflow': workflow,
                                    'run_details': {
                                        'name': target_run['name'],
                                        'apps_name': app['name'],
                                        'status': target_run['status'],
                                        'created_time': target_run['created_time'],
                                        'finished_time': target_run['finished_time'],
                                        'elapsed_time': target_run['elapsed_time'],
                                        'completed_steps': target_run['completed_steps'],
                                        'total_steps': target_run['total_steps'],
                                        'percentage': target_run['percentage']
                                    }
                                }

                # history_list.append(record_data)

        return record_data
