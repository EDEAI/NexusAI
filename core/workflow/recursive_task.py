import re
from typing import Dict, List, Optional, Any
from collections import defaultdict

class RecursiveTaskCategory:
    """
    A class to represent a single category with potential subcategories.
    """
    
    def __init__(
        self, 
        id: str,
        name: str, 
        description: str = "", 
        keywords: str = "",
        task: Optional[str] = None,
    ):
        """
        Initializes a RecursiveTaskCategory object.
        
        :param id: The unique identifier of the category.
        :param name: The name of the category.
        :param description: The description of the category.
        :param keywords: The keywords associated with the category.
        :param task: The task associated with the category.
        """
        self.id = id
        self.name = name
        self.description = description
        self.keywords = keywords
        self.task = task
        self.subcategories: List['RecursiveTaskCategory'] = []
        
    def add_subcategory(self, subcategory: 'RecursiveTaskCategory') -> None:
        """
        Adds a subcategory to the current category.
        
        :param subcategory: The subcategory to add.
        """
        self.subcategories.append(subcategory)
        
    def to_dict(self, exclude_subcategories: bool = False, first_level_only: bool = False) -> Dict[str, Any]:
        """
        Converts the category to a dictionary.
        
        :param exclude_subcategories: Whether to exclude subcategory data. Defaults to False.
        :param first_level_only: Whether to include only the first level of subcategories. Defaults to False.
        :return: A dictionary representing the category.
        """
        category_dict = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "keywords": self.keywords,
            "task": self.task,
        }
        if not exclude_subcategories:
            if first_level_only:
                category_dict["subcategories"] = [sub.to_dict(exclude_subcategories=True) for sub in self.subcategories]
            else:
                category_dict["subcategories"] = [sub.to_dict() for sub in self.subcategories]
        return category_dict
        
    def get_next_task(self, ignored_ids: List[str] = []) -> Optional[Dict[str, Any]]:
        """
        Gets the next RecursiveTaskCategory object in a depth-first manner, ignoring specified task IDs.
        Also returns the parent category of the found category and the task's level.
        
        :param ignored_ids: A list of task IDs to ignore.
        :return: A dictionary with the found RecursiveTaskCategory object, its parent, and its level, or None if not found.
        """
        def _get_next_task(category, parent, level):
            # Check if current task should be skipped
            should_skip_current = (
                category.id in ignored_ids or
                (
                    category.id == 'task-root' and 
                    category.description.strip() == '' and
                    category.keywords.strip() == ''
                )
            )
            
            if not should_skip_current:
                return {"current": category, "parent": parent, "level": level}
            
            for subcategory in category.subcategories:
                result = _get_next_task(subcategory, category, level + 1)
                if result:
                    return result
            
            return None
        
        return _get_next_task(self, None, 0)
    
    def update_task(self, task_id: str, new_task: str) -> None:
        """
        Updates the task content for the category with the specified task ID.
        
        :param task_id: The ID of the task to update.
        :param new_task: The new task content to set.
        """
        if self.id == task_id:
            self.task = new_task
            return
        
        for subcategory in self.subcategories:
            subcategory.update_task(task_id, new_task)
    
    def to_markdown(self, level: int = 0) -> str:
        """
        Converts the category to a markdown string.
        
        :param level: The current level in the hierarchy, used for indentation. Defaults to 0.
        :return: A markdown string representing the category.
        """
        max_heading_level = 6
        heading_tag = f"h{min(level + 1, max_heading_level)}"
        markdown = f"<{heading_tag}>{self.name}</{heading_tag}>\n\n"
        markdown += f"**ID:** {self.id}\n\n"
        if self.description:
            markdown += f"**Description:** {self.description}\n\n"
        if self.task:
            markdown += f"**Task:** {self.task}\n\n"
        if self.keywords:
            markdown += f"**Keywords:** {self.keywords}\n\n"
        for subcategory in self.subcategories:
            subcategory_markdown = subcategory.to_markdown(level + 1)
            markdown += f"<blockquote>{subcategory_markdown}</blockquote>\n"
        return markdown

def create_recursive_task_category_from_dict(category_dict: Dict[str, Any]) -> RecursiveTaskCategory:
    """
    Create a RecursiveTaskCategory object from a dictionary.
    
    :param category_dict: A dictionary representing a recursive task category.
    :return: An instance of RecursiveTaskCategory populated with the provided data.
    """
    category = RecursiveTaskCategory(
        id=category_dict["id"],
        name=category_dict["name"], 
        description=category_dict["description"],
        keywords=category_dict.get("keywords", ""),
        task=category_dict.get("task"),
    )
    for subcategory_dict in category_dict.get("subcategories", []):
        subcategory = create_recursive_task_category_from_dict(subcategory_dict)
        category.add_subcategory(subcategory)
    return category

def merge_recursive_task_categories(category_dicts: List[Dict[str, Any]]) -> RecursiveTaskCategory:
    """
    Merges multiple RecursiveTaskCategory dictionaries into a single RecursiveTaskCategory object.
    
    :param category_dicts: A list of dictionaries representing recursive task categories.
    :return: A merged RecursiveTaskCategory object.
    """
    def flatten_categories(category_dict: Dict[str, Any], parent_id: Optional[str] = None):
        """
        Recursively flattens categories and stores parent-child relationships.
        
        :param category_dict: The category dictionary to flatten.
        :param parent_id: The id of the parent category.
        """
        category_id = category_dict["id"]
        category_map[category_id] = RecursiveTaskCategory(
            id=category_id,
            name=category_dict["name"],
            description=category_dict["description"],
            keywords=category_dict.get("keywords", ""),
            task=category_dict["task"]
        )
        if category_id not in parent_child_map[parent_id]:
            parent_child_map[parent_id].append(category_id)
        for subcategory_dict in category_dict["subcategories"]:
            flatten_categories(subcategory_dict, category_id)
    
    def build_category_tree(root_id: str) -> RecursiveTaskCategory:
        """
        Recursively builds the category tree from the flattened categories.
        
        :param root_id: The id of the root category.
        :return: A RecursiveTaskCategory object representing the root category.
        """
        root_category = category_map[root_id]
        for child_id in parent_child_map[root_id]:
            child_category = build_category_tree(child_id)
            root_category.add_subcategory(child_category)
        return root_category
    
    # Flatten all categories and store parent-child relationships
    category_map = {}
    parent_child_map = defaultdict(list)
    for category_dict in category_dicts:
        flatten_categories(category_dict)
    
    # The first category in the list is the root category
    root_id = category_dicts[0]["id"]
    
    # Build and return the category tree
    return build_category_tree(root_id)