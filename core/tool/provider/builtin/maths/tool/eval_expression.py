import numexpr as ne
from core.workflow.variables import ObjectVariable, Variable
from core.tool.provider.builtin_tool_provider import BuiltinTool

class EvaluateExpressionTool(BuiltinTool):
    def _invoke(self, tool_parameters: ObjectVariable) -> Variable:
        """
        Invoke the tool to evaluate a mathematical expression.

        :param tool_parameters: ObjectVariable containing the parameters for the tool.
        :return: Variable containing the result of the evaluated expression.
        :raises ValueError: If the expression is invalid or evaluation fails.
        """
        # Convert tool parameters to a dictionary, filtering out None values
        tool_parameters_dict = {
            key: value.value
            for key, value in tool_parameters.properties.items()
            if value.value is not None
        }

        # Retrieve and clean the expression from the parameters
        expression = tool_parameters_dict.get('expression', '').strip()
        if not expression:
            raise ValueError('Invalid expression')

        try:
            # Evaluate the expression using numexpr
            result = ne.evaluate(expression)
        except Exception as e:
            # Raise an error if evaluation fails
            raise ValueError(f'Invalid expression: {expression}, error: {str(e)}')

        # Return the result as a Variable object
        return Variable(name='text', type="string", value=str(result), display_name='Output text')