from time import monotonic
from typing import Any, Dict, Optional

from .base import ImportToKBBaseNode
from ..context import Context
from ..variables import ObjectVariable, validate_required_variable
from log import Logger


logger = Logger.get_logger('celery-app')


class HumanNode(ImportToKBBaseNode):
    """
    A HumanNode object is used to create manual confirmation tasks in a workflow.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        input: Optional[ObjectVariable] = None, 
        output: Optional[ObjectVariable] = None,
        requires_upload: bool = False, 
        wait_for_all_predecessors: bool = False, 
        manual_confirmation: bool = True, 
        import_to_knowledge_base: Dict[str, bool] = {},
        knowledge_base_mapping: Dict[str, Dict[str, int]] = {},
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a HumanNode object with specific parameters for manual confirmation tasks.
        """
        init_kwargs = {
            "type": "human",
            "title": title,
            "desc": desc,
            "input": input,
            "output": output,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "manual_confirmation": manual_confirmation,
            "import_to_knowledge_base": import_to_knowledge_base,
            "knowledge_base_mapping": knowledge_base_mapping,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        app_run_id: int = 0,
        node_exec_id: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = monotonic()
            validate_required_variable(self.data['input'])

            self.import_inputs_to_knowledge_base_and_get_file_list(
                app_run_id, node_exec_id,
                (
                    # NOT running the node separately,
                    # which means running in the execution of the workflow
                    app_run_id != 0
                    and self.data['import_to_knowledge_base'].get('input', False)
                )
            )
            
            return {
                'status': 'success',
                'message': 'Human node completed successfully.',
                'data': {
                    'elapsed_time': monotonic() - start_time,
                    'inputs':self.data['input'].to_dict(),
                    'output_type' : 1,
                    'outputs': self.data['output'].to_dict(),
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            self.delete_documents_by_node_exec_id(node_exec_id)
            return {
                'status': 'failed',
                'message': str(e)
            }
    