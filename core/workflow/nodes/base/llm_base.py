import sys, json, re
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import Any, Callable, Dict, List, Optional, Union

from langchain_core.documents import Document
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from langchain_core.runnables.utils import Input, Output

from . import Node
from ...variables import ArrayVariable, Variable
from ...context import Context
from database.models import Models, AppNodeExecutions, DocumentSegments, Documents, AIToolLLMRecords
from llm.models import LLMPipeline
from llm.prompt import create_prompt_from_dict, replace_prompt_with_context
from llm.messages import Messages, create_messages_from_serialized_format


document_segments = DocumentSegments()
documents = Documents()

class LLMBaseNode(Node):
    """
    Base class for all LLM nodes.
    """
    
    def __init__(self, **kwargs):
        """
        Initializes a new instance of the LLMBaseNode class.
        """
        super().__init__(**kwargs)
        
    def duplicate_braces(self, text: str) -> str:
        """
        Duplicates braces in the text.
        
        Args:
            text (str): The text to duplicate braces in.
            
        Returns:
            str: The text with duplicated braces.
        """
        return text.replace("{", "{{").replace("}", "}}")
        
    def invoke(
        self, 
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Union[str, Dict[str, Any]] = {},
        file_list: Optional[ArrayVariable] = None,
        return_json: bool = False,
        correct_llm_output: bool = False,
        requirements_and_goals: Optional[str] = None,
        requirements_and_goals_kwargs: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Workflow node invokes the LLM model to generate text using the language model.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The UUID of the edge.
            context (Context): The context object containing all variables.
            retrieval_chain (Optional[Runnable[Input, Output]]): The retrieval chain to be used for the LLM model.
            input (Dict[str, Any]): The input data to be passed to the model.
            return_json (bool): Indicates whether to return the output in JSON format.
            correct_llm_output (bool): Indicates whether to correct the LLM output using the correct prompt.
            requirements_and_goals (Optional[str]): The requirements and goals to be passed to the model.
            requirements_and_goals_kwargs (Optional[Dict[str, str]]): The keyword arguments to be passed to the requirements and goals.
            
        Returns:
            Dict[str, Any]: A dictionary containing the model data, content, prompt tokens, completion tokens, and total tokens.
        """
        model_info = Models().get_model_by_config_id(self.data["model_config_id"])
        if not model_info:
            raise Exception("Model configuration not found.")
        
        llm_config = {**model_info["supplier_config"], **model_info["model_config"]}
        if return_json:
            llm_config["model_kwargs"] = {"response_format": {"type": "json_object"}}
        llm_pipeline = LLMPipeline(supplier=model_info["supplier_name"], config=llm_config)
        
        if correct_llm_output:
            if edge_id:
                history = AppNodeExecutions().get_node_history(app_run_id, edge_id)
            else:
                history = AIToolLLMRecords().get_history_record(app_run_id)
            if not history or len(history) != 2:
                raise Exception("history not found.")
            messages = create_messages_from_serialized_format(history[1]["model_data"]["messages"])
            # Escape braces in the output text
            ai_output_str = self.duplicate_braces(history[1]["model_data"]["raw_output"])
            ai_output = Variable(name="text", type="string", value=ai_output_str)
            messages.add_ai_message(ai_output)
            correct_prompt = create_prompt_from_dict(history[0]["correct_prompt"])
            # Escape braces in the corrected prompt
            if system_prompt := correct_prompt.get_system():
                correct_prompt.system.value = self.duplicate_braces(system_prompt)
            if user_prompt := correct_prompt.get_user():
                correct_prompt.user.value = self.duplicate_braces(user_prompt)
            if assistant_prompt := correct_prompt.get_assistant():
                correct_prompt.assistant.value = self.duplicate_braces(assistant_prompt)
            messages.add_prompt(correct_prompt)
        else:
            if context:
                replace_prompt_with_context(self.data["prompt"], context, duplicate_braces=True)
            messages = Messages()
            messages.add_prompt(self.data["prompt"])
            if file_list:
                for file_var in file_list.values:
                    messages.add_human_message(file_var)
        
        if retrieval_chain:
            def format_docs(segments: List[Document]) -> str:
                document_names = {}
                formatted_docs_list = []
                for segment_obj in segments:
                    index_id = str(segment_obj.metadata['index_id'])
                    segment = document_segments.get_segment_by_index_id(index_id)
                    document_id = segment['document_id']
                    if document_id in document_names:
                        document_name = document_names[document_id]
                    else:
                        document = documents.get_document_by_id(document_id)
                        document_name = document['name']
                        document_names[document_id] = document_name
                    formatted_docs_list.append(
                        {'content': segment_obj.page_content, 'source': document_name}
                    )
                return json.dumps(formatted_docs_list, ensure_ascii=False)
            
            user_prompt = input['user_prompt']
            rag_result = retrieval_chain.invoke(user_prompt)
            formatted_docs = format_docs(rag_result)
            if requirements_and_goals_kwargs:
                requirements_and_goals_kwargs['formatted_docs'] = formatted_docs
            else:
                input['formatted_docs'] = formatted_docs
        if requirements_and_goals:
            input['requirements_and_goals'] = requirements_and_goals.format(**requirements_and_goals_kwargs)
        ai_message = llm_pipeline.invoke(messages.to_langchain_format(), input)
        content = ai_message.content
        if return_json:
            content = self.extract_json_from_string(content)
        token_usage = ai_message.response_metadata["token_usage"]
        prompt_tokens = token_usage["prompt_tokens"]
        completion_tokens = token_usage["completion_tokens"]
        total_tokens = token_usage["total_tokens"]
        
        messages.replace_variables(input)
        model_data = {
            'model': llm_config,
            'messages': messages.serialize(),
            'raw_output': ai_message.content
        }
        
        return model_data, content, prompt_tokens, completion_tokens, total_tokens
    
    def extract_json_from_string(self, text: str) -> dict:
        """
        Extracts JSON content from a string, filtering out any extraneous content.

        Args:
            text (str): The string containing JSON content.

        Returns:
            dict: The extracted JSON content as a dictionary.
        """
        try:
            json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
            return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            raise ValueError(f"No valid JSON content found in the string:\n{text}")

    def extract_uuid_from_string(self, text: str) -> str:
        """
        Extracts a UUID from a string, filtering out any extraneous content.

        Args:
            text (str): The string containing a UUID.

        Returns:
            str: The extracted UUID.
        """
        try:
            return re.search(r'[0-9a-fA-F\-]+', text).group()
        except AttributeError:
            raise ValueError("No valid UUID found in the string.")