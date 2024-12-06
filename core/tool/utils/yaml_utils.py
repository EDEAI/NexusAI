import logging
from typing import Any

import yaml
from yaml import YAMLError

# Initialize logger for this module
logger = logging.getLogger(__name__)

def load_yaml_file(file_path: str, ignore_error: bool = True, default_value: Any = {}) -> Any:
    """
    Safely load a YAML file.

    :param file_path: The path of the YAML file.
    :param ignore_error: 
        If True, return default_value if an error occurs and log the error at debug level.
        If False, raise an error if an error occurs.
    :param default_value: The value returned when errors are ignored.
    :return: An object representing the YAML content.
    """
    try:
        # Open the YAML file with UTF-8 encoding
        with open(file_path, encoding='utf-8') as yaml_file:
            try:
                # Load the YAML content safely
                yaml_content = yaml.safe_load(yaml_file)
                # Return the loaded content or the default value if content is None
                return yaml_content if yaml_content else default_value
            except Exception as e:
                # Raise a YAML error with a descriptive message
                raise YAMLError(f'Failed to load YAML file {file_path}: {e}')
    except Exception as e:
        if ignore_error:
            # Log the error at debug level and return the default value
            logger.debug(f'Failed to load YAML file {file_path}: {e}')
            return default_value
        else:
            # Raise the original exception
            raise e