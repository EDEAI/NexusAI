from typing import Any, Dict, Optional
from datetime import datetime
from .base import ImportToKBBaseNode
from ..variables import ObjectVariable, validate_required_variable
from log import Logger


logger = Logger.get_logger('celery-app')

class StartNode(ImportToKBBaseNode):
    """
    A StartNode object is used to mark the start of the workflow.
    """

    def __init__(
        self,
        title: str,
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        output: Optional[ObjectVariable] = None,
        requires_upload: bool = False,
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a StartNode object.
        """
        init_kwargs = {
            "type": "start",
            "title": title,
            "desc": desc,
            "input": input,
            "output": output,
            "requires_upload": requires_upload,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id

        super().__init__(**init_kwargs)

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            validate_required_variable(self.data['input'])
            app_run_id = kwargs.get('app_run_id', 0)
            node_exec_id = kwargs.get('node_exec_id', 0)
            self.import_inputs_to_knowledge_base_and_get_file_list(
                app_run_id, node_exec_id, self.data['requires_upload'],
                (
                    # NOT running the node separately,
                    # which means running in the execution of the workflow
                    app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('input', False)
                )
            )
                
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Workflow execution successfully started.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': self.data['input'].to_dict(),
                    'output_type' : 1,
                    'outputs': self.data['output'].to_dict(),
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            node_exec_id = kwargs.get('node_exec_id', 0)
            self.delete_documents_by_node_exec_id(node_exec_id)
            return {
                'status': 'failed',
                'message': str(e)
            }
