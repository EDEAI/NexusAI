from typing import Dict, Any, Optional

from core.database import MySQL


class Users(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    table_name = "users"
    """
    Indicates whether the `users` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def search_my_team_all_agents(self, uid: int, level: int = 0, user_ids=None, all_agents=None):
        if level == 0:
            # 在初始调用时定义并初始化 all_agents 列表
            all_agents = []
            conditions = [
                {'column': 'id', 'value': uid},
                {'column': 'status', 'value': 1},
            ]
        else:
            conditions = [
                {'column': 'status', 'value': 1},
                {"column": "inviter_id", "op": "in", "value": user_ids}
            ]

        level += 1  # 增加层级深度信息

        # 当前层级查询
        datasets = self.select(
            columns=['id AS user_id'],
            conditions=conditions,
        )

        if datasets:
            # 提取 user_id 生成新的列表
            user_id = [item['user_id'] for item in datasets]
            all_agents = all_agents + user_id
            # 递归调用并返回结果
            return self.search_my_team_all_agents(uid, level, user_id, all_agents)
        else:
            # 返回结果
            filtered_list = [x for x in all_agents if x != uid]
            return filtered_list

    # Get the role of the user
    def get_user_id_role(self, user_id: int) -> bool:
        role = self.select_one(columns="*", conditions=[{'column': 'id', 'value': user_id}])
        print(role)
        if role['role'] != 1:
            return False
        return True

    def get_user_language(self, user_id: int) -> str:
        """
        Get the current language of the user by user ID.

        :param user_id: The ID of the user.
        :return: The current language of the user.
        """
        user = self.select_one(columns=["language"], conditions={'column': 'id', 'value': user_id})
        if user:
            return user['language']
        else:
            raise ValueError(f"User with ID {user_id} not found")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = self.select_one(
            columns=['team_id', 'id', 'nickname'],
            conditions=[
                {'column': 'id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ]
        )
        return user
