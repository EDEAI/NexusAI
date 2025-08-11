import json
from typing import Any, Dict, List

def process_dict(d: Dict[str, Any], max_length: int) -> Dict[str, Any]:
    """
    Process dictionary to ensure its JSON string representation does not exceed max_length
    :param d: Input dictionary
    :param max_length: Maximum length limit
    :return: Processed dictionary
    """
    def truncate_string(s: str, length: int) -> str:
        """Truncate string and add ellipsis at the end"""
        if len(s) <= length:
            return s
        return s[:length-3] + '...'
    
    def process_value(value: Any) -> Any:
        """Recursively process values in dictionary"""
        if isinstance(value, dict):
            # Process dictionary, keep all fields, only process values
            return {k: process_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Process array, can discard entire array elements, end elements are prioritized for discard
            # Here we try to keep the array, but gradually discard end elements if length exceeds limit
            new_list = [process_value(item) for item in value]
            return new_list
        elif isinstance(value, str):
            # Process string, can be truncated
            return truncate_string(value, max_length)
        else:
            # Other types remain unchanged
            return value
    
    # Initial processing
    current_length = len(json.dumps(d, ensure_ascii=False))
    if current_length <= max_length:
        return d
    processed_dict = process_value(d)
    
    # Check length and adjust
    current_length = len(json.dumps(d, ensure_ascii=False))
    while current_length > max_length:
        # If length exceeds limit, try to reduce array elements
        # Start from outermost layer, gradually process inward
        def reduce_list(lst: List[Any]) -> List[Any]:
            """Reduce array elements"""
            if len(lst) > 1:
                return lst[:-1]  # Discard the last element
            else:
                return []  # Return empty array if only one element or empty
        
        def adjust_dict(d: Dict[str, Any]) -> None:
            """Adjust array elements in dictionary"""
            for k, v in d.items():
                if isinstance(v, list):
                    d[k] = reduce_list(v)
                elif isinstance(v, dict):
                    adjust_dict(v)
        
        adjust_dict(processed_dict)
        
        # If arrays are already empty but still exceeds limit, further process strings
        if len(json.dumps(processed_dict, ensure_ascii=False)) > max_length:
            # Further truncate strings
            def further_truncate(value: Any) -> Any:
                if isinstance(value, dict):
                    return {k: further_truncate(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [further_truncate(item) for item in value]
                elif isinstance(value, str):
                    # Further reduce string length
                    if len(value) > 4095:
                        return truncate_string(value, len(value) - 128)
                    else:
                        return value
                else:
                    return value
            
            processed_dict = further_truncate(processed_dict)
        new_length = len(json.dumps(processed_dict, ensure_ascii=False))
        if new_length == current_length:
            # No more space to reduce, break out of loop
            break
        current_length = new_length
    
    return processed_dict
