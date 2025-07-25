import sys, os
from pathlib import Path
from datetime import datetime
import hashlib

sys.path.append(str(Path(__file__).absolute().parent.parent))
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from core.database.models.teams import Teams
from core.database.models.users import Users
from core.database.models.user_team_relations import UserTeamRelations
from core.database.models.model_configurations import ModelConfigurations


def create_team(team_name, account, password):
    """
    Method to create a team
    
    Parameters:
    team_name: Team name
    account: Account
    password: Password
    """
    
    # Parameter validation
    if not team_name or team_name.strip() == "":
        print("Error: Team name cannot be empty")
        sys.exit(1)
    
    if not account or account.strip() == "":
        print("Error: Account cannot be empty")
        sys.exit(1)
    
    if not password or password.strip() == "":
        print("Error: Password cannot be empty")
        sys.exit(1)
    
    # Check if account already exists
    existing_user = Users().select_one(
        columns=['id'],
        conditions=[
            {'column': 'email', 'value': account.strip()},
            {'column': 'status', 'value': 1}
        ]
    )
    
    if existing_user:
        print(f"Error: Account '{account.strip()}' already exists, cannot create duplicate account")
        sys.exit(1)
    
    try:
        current_time = datetime.now()
        
        # 1. Insert into teams table
        team_data = {
            'name': team_name.strip(),
            'type': 1,
            'created_time': current_time,
            'status': 1
        }
        print(f"Creating team: {team_data}")
        team_id = Teams().insert(team_data)
        
        if not team_id:
            print("Error: Failed to create team")
            sys.exit(1)
        
        print(f"Successfully created team, Team ID: {team_id}")
        
        # 2. Create user and insert into users table
        # Generate password salt (using timestamp as salt, consistent with auth.py validation logic)
        password_salt = str(int(current_time.timestamp()))
        
        # Use the same encryption method as fake_hash_password in auth.py: MD5(MD5(password) + salt)
        password_with_salt = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + password_salt).encode()).hexdigest()
        
        user_data = {
            'team_id': team_id,
            'role': 1,
            'inviter_id': 0,
            'email': account.strip(),
            'nickname':'administrator',
            'password': password_with_salt,
            'password_salt': password_salt,
            'created_time': current_time,
            'status': 1,
            'language': 'zh'
        }
        print(f"Creating user: {user_data}")
        user_id = Users().insert(user_data)
        
        if not user_id:
            print("Error: Failed to create user")
            sys.exit(1)
        
        print(f"Successfully created user, User ID: {user_id}")
        
        # 3. Insert into user_team_relations table
        relation_data = {
            'user_id': user_id,
            'team_id': team_id,
            'role': 1,
            'inviter_id': 0,
            'created_time': current_time
        }
        print(f"Creating user-team relationship: {relation_data}")
        relation_id = UserTeamRelations().insert(relation_data)
        
        if not relation_id:
            print("Error: Failed to create user-team relationship")
            sys.exit(1)
        
        print("Successfully created user-team relationship")
        
        # 4. Copy model configurations
        # Query all model configurations with team_id=1
        model_configs = ModelConfigurations().select(
            columns=['model_id', 'config', 'default_used', 'sort_order'],
            conditions=[
                {'column': 'team_id', 'value': 1},
                {'column': 'status', 'value': 1}
            ]
        )
        
        if model_configs:
            print(f"Copying {len(model_configs)} model configurations")
            
            # Batch insert model configurations for new team
            for config in model_configs:
                model_config_data = {
                    'team_id': team_id,
                    'model_id': config['model_id'],
                    'config': config['config'],
                    'default_used': config['default_used'],
                    'sort_order': config['sort_order'],
                    'created_time': current_time,
                    'updated_time': None,
                    'status': 1
                }
                
                model_config_id = ModelConfigurations().insert(model_config_data)
                if not model_config_id:
                    print(f"Warning: Failed to copy model configuration, model_id: {config['model_id']}")
            
            print(f"Successfully copied model configurations")
        else:
            print("Warning: No model configurations found to copy")
        
        print(f"Team '{team_name}' created successfully!")
        
    except Exception as e:
        print(f"Error occurred while creating team: {e}")
        sys.exit(1)


# Usage example
if __name__ == "__main__":
    # Can be called via command line arguments or direct function call
    if len(sys.argv) == 4:
        team_name = sys.argv[1]
        account = sys.argv[2]
        password = sys.argv[3]
        create_team(team_name, account, password)
    else:
        print("Usage: python create_team.py <team_name> <account> <password>")
        print("Example: python create_team.py 'Test Team' 'admin@example.com' '123456'")
        # Or call function directly for testing
        # create_team("Test Team", "admin@example.com", "123456")