import json
from core.workflow.variables import ObjectVariable, Variable
from duckduckgo_search import DDGS
from core.tool.provider.builtin_tool_provider import BuiltinTool

class DuckDuckGoSearchTool(BuiltinTool):
    """
    Tool for performing a search using DuckDuckGo search engine.
    """

    def _invoke(self, tool_parameters: ObjectVariable):
        """
        Invokes the DuckDuckGo search tool with the given parameters.

        Args:
            tool_parameters (ObjectVariable): The parameters for the search tool, 
                                              including the search query and max results.

        Returns:
            Variable: A Variable object containing the search results in JSON format.
        """
        # Convert tool parameters to a dictionary, excluding None values
        tool_parameters_dict = {
            key: value.value
            for key, value in tool_parameters.properties.items()
            if value.value is not None
        }

        # Extract the search query and maximum number of results
        query = tool_parameters_dict.get('query')
        max_results = tool_parameters_dict.get('max_results', 5)

        # Perform the search using DuckDuckGo
        response = DDGS().text(query, max_results=max_results)

        # Return the search results as a JSON-formatted Variable
        return Variable(name='text', type="json", value=json.dumps(response), display_name='Output text')