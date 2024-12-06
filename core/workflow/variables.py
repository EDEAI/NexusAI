from typing import Union, List, Dict, Tuple, Any, Optional, Type
from pydantic import BaseModel, Field, create_model
import json

class Variable:
    """
    Represents a single variable with a name, display name, type, and optional value.
    """
    
    def __init__(
        self, 
        name: str, 
        type: str, 
        display_name: Optional[str] = None, 
        value: Optional[Union[str, int, float]] = None, 
        required: Optional[bool] = None,
        max_length: Optional[int] = None
    ):
        """
        Initializes a Variable object.

        :param name: str, the name of the variable used in the backend.
        :param type: str, the type of the variable. Accepts 'string', 'number', or 'file/json'.
            Note: 'file/json' type is treated as a 'string'.
        :param display_name: str, the name of the variable displayed in the frontend.
        :param value: Union[str, int, float, None], the value of the variable. The type depends on the variable's type.
        :param required: bool, indicates if the variable is required.
        :param max_length: int, the maximum length of the value if the type is 'string'. Default is 0 (no limit).
        """
        self.name = name
        self.type = type
        if display_name is not None:
            self.display_name = display_name
        self.value = value
        if required is not None:
            self.required = required
        if self.type == "string":
            if max_length is None:
                self.max_length = 0
            else:
                self.max_length = max_length
            if self.max_length > 0 and len(self.value) > self.max_length:
                raise ValueError(f"Value exceeds maximum length of {self.max_length}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Variable object to a dictionary.

        :return: Dict[str, Any], a dictionary representation of the Variable object.
        """
        data = {
            "name": self.name,
            "type": self.type,
            "value": self.value
        }
        if hasattr(self, "display_name"):
            data["display_name"] = self.display_name
        if hasattr(self, "required"):
            data["required"] = self.required
        if hasattr(self, "max_length"):
            data["max_length"] = self.max_length
        return data
        
    def to_string(self) -> str:
        """
        Converts the value of the variable to a string.
        
        :return: str, the string representation of the value.
        """
        if self.value is None:
            return ""
        return str(self.value) if self.type == "number" else self.value
        
class ArrayVariable:
    """
    Represents an array variable with a name, display name, type, and a list of values.
    """
    
    def __init__(
        self, 
        name: str, 
        type: str, 
        display_name: Optional[str] = None
    ):
        """
        Initializes an ArrayVariable object with an empty list of values.

        :param name: str, the internal name of the array variable.
        :param type: str, the type of the elements in the array. Accepts 'array[string]', 'array[number]', 'array[file]', 'array[object]'.
        :param display_name: str, the display name of the array variable.
        """
        self.name = name
        self.type = type
        if display_name is not None:
            self.display_name = display_name
        self.values: List[Variable] = []

    def add_value(self, value: Union[Variable, "ObjectVariable"]):
        """
        Adds a new value to the array if it matches the array's element type.

        :param value: Union[Variable, ObjectVariable], the value to be added. Its type must match the specified element type in type.
        """
        # Extract the type of the array elements from type (e.g., 'array[string]' -> 'string')
        element_type = self.type.split('[')[-1].split(']')[0]
        
        if value.type == element_type:
            self.values.append(value)
        else:
            raise ValueError(f"Value must be of type {element_type} as specified in type")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ArrayVariable object to a dictionary representation.

        :return: Dict[str, Any], a dictionary representation of the ArrayVariable object, including its name, display name, type, and values.
        """
        data = {
            "name": self.name,
            "type": self.type,
            "values": [value.to_dict() for value in self.values]
        }
        if hasattr(self, 'display_name'):
            data["display_name"] = self.display_name
        return data
        
    def to_string(self) -> str:
        """
        Converts the values of the array to a concatenated string separated by newlines.
        
        :return: str, the newline-separated string representation of the values.
        """
        return '\n'.join([value.to_string() for value in self.values])
        
class ObjectVariable:
    """
    Represents an object variable with a name, display name, type, and a dictionary of properties.
    """
    
    def __init__(
        self, 
        name: str, 
        display_name: Optional[str] = None,
        to_string_keys: Optional[List[str]] = None
    ):
        """
        Initializes an ObjectVariable object with no properties.

        :param name: str, the name of the object variable used in the backend.
        :param display_name: str, the name of the object variable displayed in the frontend.
        :param to_string_keys: Optional[List[str]], a list of property names to include in the to_string output.
        """
        self.name = name
        if display_name is not None:
            self.display_name = display_name
        self.type = "object"
        self.properties: Dict[str, Union[Variable, ArrayVariable, ObjectVariable]] = {}
        if to_string_keys is not None:
            self.to_string_keys = to_string_keys

    def add_property(self, key: str, value: Union[Variable, ArrayVariable, "ObjectVariable"]):
        """
        Adds a new property to the object.

        :param key: str, the name of the property.
        :param value: Union[Variable, ArrayVariable, ObjectVariable], the value of the property.
        """
        self.properties[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ObjectVariable object to a dictionary.

        :return: Dict[str, Any], a dictionary representation of the ObjectVariable object.
        """
        data = {
            "name": self.name,
            "type": self.type,
            "properties": {key: value.to_dict() for key, value in self.properties.items()}
        }
        if hasattr(self, 'display_name'):
            data["display_name"] = self.display_name
        if hasattr(self, 'to_string_keys'):
            data["to_string_keys"] = self.to_string_keys
        return data
        
    def to_string(self) -> str:
        """
        Converts selected properties of the object to a concatenated string of their string representations, separated by newlines.
        If to_string_keys is specified, only those properties are included; otherwise, all properties are included.
        
        :return: str, the newline-separated string representation of selected properties.
        """
        if hasattr(self, 'to_string_keys') and self.to_string_keys:
            properties_to_convert = [self.properties[key] for key in self.to_string_keys if key in self.properties]
        else:
            properties_to_convert = self.properties.values()
        return '\n'.join([value.to_string() for value in properties_to_convert])
        
VariableTypes = Union[Variable, ArrayVariable, ObjectVariable]

def create_variable_from_dict(data: Dict[str, Any]) -> VariableTypes:
    """
    Creates a VariableTypes object from a dictionary.

    :param data: Dict[str, Any], a dictionary representing a VariableTypes object.
    :return: VariableTypes, an instance of Variable, ArrayVariable, or ObjectVariable.
    """
    kwargs = {"name": data["name"]}
    if "display_name" in data:
        kwargs["display_name"] = data["display_name"]
    if "required" in data:
        kwargs["required"] = data["required"]
    if data["type"] == "string" and "max_length" in data:
        kwargs["max_length"] = data["max_length"]
    if data["type"] == "object":
        if "to_string_keys" in data:
            kwargs["to_string_keys"] = data["to_string_keys"]
        obj_var = ObjectVariable(**kwargs)
        for key, value in data.get("properties", {}).items():
            obj_var.add_property(key, create_variable_from_dict(value))
        return obj_var
    elif data["type"].startswith("array"):
        kwargs["type"] = data["type"]
        arr_var = ArrayVariable(**kwargs)
        for value in data.get("values", []):
            arr_var.add_value(create_variable_from_dict(value))
        return arr_var
    else:
        kwargs["type"] = data["type"]
        return Variable(**kwargs, value=data.get("value"))
    
def validate_required_variable(variable: VariableTypes):
    """
    Validates that all required variables have values. If a required variable has no value, raises a ValueError.

    :param variable: VariableTypes, an instance of Variable, ArrayVariable, or ObjectVariable.
    :raises ValueError: If a required variable has no value.
    """
    if isinstance(variable, Variable):
        if getattr(variable, 'required', False) and (variable.value is None or variable.value == ''):
            raise ValueError(f"Required variable '{variable.name}' has no value.")
    elif isinstance(variable, ArrayVariable):
        for value in variable.values:
            validate_required_variable(value)
    elif isinstance(variable, ObjectVariable):
        for value in variable.properties.values():
            validate_required_variable(value)
    
def replace_value_in_variable(
    original_variable: Variable,
    context_variable: VariableTypes,
    node_id: str,
    source: str,
    var_name: str,
    duplicate_braces: bool = False,
    replace_type: bool = True
):
    """
    Replaces the value of the original variable with the value from the context variable
    if the names match and the types are compatible.

    Parameters:
    - original_variable: The variable whose value is to be replaced.
    - context_variable: The variable from the context that potentially contains the new value.
    - node_id: The unique identifier of the node in the workflow.
    - source: The source of the variable value in the node (inputs|outputs).
    - var_name: The name of the variable whose value is to be replaced.
    - duplicate_braces: Whether to duplicate braces in the variable value.
    - replace_type: Whether to replace the type of the original variable with the context variable's type.

    Returns:
    None. The function directly modifies the original_variable's value.
    """
    if var_name == context_variable.name:
        if original_variable.type in ["string", "file", "json"]:
            if replace_type and context_variable.type in ["file", "json"]:
                original_variable.type = context_variable.type
            variable_string = context_variable.to_string()
            if duplicate_braces:
                variable_string = variable_string.replace("{", "{{").replace("}", "}}")
            original_variable.value = original_variable.value.replace(
                f"<<{node_id}.{source}.{var_name}>>",
                variable_string
            )
        elif original_variable.type == "number":
            if context_variable.type == "number":
                original_variable.value = context_variable.value
            else:
                raise ValueError(f"Variable '{original_variable.name}' type '{original_variable.type}' does not match the replacement variable '{context_variable.name}' type '{context_variable.type}'")
    elif isinstance(context_variable, ArrayVariable) or isinstance(context_variable, ObjectVariable):
        for value in (context_variable.values if isinstance(context_variable, ArrayVariable) else context_variable.properties.values()):
            replace_value_in_variable(original_variable, value, node_id, source, var_name, duplicate_braces, replace_type)

def replace_value_in_variable_with_new_value(
    variable: Union[Variable, ArrayVariable, ObjectVariable],
    new_value: Dict
):
    """
    Replaces the value of a variable with a new value.
    
    Parameters:
    - variable: The variable whose value is to be replaced. Can be a Variable, ArrayVariable, or ObjectVariable.
    - new_value: The new value to set. Can be any type.
    """
    def _replace(
        variable: Union[Variable, ArrayVariable, ObjectVariable],
        new_value: Any
    ):
        if isinstance(variable, Variable):
            # For simple variables, check if new_value is a dict and contains the variable name
            if variable.type == 'json':
                new_value = json.dumps(new_value, ensure_ascii=False)
            variable.value = new_value
        elif isinstance(variable, ArrayVariable):
            # For array variables, recursively update each value in the array
            for value in variable.values:
                _replace(value, new_value[value.name])
        elif isinstance(variable, ObjectVariable):
            # For object variables, recursively update each property value
            for value in variable.properties.values():
                _replace(value, new_value[value.name])

    if isinstance(variable, Variable):
        if variable.type == 'json':
            new_value[variable.name] = json.dumps(new_value[variable.name], ensure_ascii=False)
        variable.value = new_value[variable.name]
    else:
        _replace(variable, new_value)
            
def get_first_variable_value(variable: VariableTypes) -> Any:
    """
    Retrieves the value of a single Variable object. If the input is an ArrayVariable or ObjectVariable,
    it retrieves the value of the first Variable object contained within.

    :param variable: VariableTypes, the variable object from which to retrieve the value.
    :return: Any, the value of the first Variable object.
    """
    if isinstance(variable, Variable):
        return variable.value
    elif isinstance(variable, ArrayVariable) and variable.values:
        return get_first_variable_value(variable.values[0])
    elif isinstance(variable, ObjectVariable) and variable.properties:
        first_key = next(iter(variable.properties))
        return get_first_variable_value(variable.properties[first_key])
    else:
        return None
            
def flatten_variable(variable: VariableTypes) -> Dict[str, Tuple[str, str, bool]]:
    """
    Flattens a Variable, ArrayVariable, or ObjectVariable into a one-dimensional dictionary.
    The keys are the 'name' attributes of the innermost Variable objects, and the values are tuples
    where the first element is the string representation of the variable's type attribute, the second element is the display_name attribute,
    and the third element is the required attribute.

    :param variable: VariableTypes, the variable object to flatten.
    :return: Dict[str, Tuple[str, str, bool]], a one-dimensional dictionary representation of the variable object.
    """
    flat_dict = {}

    def _flatten(var: VariableTypes):
        if isinstance(var, Variable):
            flat_dict[var.name] = (
                'number' if var.type == 'number' else 'string', 
                getattr(var, 'display_name', ''),
                getattr(var, 'required', False)
            )
        elif isinstance(var, ArrayVariable):
            for item in var.values:
                _flatten(item)
        elif isinstance(var, ObjectVariable):
            for prop in var.properties.values():
                _flatten(prop)

    _flatten(variable)
    return flat_dict

def flatten_variable_with_values(variable: VariableTypes) -> Dict:
    """
    Flattens a Variable, ArrayVariable, or ObjectVariable into a dictionary.
    The keys are the 'name' attributes of the innermost Variable objects, and the values are values of the objects.

    :param variable: VariableTypes, the variable object to flatten.
    :return: Dict[str, Any], a dictionary representation of the variable object.
    """

    def _flatten(var: VariableTypes) -> Any:
        if isinstance(var, Variable):
            if var.type == 'json':
                var.value = json.loads(var.value)
            return var.value
        elif isinstance(var, ArrayVariable):
            flat_dict = {}
            for item in var.values:
                flat_dict[item.name] = _flatten(item)
            return flat_dict
        elif isinstance(var, ObjectVariable):
            flat_dict = {}
            for prop in var.properties.values():
                flat_dict[prop.name] = _flatten(prop)
            return flat_dict

    if isinstance(variable, Variable):
        if variable.type == 'json':
            variable.value = json.loads(variable.value)
        return {variable.name: variable.value}
    else:
        return _flatten(variable)

def unflatten_dict_with_values(input_data: Dict[str, Union[int, float, str]], name: str) -> ObjectVariable:
    """
    Unflattens a one-dimensional dictionary into a ObjectVariable 

    :param input_data: Dict[str, Union[int, float, str]]), a dictionary representation of the variable object.
    :return: ObjectVariable, the variable object after unflattening.
    """
    object_variable = ObjectVariable(name=name)
    for key, value in input_data.items():
        if isinstance(value, str):
            variable = Variable(name=key, type='string', value=value)
        else:
            variable = Variable(name=key, type='number', value=value)
        object_variable.add_property(key, variable)
    return object_variable

def convert_to_fastapi_model(model_name: str, variable: VariableTypes) -> Type[BaseModel]:
    """
    Converts a Variable, ArrayVariable, or ObjectVariable to a FastAPI parameter model using Pydantic.

    :param model_name: str, the name of the Pydantic model class to create.
    :param variable: VariableTypes, the variable object to flatten and convert.
    :return: Type[BaseModel], a Pydantic model class representing the FastAPI parameters.
    """
    flattened_vars = flatten_variable(variable)
    input_data_fields = {}
    
    for var_name, (var_type, display_name, required) in flattened_vars.items():
        field_info = Field(... if required else None, title=display_name, description=f"{display_name} ({var_type})")
        if var_type == 'number':
            input_data_fields[var_name] = (Union[int | float], field_info)
        else:
            input_data_fields[var_name] = (str, field_info)
    
    # Create a Pydantic model class with the dynamically created fields
    InputDataModel = create_model(f'{model_name}InputDataModel', **input_data_fields)
    InputModel = create_model(
        f'{model_name}InputModel',
        input_data=(InputDataModel, Field(..., title='Input Data', description='Input Data'))
    )
    return InputModel