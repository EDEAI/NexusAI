import sys, uuid, json
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from . import LLMBaseNode
from ..variables import Variable, ArrayVariable, ObjectVariable, validate_required_variable, get_first_variable_value
from ..context import Context, replace_variable_value_with_context
from core.llm.prompt import Prompt
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('celery-app')

class RequirementCategory:
    """
    A class to manage requirement categories, each represented as a dictionary with an ID and content.
    """
    
    def __init__(self):
        """
        Initializes the RequirementCategory object with an empty list to store categories.
        """
        self.categories: List[Dict[str, str]] = []

    def add_category(self, content: str) -> None:
        """
        Adds a new category to the list of categories.

        :param content: The content of the requirement category.
        """
        category = {
            "id": str(uuid.uuid4()),
            "content": content
        }
        self.categories.append(category)
        
    def get_category_name_by_id(self, category_id: str) -> str:
        """
        Retrieves the name of the category given its ID.

        :param category_id: The ID of the category to find.
        :return: The content (name) of the category if found, otherwise returns an empty string.
        """
        for category in self.categories:
            if category["id"] == category_id:
                return category["content"]
        return ""
        
    def to_dict(self) -> List[Dict[str, str]]:
        """
        Converts the list of categories to a list of dictionaries.

        :return: A list of dictionaries, each representing a requirement category.
        """
        return self.categories
    
def create_requirement_category_from_dict(categories_list: List[Dict[str, str]]) -> RequirementCategory:
    """
    Creates an instance of RequirementCategory from a list of dictionaries.

    :param categories_list: A list of dictionaries, each representing a requirement category.
    :return: An instance of RequirementCategory populated with the provided categories.
    """
    requirement_category = RequirementCategory()
    requirement_category.categories = categories_list
    return requirement_category

class RequirementCategoryNode(LLMBaseNode):
    """
    A RequirementCategoryNode object is used to create requirement categories in a workflow.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        input: Optional[Union[Variable, ArrayVariable, ObjectVariable]] = None, 
        model_config_id: int = 0, 
        requirement_category: Optional[RequirementCategory] = None, 
        prompt: Optional[Prompt] = None,
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a RequirementCategoryNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "requirement_category",
            "title": title,
            "desc": desc,
            "input": input,
            "model_config_id": model_config_id,
            "requirement_category": requirement_category,
            "prompt": prompt,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(
        self,
        context: Context,
        app_run_id: int = 0,
        edge_id: str = '',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            requirement_category = self.data['requirement_category']
            if not requirement_category:
                raise Exception("Requirement category not found.")
            category_example_json = json.dumps({'id': 'category ID', 'content': 'category name'})
            all_category_json = json.dumps(requirement_category.to_dict(), ensure_ascii=False)
            
            input = self.data['input']
            replace_variable_value_with_context(input, context)
            validate_required_variable(input)
            
            prompt_config = get_language_content("requirement_category")
            if self.data["prompt"]:
                prompt_config["system"] += "\n" + self.duplicate_braces(self.data["prompt"].get_system())
            self.data["prompt"] = Prompt(system=prompt_config["system"], user=prompt_config["user"])
            
            model_data, category, prompt_tokens, completion_tokens, total_tokens = self.invoke(
                app_run_id=app_run_id, 
                edge_id=edge_id,
                context=context, 
                input={
                    'format': category_example_json,
                    'requirement': get_first_variable_value(input),
                    'categories': all_category_json
                },
                return_json=True,
            )
            
            category_id = category["id"]
            category_name = requirement_category.get_category_name_by_id(category_id)
            if not category_name:
                raise Exception("Category name not found.")
            outputs = Variable(name="category_name", type="string", value=category_name)
            
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Requirement category node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'inputs': input.to_dict(),
                    'model_data': model_data,
                    'condition_id': category_id,
                    'output_type' : 1,
                    'outputs': outputs.to_dict(),
                    'prompt_tokens': prompt_tokens,
                    'completion_tokens': completion_tokens,
                    'total_tokens': total_tokens
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }