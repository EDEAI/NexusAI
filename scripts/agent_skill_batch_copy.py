import pymysql


def main():
    src_agent_app_id = 100
    target_agent_llm_config_id = 50
    target_team_id = 10
    target_user_id = 21
    with (
        pymysql.Connection(
            host='localhost',
            port=3306,
            user='nexus_ai',
            password='mysqlpwd',
            database='nexus_ai',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        ) as connection,
        connection.cursor() as cursor
    ):
        # Copy Agent APP data
        cursor.execute(
            '''INSERT INTO apps (
                team_id, user_id, name, description, avatar, icon, icon_background,
                mode, enable_api, api_token, is_public, publish_status,
                attrs_are_visible, execution_times, created_time, updated_time, status
            )
            SELECT
                %s, %s, 
                name,
                description, avatar, icon, icon_background,
                mode, 0, NULL, is_public, publish_status,
                attrs_are_visible, 0, NOW(), NOW(), status
            FROM apps
            WHERE id = %s;''',
            [target_team_id, target_user_id, src_agent_app_id]
        )
        new_agent_app_id = cursor.lastrowid
        print('Copy Agent APP data', new_agent_app_id)
        input('>>>')


        # Copy Agent data
        new_agent_ids = []
        for publish_status in [0, 1]:
            cursor.execute(
                '''INSERT INTO agents (
                    team_id, user_id, app_id, obligations, input_variables, auto_match_ability,
                    default_output_format, model_config_id, allow_upload_file,
                    publish_status, created_time, updated_time, status
                )
                SELECT
                    %s, %s, %s,
                    obligations, input_variables, auto_match_ability,
                    default_output_format, %s, allow_upload_file,
                    %s, NOW(), NOW(), status
                FROM agents
                WHERE app_id = %s AND publish_status = 1;''',
                [target_team_id, target_user_id, new_agent_app_id, target_agent_llm_config_id, publish_status, src_agent_app_id]
            )
            new_agent_ids.append(cursor.lastrowid)
        print('Copy Agent data', len(new_agent_ids), new_agent_ids)
        input('>>>')

        # Find all bound Skills
        cursor.execute(
            '''SELECT app_id
            FROM agent_callable_items
            WHERE agent_id = (SELECT id FROM agents WHERE app_id = %s AND publish_status = 1)
            AND item_type = 1;''',
            [src_agent_app_id]
        )
        old_skills = cursor.fetchall()
        print('Find all bound Skills', len(old_skills), [old_skill['app_id'] for old_skill in old_skills])
        input('>>>')


        # Copy Skills data
        new_skill_app_ids = []
        new_custom_tool_ids = []
        for old_skill in old_skills:
            cursor.execute(
                '''INSERT INTO apps (
                    team_id, user_id, name, description, avatar, icon, icon_background,
                    mode, enable_api, api_token, is_public, publish_status,
                    attrs_are_visible, execution_times, created_time, updated_time, status
                )
                SELECT
                    %s, %s,
                    name, description, avatar, icon, icon_background,
                    mode, 0, NULL, is_public, publish_status,
                    attrs_are_visible, 0, NOW(), NOW(), status
                FROM apps
                WHERE id = %s;''',
                [target_team_id, target_user_id, old_skill['app_id']]
            )
            new_skill_app_id = cursor.lastrowid
            new_skill_app_ids.append(new_skill_app_id)
            for publish_status in [0, 1]:
                cursor.execute(
                    '''INSERT INTO custom_tools (
                        team_id, user_id, app_id, config, input_variables, dependencies, code,
                        output_type, output_variables, publish_status, created_time, updated_time, status
                    )
                    SELECT
                        %s, %s,
                        %s, config, input_variables, dependencies, code,
                        output_type, output_variables, %s, NOW(), NOW(), status
                    FROM custom_tools
                    WHERE app_id = %s AND publish_status = 1;''',
                    [target_team_id, target_user_id, new_skill_app_id, publish_status, old_skill['app_id']] 
                )
                new_custom_tool_ids.append(cursor.lastrowid)
        print('Copy Skills APP data', len(new_skill_app_ids), new_skill_app_ids)
        print('Copy Skills data', len(new_custom_tool_ids), new_custom_tool_ids)
        input('>>>')

        # Create new Agent-Skill binding data
        new_agent_callable_item_ids = []
        for new_skill_app_id in new_skill_app_ids:
            for new_agent_id in new_agent_ids:
                cursor.execute(
                    '''INSERT INTO agent_callable_items (
                        agent_id, app_id, item_type, created_time, updated_time
                    )
                    SELECT
                        %s, %s, 1, NOW(), NOW();''',
                    [new_agent_id, new_skill_app_id]
                )
                new_agent_callable_item_ids.append(cursor.lastrowid)
        print('Create new Agent-Skill binding data', len(new_agent_callable_item_ids), new_agent_callable_item_ids)
        input('>>>')
        
        connection.commit()

if __name__ == '__main__':
    main()
