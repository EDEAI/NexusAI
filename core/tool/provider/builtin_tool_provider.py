# builtin_tool_provider.py

import os
from importlib import util
from typing import AnyStr, Type
from core.tool.errors import ToolProviderNotFoundError, ToolCertificateVerification
from core.tool.utils.yaml_utils import load_yaml_file
from config import settings
from typing import Any


class BuiltinTool:
    """
    Base class for all built-in tool.
    """

    def __init__(self, credentials: dict):
        self.credentials = credentials

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the provided credentials. Override in subclasses.
        """
        pass  # Default is no-op

    def _invoke(self, tool_parameters: dict[str, Any]) -> Any:
        """
        This should be overridden by subclasses to provide specific invoke logic.
        """
        raise NotImplementedError("Subclasses should implement this method")

    def invoke(self, tool_parameters: dict[str, Any]) -> Any:
        """
        Validate credentials and then invoke the tool.
        """
        self._validate_credentials(self.credentials)
        return self._invoke(tool_parameters)


# Helper functions for dynamic module loading
def load_single_subclass_from_source(
        module_name: str,
        script_path: AnyStr,
        parent_type: Type,
        use_lazy_loader: bool = False,
) -> Type:
    """
    Load a single subclass from the source.
    """
    module = import_module_from_source(module_name, script_path, use_lazy_loader)
    subclasses = get_subclasses_from_module(module, parent_type)

    # Print debug information to show all found subclasses
    print(f"Found subclasses in {module_name}: {[cls.__name__ for cls in subclasses]}")

    match len(subclasses):
        case 1:
            return subclasses[0]
        case 0:
            raise Exception(f'Missing subclass of {parent_type.__name__} in {script_path}')
        case _:
            raise Exception(f'Multiple subclasses of {parent_type.__name__} in {script_path}')


def import_module_from_source(module_name: str, script_path: AnyStr, use_lazy_loader: bool = False) -> Any:
    """
    Helper function to import a module from a source file.
    """
    spec = util.spec_from_file_location(module_name, script_path)
    if spec is None:
        raise ImportError(f"Cannot find module '{module_name}' at path '{script_path}'")

    module = util.module_from_spec(spec)
    if not use_lazy_loader and spec.loader is not None:
        spec.loader.exec_module(module)
    elif use_lazy_loader and hasattr(spec.loader, 'lazy_load'):
        spec.loader.lazy_load(module_name, globals(), module)

    return module


def get_subclasses_from_module(module: Any, parent_type: Type) -> list:
    """
    Helper function to get subclasses of a given parent type from a module.
    """
    return [
        cls for cls in module.__dict__.values()
        if isinstance(cls, type) and issubclass(cls, parent_type) and cls is not parent_type
    ]


# Dynamic loading functions
def load_provider_class(provider: str, parent_type: Type) -> Type:
    """
    Load a specific provider class.
    """
    module_name = f'core.tool.provider.builtin.{provider}.{provider}'
    script_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'builtin', provider, f'{provider}.py'
    )
    return load_single_subclass_from_source(module_name, script_path, parent_type)


def load_tool_class(provider: str, tool_name: str, parent_type: Type) -> Type:
    """
    Load a specific tool class based on the provider and tool name.
    """
    module_name = f'core.tool.provider.builtin.{provider}.tool.{tool_name}'
    script_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'builtin', provider, 'tool', f'{tool_name}.py'
    )
    return load_single_subclass_from_source(module_name, script_path, parent_type)


# Functions to get provider and tool information
def get_tool_providers() -> dict[str, Any]:
    """
    Get all tool provider configuration information.
    :return: A dictionary containing all provider configurations.
    """
    # Define the base path for the built-in tool providers.
    builtin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'builtin')
    providers = {}
    # Iterate through all subdirectories within the builtin directory.
    for provider in os.listdir(builtin_path):
        provider_dir = os.path.join(builtin_path, provider)

        # Ensure the current item is a directory.
        if os.path.isdir(provider_dir):
            yaml_path = os.path.join(provider_dir, f"{provider}.yaml")

            # Check if the YAML file exists for the provider.
            if os.path.exists(yaml_path):
                try:
                    provider_yaml = load_yaml_file(yaml_path, ignore_error=False)

                    # Set the name field in the credentials_for_provider section.
                    if 'credentials_for_provider' in provider_yaml and provider_yaml[
                        'credentials_for_provider'] is not None:
                        for credential_name, credential_info in provider_yaml['credentials_for_provider'].items():
                            credential_info['name'] = credential_name

                    # Add the provider configuration to the providers dictionary.
                    providers[provider] = provider_yaml
                except Exception as e:
                    # Raise an exception if the YAML file cannot be loaded.
                    raise ToolProviderNotFoundError(f'Cannot load provider YAML for {provider}: {e}')
            else:
                # Raise an exception if the YAML file is missing for the provider.
                raise ToolProviderNotFoundError(f'YAML file missing for provider {provider} in {provider_dir}')

    return providers


def get_tools(provider: str) -> list[Any]:
    """
    Returns a list of tool that the specified provider can provide.
    :param provider: The name of the tool provider.
    :return: list of tool
    """
    tool_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "builtin", provider, "tool")
    print(f"Looking for tool in directory: {tool_dir}")

    if not os.path.exists(tool_dir):
        raise FileNotFoundError(f"Tool directory not found: {tool_dir}")

    # Get all the YAML files in the tool path
    tool_files = list(filter(lambda x: x.endswith(".yaml") and not x.startswith("__"), os.listdir(tool_dir)))

    tools = []
    for tool_file in tool_files:
        tool_path = os.path.join(tool_dir, tool_file)
        provider_yaml = load_yaml_file(tool_path, ignore_error=False)
        tools.append(provider_yaml)
    return tools


# Validation and usage functions
def validate_credentials(provider: str, credentials: dict, parent_type: Type = BuiltinTool) -> bool:
    """
    Validate the credentials for a specific provider.
    This loads a validation tool if exists and checks the credentials.
    :param provider: Name of the tool provider.
    :param credentials: Credentials for authorization.
    :param parent_type: Parent class type.
    :return: bool indicating if credentials are valid.
    """
    try:
        provider_cls = load_provider_class(provider, parent_type)
        provider_instance = provider_cls(credentials)
        return provider_instance.validate()  # This should return True if validation is successful
    except (ImportError, ToolProviderNotFoundError, ToolCertificateVerification) as e:
        print(f"Validation failed for provider {provider}: {str(e)}")
        return False


def use_tool(provider: str, tool_name: str, credentials: dict, parameters: dict,
             parent_type: Type = BuiltinTool) -> Any:
    """
    Load and use a tool.
    :param provider: Name of the tool provider.
    :param tool_name: Name of the tool.
    :param credentials: Credentials for authorization.
    :param parameters: Parameters for tool invocation.
    :param parent_type: Parent class type.
    :return: Result of the tool invocation.
    """
    tool_cls = load_tool_class(provider, tool_name, parent_type)
    tool_instance = tool_cls(credentials)
    if hasattr(tool_instance, 'validate'):
        tool_instance.validate()  # Validate credentials if method exists
    return tool_instance.invoke(parameters)


def get_tool_providers_with_tools() -> dict[str, Any]:
    """
    Get all tool provider configuration information along with their tools.
    :return: A dictionary containing all provider configurations and tools.
    """
    # Define the base path for the built-in tool providers.
    builtin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'builtin')
    providers = {}  # Iterate through all subdirectories within the builtin directory.
    for provider in os.listdir(builtin_path):
        provider_dir = os.path.join(builtin_path, provider)

        # Ensure the current item is a directory.
        if os.path.isdir(provider_dir):
            yaml_path = os.path.join(provider_dir, f"{provider}.yaml")

            # Check if the YAML file exists for the provider.
            if os.path.exists(yaml_path):
                try:
                    provider_yaml = load_yaml_file(yaml_path, ignore_error=False)
                    provider_yaml['identity']['icon'] = f"{settings.ICON_URL}/tool_icon/{provider_yaml['identity']['icon']}"
                    # Set the name field in the credentials_for_provider section.
                    if 'credentials_for_provider' in provider_yaml and provider_yaml[
                        'credentials_for_provider'] is not None:
                        for credential_name, credential_info in provider_yaml['credentials_for_provider'].items():
                            credential_info['name'] = credential_name
                    # Add the tools information
                    tool_dir = os.path.join(provider_dir, "tool")
                    print(f"Looking for tools in directory: {tool_dir}")

                    if os.path.exists(tool_dir):
                        # Get all the YAML files in the tool path
                        tool_files = list(
                            filter(lambda x: x.endswith(".yaml") and not x.startswith("__"), os.listdir(tool_dir)))

                        tools = []
                        for tool_file in tool_files:
                            tool_path = os.path.join(tool_dir, tool_file)
                            tool_yaml = load_yaml_file(tool_path, ignore_error=False)
                            tools.append(tool_yaml)

                        provider_yaml['tools'] = tools
                    else:
                        provider_yaml['tools'] = []
                    providers[provider] = provider_yaml

                except Exception as e:
                    # Raise an exception if the YAML file cannot be loaded.
                    raise ToolProviderNotFoundError(f'Cannot load provider YAML for {provider}: {e}')
            else:
                # Raise an exception if the YAML file is missing for the provider.
                raise ToolProviderNotFoundError(f'YAML file missing for provider {provider} in {provider_dir}')

    return providers
