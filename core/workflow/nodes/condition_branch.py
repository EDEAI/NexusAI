import sys, uuid
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parent.parent.parent.parent))

from typing import List, Dict, Optional, Any
from datetime import datetime
from . import Node
from ..variables import Variable, create_variable_from_dict
from ..context import Context, replace_variable_value_with_context
from log import Logger


logger = Logger.get_logger('celery-app')

class LogicCondition:
    """
    Represents a logic condition that compares a variable's value against a target value using a specified operator.
    """
    def __init__(
        self, 
        variable: Variable, 
        operator: str, 
        target_value: str
    ):
        """
        Initializes a LogicCondition object.

        :param variable: Variable, the variable object whose value is to be compared.
        :param operator: str, the operator used for comparison. Accepts '=', '!=', '>', '<', '>=', '<=', 'is None', 'is not None'.
        :param target_value: str, the target value to compare the variable's value against.
        """
        if variable.type not in ["string", "number"]:
            raise ValueError(f"Logic conditions are only supported for variables of type 'string' or 'number' (received '{variable.type}')")
        self.variable = variable
        self.operator = operator
        self.target_value = float(target_value) if variable.type == "number" else str(target_value)

    def evaluate(self) -> bool:
        """
        Evaluates the logic condition by comparing the variable's value against the target value using the specified operator.

        :return: bool, the result of the logic comparison.
        """
        if self.variable.type == "number":
            if self.operator == "=":
                return self.variable.value == self.target_value
            elif self.operator == "≠":
                return self.variable.value != self.target_value
            elif self.operator == ">":
                return self.variable.value > self.target_value
            elif self.operator == "<":
                return self.variable.value < self.target_value
            elif self.operator == ">=":
                return self.variable.value >= self.target_value
            elif self.operator == "<=":
                return self.variable.value <= self.target_value
            elif self.operator == "is None":
                return self.variable.value is None
            elif self.operator == "is not None":
                return self.variable.value is not None
            else:
                raise ValueError(f"Type:number unsupported operator: {self.operator}")
        elif self.variable.type == "string":
            if self.operator == "=":
                return self.variable.value == self.target_value
            elif self.operator == "≠":
                return self.variable.value != self.target_value
            elif self.operator == "in":
                return self.target_value in self.variable.value
            elif self.operator == "not in":
                return self.target_value not in self.variable.value
            elif self.operator == "startswith":
                return self.variable.value.startswith(self.target_value)
            elif self.operator == "endswith":
                return self.variable.value.endswith(self.target_value)
            elif self.operator == "is None":
                return self.variable.value is None or self.variable.value == ""
            elif self.operator == "is not None":
                return self.variable.value is not None or self.variable.value != ""
            else:
                raise ValueError(f"Type:string unsupported operator: {self.operator}")
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the LogicCondition instance into a dictionary representation.

        :return: A dictionary containing the properties of the LogicCondition instance.
        """
        return {
            "variable": self.variable.to_dict(),
            "operator": self.operator,
            "target_value": self.target_value
        }
        
class LogicBranch():
    """
    Represents a list of logic conditions that are combined using a logical operator ('and' or 'or') to form a conditional branch in a workflow.
    """
    def __init__(self, operator: str, original_id: Optional[str] = None):
        """
        Initializes a LogicBranch object.

        :param conditions: A list of LogicCondition instances.
        :param operator: The logical operator to apply ('and' or 'or').
        """
        self.id = original_id if original_id else str(uuid.uuid4())
        self.conditions: List[LogicCondition] = []
        self.operator = operator
        
    def add_condition(self, condition: LogicCondition) -> None:
        """
        Adds a LogicCondition instance to the list of conditions.

        :param condition: The LogicCondition instance to add.
        """
        self.conditions.append(condition)
        
    def evaluate(self) -> bool:
        """
        Evaluates the conditional branch by applying the logical operator to all conditions.

        :return: The result of the logical operation as a boolean.
        """
        if self.operator == 'and':
            return all(condition.evaluate() for condition in self.conditions)
        else:
            return any(condition.evaluate() for condition in self.conditions)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the LogicBranch instance into a dictionary representation.

        :return: A dictionary containing the properties of the LogicBranch instance, including a list of conditions.
        """
        return {
            "id": self.id,
            "conditions": [condition.to_dict() for condition in self.conditions],
            "operator": self.operator
        }
        
class LogicBranches():
    """
    Represents a collection of logic branches in a workflow.
    """
    def __init__(self, else_branch_id: Optional[str] = None):
        """
        Initializes a LogicBranches object with an empty list to store branches.
        
        :param else_branch_id: The ID of the else branch, if it exists.
        """
        self.branches: List[LogicBranch] = []
        self.else_branch = LogicBranch("and", else_branch_id) if else_branch_id else LogicBranch("and")
        
    def add_branch(self, branch: LogicBranch) -> None:
        """
        Adds a LogicBranch instance to the collection.

        :param branch: The LogicBranch instance to add.
        """
        self.branches.append(branch)
        
    def evaluate(self) -> Optional[str]:
        """
        Evaluates all branches in the collection.

        :return: The id of the first LogicBranch that evaluates to True, or None if no such branch exists.
        """
        for branch in self.branches:
            if branch.evaluate():
                return branch.id
        return self.else_branch.id
        
    def to_dict(self) -> List[Dict[str, Any]]:
        """
        Converts the collection of LogicBranch instances into a list of dictionaries.

        :return: A list of dictionaries, each representing a LogicBranch instance.
        """
        branches_dict = [branch.to_dict() for branch in self.branches]
        branches_dict.append(self.else_branch.to_dict())
        return branches_dict
        
def create_logic_condition_from_dict(condition_dict: Dict[str, Any]) -> LogicCondition:
    """
    Creates a LogicCondition instance from a dictionary representation.

    :param condition_dict: A dictionary containing the properties of a LogicCondition instance.
    :return: A LogicCondition instance populated with the provided properties.
    """
    variable = create_variable_from_dict(condition_dict["variable"])
    operator = condition_dict["operator"]
    target_value = condition_dict["target_value"]
    return LogicCondition(variable, operator, target_value)

def create_logic_branch_from_dict(branch_dict: Dict[str, Any]) -> LogicBranch:
    """
    Creates a LogicBranch instance from a dictionary representation.

    :param branch_dict: A dictionary containing the properties of a LogicBranch instance.
    :return: A LogicBranch instance populated with the provided properties.
    """
    logic_branch = LogicBranch(branch_dict["operator"], branch_dict["id"])
    for condition in branch_dict["conditions"]:
        logic_branch.add_condition(create_logic_condition_from_dict(condition))
    return logic_branch

def create_logic_branches_from_dict(branches_list: List[Dict[str, Any]]) -> LogicBranches:
    """
    Creates a LogicBranches instance from a list of dictionaries.

    :param branches_list: A list of dictionaries, each representing a LogicBranch instance.
    :return: A LogicBranches instance populated with the provided branches.
    """
    logic_branches = LogicBranches(branches_list[-1]["id"])
    for branch_dict in branches_list[:-1]:
        logic_branches.add_branch(create_logic_branch_from_dict(branch_dict))
    return logic_branches

def replace_logic_branches_with_context(logic_branches: LogicBranches, context: Context) -> LogicBranches:
    """
    Replaces the variables in the logic branches with their values from the context.

    :param logic_branches: LogicBranches, the collection of logic branches to update.
    :param context: Context, the context object containing the variable values.
    :return: LogicBranches, the updated collection of logic branches.
    """
    for branch in logic_branches.branches:
        for condition in branch.conditions:
            replace_variable_value_with_context(condition.variable, context)
    return logic_branches

class ConditionBranchNode(Node):
    """
    A ConditionBranchNode object is used to create conditional branches in a workflow.
    """
    
    def __init__(
        self, 
        title: str, 
        desc: str = "", 
        logic_branches: Optional[LogicBranches] = None, 
        wait_for_all_predecessors: bool = True, 
        flow_data: Dict[str, Any] = {}, 
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a ConditionBranchNode object with typing enhancements and the ability to track the original node ID.
        """
        init_kwargs = {
            "type": "condition_branch",
            "title": title,
            "desc": desc,
            "logic_branches": logic_branches,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
        
    def run(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Execute the node task.
        """
        try:
            start_time = datetime.now()
            logic_branches = self.data['logic_branches']
            replace_logic_branches_with_context(logic_branches, context)
            branch_id = logic_branches.evaluate()
            end_time = datetime.now()
            return {
                'status': 'success',
                'message': 'Condition branch node executed successfully.',
                'data': {
                    'elapsed_time': end_time.timestamp() - start_time.timestamp(),
                    'condition_id': branch_id
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }