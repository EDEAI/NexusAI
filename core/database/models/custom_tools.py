from typing import Any, Dict, List
from core.database import MySQL
from core.database.models.tag_bindings import TagBindings
from core.database.models.apps import Apps
from core.database.models import Users
import math
from datetime import datetime
from languages import get_language_content
from config import settings


class CustomTools(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "custom_tools"
    """
    Indicates whether the `custom_tools` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_skill_info(self, user_id: int, app_id: int, publish_status: int, team_id: int) -> Dict[str, Any]:
        apps_model = Apps()
        app = apps_model.select_one(
            columns=["id AS app_id", "user_id", "name", "description", "icon", "icon_background", "is_public", "attrs_are_visible",
                     "publish_status AS app_publish_status",
                     "enable_api", "created_time", "status"],
            conditions=[
                {"column": "id", "value": app_id},
                {"column": "team_id", "value": team_id},
                {"column": "mode", "value": 4},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not app:
            return {"status": 2, "message": "app error"}
        if app["user_id"] != user_id:
            if publish_status == 0:
                return {"status": 2, "message": "Only creators can view drafts"}
            if app["is_public"] == 0:
                return {"status": 2, "message": "Team members are not open"}
            if app["status"] != 1:
                return {"status": 2, "message": "The app status is not normal"}
        skill = self.select_one(columns='*',
                                conditions=[
                                    {"column": "app_id", "value": app_id},
                                    {"column": "team_id", "value": team_id},
                                    {"column": "publish_status", "value": publish_status},
                                    {"column": "status", "op": "in", "value": [1, 2]}
                                ])
        if not skill:
            return {'status': 2, 'message': 'Skill not found'}
        if skill["user_id"] != user_id and skill["status"] != 1:
            return {"status": 2, "message": "The skill status is not normal"}
        user_data = Users().select_one(columns='*', conditions=[{"column": "id", "value": skill['user_id']}])
        skill['name'] = app['name']
        skill['description'] = app['description']
        skill['attrs_are_visible'] = app['attrs_are_visible']
        skill['is_public'] = app['is_public']
        skill['nickname'] = user_data['nickname']
        skill['is_creator'] = 0 if app["user_id"] != user_id else 1
        skill['app_publish_status'] = app['app_publish_status']
        input_variables = skill['input_variables']
        skill_publish_status = skill['publish_status']
        if app["user_id"] != user_id and app["attrs_are_visible"] != 1:
            skill = {
                "name": app['name'],
                "description": app['description'],
                "is_public": app['is_public'],
                "attrs_are_visible": app['attrs_are_visible'],
                "team_id": team_id,
                "user_id": user_id,
                "app_id": app['app_id'],
                "nickname": user_data['nickname'],
                "publish_status": skill_publish_status,
                "is_creator": 0 if app["user_id"] != user_id else 1,
                "input_variables": input_variables,
                "app_publish_status": app["app_publish_status"],
                "created_time": skill["created_time"],
                "id": skill["id"],
                "published_time": skill["published_time"],
                "status": skill["status"],
                "updated_time": skill["updated_time"]
            }
            return {'status': 1, 'message': 'ok', 'data': skill}
        else:
            return {'status': 1, 'message': 'ok', 'data': skill}

    def get_publish_skill_info(self, user_id: int, app_id: int, publish_status: int) -> Dict[str, Any]:
        skill = self.select_one(columns='*', conditions=[
            {"column": "user_id", "value": user_id},
            {"column": "publish_status", "value": publish_status},
            {"column": "app_id", "value": app_id}

        ])
        if not skill:
            return {'status': 2, 'message': 'Skill not found'}
        return {'status': 1, 'message': 'ok', 'data': skill}

    def get_skill_by_id(self, skill_id: int):
        skill = self.select_one(columns='*',
                                conditions=[
                                    {"column": "id", "value": skill_id},
                                    {"column": "status", "value": 1}
                                ])
        return skill if skill else {}

    def skill_list(self, page: int = 1, page_size: int = 10, uid: int = 0, team_id: int = 0, skill_search_type: int = 1,
                   name: str = ""):
        if skill_search_type == 1:
            conditions = [
                {"column": "custom_tools.user_id", "value": uid},
                {"column": "custom_tools.publish_status", "value": 0},
                {"column": "custom_tools.status", "op": "in", "value": [1, 2]},
                {"column": "apps.mode", "value": 4},
                {"column": "apps.status", "op": "in", "value": [1, 2]}
            ]
        elif skill_search_type == 2:
            conditions = [
                {"column": "custom_tools.team_id", "value": team_id},
                {"column": "custom_tools.user_id", 'op': '!=', 'value': uid},
                {"column": "custom_tools.publish_status", "value": 1},
                {"column": "custom_tools.status", "value": 1},
                {"column": "apps.mode", "value": 4},
                {"column": "apps.is_public", "value": 1},
                {"column": "apps.status", "value": 1}
            ]
        else:
            conditions = [
                {"column": "custom_tools.user_id", "value": uid},
                {"column": "custom_tools.publish_status", "value": 1},
                {"column": "custom_tools.status", "value": 1},
                {"column": "apps.mode", "value": 4},
                {"column": "apps.status", "value": 1},
            ]
        if name:
            conditions.append({"column": "apps.name", "op": "like", "value": "%" + name + "%"})

        total_count = self.select(
            aggregates={"id": "count"},
            joins=[
                ["left", "apps", "custom_tools.app_id = apps.id"],
                ["left", "users", "custom_tools.user_id = users.id"]
            ],
            conditions=conditions,
        )[0]["count_id"]

        list = self.select(
            columns=["custom_tools.id AS skill_id", "custom_tools.app_id", "apps.name", "apps.description", "apps.icon", "apps.avatar",
                     "apps.icon_background", "users.nickname", "users.avatar"],
            joins=[
                ["left", "apps", "custom_tools.app_id = apps.id"],
                ["left", "users", "custom_tools.user_id = users.id"]
            ],
            conditions=conditions,
            order_by="custom_tools.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )
        if list:
            for item in list:
                # if item.get('avatar'):
                #     item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
                if item.get('avatar'):
                    if not item['avatar'].startswith(('http://', 'https://')):
                        item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

        return {
            "list": list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def skill_data_create(self, data, user_id: int, team_id: int) -> Dict[str, Any]:
        """
        Create or update skill data
        Args:
            data: Skill data dictionary containing configuration
            user_id: User ID creating/updating the skill
            team_id: Team ID for the skill
        Returns:
            Dict containing status and response data
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        app_model = Apps()
        app_id = data.get('app_id', None)
        if app_id:
            app_update_data = {
                "name": data.get('name'),
                "description": data.get('description'),
                "updated_time": current_time
            }
            app_model.update([{'column': 'id', 'value': app_id}], app_update_data)
            
            update_data = {
                "updated_time": current_time,
                "input_variables": data['input_variables'],
                "dependencies": data['dependencies'],
                "code": data['code'],
                "output_type": data['output_type'],
                "output_variables": data['output_variables']
            }
            
            conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id},
                          {'column': 'publish_status', 'value': 0}]
            self.update(conditions, update_data)
            
            
            update_data['published_time'] = current_time
            conditions_1 = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id},
                          {'column': 'publish_status', 'value': 1}]
            self.update(conditions_1,update_data)  
            # Handle tags
            tag_ids = data.get('tags', [])
            if tag_ids:
                tag_bindings = TagBindings()
                if not tag_bindings.batch_update_bindings([app_id], tag_ids):
                    return {"status": 2, "message": get_language_content("tag_binding_create_failed")}

            return {
                "status": 1,
                "message": get_language_content("skill_create_success"),
                "skill_id": 0,
                "app_id": app_id
            }
        # Create new app
        base_data = {
            "name": data.get('name'),
            "description": data.get('description'),
            "mode": 4,  # For skills
            "publish_status": 0,
            "team_id": team_id,
            "user_id": user_id,
            "created_time": current_time,
            "updated_time": current_time
        }

        app_id = app_model.insert(base_data)
        if not app_id:
            return {"status": 2, "message": get_language_content("apps_insert_error")}

        # Handle tags
        tag_ids = data.get('tags', [])
        if tag_ids:
            tag_bindings = TagBindings()
            if not tag_bindings.batch_update_bindings([app_id], tag_ids):
                return {"status": 2, "message": get_language_content("tag_binding_create_failed")}

        # create skill
        skill_data = {
            "team_id": team_id,
            "user_id": user_id,
            "app_id": app_id,
            "created_time": current_time,
            "updated_time": current_time,
            "input_variables": data['input_variables'],
            "dependencies": data['dependencies'],
            "code": data['code'],
            "output_type": data['output_type'],
            "output_variables": data['output_variables'],
        }
        skill_id = self.insert(skill_data)
        skill_data['publish_status'] = 1
        skill_data['published_time'] = current_time
        skill_id = self.insert(skill_data)
        apps_data = {
            "publish_status": 1,
            "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        app_model.update([{'column': 'id', 'value': app_id}], apps_data)
        return {
            "status": 1,
            "message": get_language_content("skill_create_success"),
            "skill_id": skill_id,
            "app_id": app_id
        }



