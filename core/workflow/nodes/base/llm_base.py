import asyncio, sys, json, re
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from copy import deepcopy
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, Union

from langchain_core.documents import Document
from langchain_core.messages import AIMessageChunk
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
    
    def _prepare_messages_and_input(
        self, 
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Dict[str, Any] = {},
        file_list: Optional[ArrayVariable] = None,
        correct_llm_output: bool = False,
        requirements_and_goals: Optional[str] = None,
        requirements_and_goals_kwargs: Optional[Dict[str, str]] = None,
        override_rag_input: Optional[str] = None
    ) -> Tuple[Messages, Dict[str, Any]]:
        if correct_llm_output:
            if edge_id:
                history = AppNodeExecutions().get_node_history(app_run_id, edge_id)
            else:
                history = AIToolLLMRecords().get_history_record(app_run_id)
            if not history or len(history) != 2:
                raise Exception("history not found.")
            if history[1].get("model_data"):
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
            
            user_prompt = input['user_prompt'] if override_rag_input is None else override_rag_input
            rag_result = retrieval_chain.invoke(user_prompt if override_rag_input is None else override_rag_input)
            formatted_docs = format_docs(rag_result)
            if requirements_and_goals_kwargs:
                requirements_and_goals_kwargs['formatted_docs'] = formatted_docs
            else:
                input['formatted_docs'] = formatted_docs
        if requirements_and_goals:
            input['requirements_and_goals'] = requirements_and_goals.format(**requirements_and_goals_kwargs)

        return messages, input
        
    def invoke(
        self,
        app_run_id: int, 
        edge_id: str,
        context: Context,
        retrieval_chain: Optional[Runnable[Input, Output]] = None,
        input: Dict[str, Any] = {},
        file_list: Optional[ArrayVariable] = None,
        return_json: bool = False,
        correct_llm_output: bool = False,
        requirements_and_goals: Optional[str] = None,
        requirements_and_goals_kwargs: Optional[Dict[str, str]] = None,
        override_rag_input: Optional[str] = None
    ) -> Tuple[Dict[str, Any], str, int, int, int]:
        """
        Workflow node invokes the LLM model to generate text using the language model.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The UUID of the edge.
            context (Context): The context object containing all variables.
            retrieval_chain (Optional[Runnable[Input, Output]]): The retrieval chain to be used for the model.
            input (Dict[str, Any]): The input data to be passed to the model.
            file_list (Optional[ArrayVariable]): The list of files to be uploaded to the model.
            return_json (bool): Indicates whether to return the output in JSON format.
            correct_llm_output (bool): Indicates whether to correct the LLM output using the correct prompt.
            requirements_and_goals (Optional[str]): The requirements and goals to be passed to the model.
            requirements_and_goals_kwargs (Optional[Dict[str, str]]): The keyword arguments to be passed to the requirements and goals.
            override_rag_input (Optional[str]): The input to be used for the retrieval chain.
            
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

        messages, input = self._prepare_messages_and_input(
            app_run_id=app_run_id, 
            edge_id=edge_id,
            context=context,
            retrieval_chain=retrieval_chain,
            input=input,
            file_list=file_list,
            correct_llm_output=correct_llm_output,
            requirements_and_goals=requirements_and_goals,
            requirements_and_goals_kwargs=requirements_and_goals_kwargs,
            override_rag_input=override_rag_input
        )

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
    
    def get_ainvoke_func(
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
        requirements_and_goals_kwargs: Optional[Dict[str, str]] = None,
        override_rag_input: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Callable[[], AsyncIterator[AIMessageChunk]]]:
        """
        This function is used to get the model data and the async AI invoke function.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The UUID of the edge.
            context (Context): The context object containing all variables.
            retrieval_chain (Optional[Runnable[Input, Output]]): The retrieval chain to be used for the model.
            input (Dict[str, Any]): The input data to be passed to the model.
            file_list (Optional[ArrayVariable]): The list of files to be uploaded to the model.
            return_json (bool): Indicates whether to return the output in JSON format.
            correct_llm_output (bool): Indicates whether to correct the LLM output using the correct prompt.
            requirements_and_goals (Optional[str]): The requirements and goals to be passed to the model.
            requirements_and_goals_kwargs (Optional[Dict[str, str]]): The keyword arguments to be passed to the requirements and goals.
            override_rag_input (Optional[str]): The input to be used for the retrieval chain, if provided.

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
        messages, input = self._prepare_messages_and_input(
            app_run_id=app_run_id, 
            edge_id=edge_id,
            context=context,
            retrieval_chain=retrieval_chain,
            input=input,
            file_list=file_list,
            correct_llm_output=correct_llm_output,
            requirements_and_goals=requirements_and_goals,
            requirements_and_goals_kwargs=requirements_and_goals_kwargs,
            override_rag_input=override_rag_input
        )

        async def ainvoke():
            llm_input = [(role, message.value.format(**input)) for role, message in messages.messages]

            for _ in range(5):
                try:
                    llm_aiter = llm_pipeline.llm.astream(llm_input, stream_usage=True)
                    while True:
                        try:
                            yield await asyncio.wait_for(anext(llm_aiter), timeout=20)
                        except StopAsyncIteration:
                            break
                    break
                except asyncio.TimeoutError:
                    pass
            else:
                raise Exception('Cannot connect to LLM after trying 5 times. Please check the network connection.')
        
        messages_copy = deepcopy(messages)
        messages_copy.replace_variables(input)
        model_data = {
            'model': llm_config,
            'messages': messages_copy.serialize(),
        }
        return model_data, ainvoke
    
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