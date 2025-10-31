import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib
import json

sys.path.append(str(Path(__file__).absolute().parent.parent))
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from core.database.models.tenants import Tenants
from core.database.models.users import Users


def create_tenants(
    account,
    password,
    name,
    country,
    legal_name=None,
    notes=None,
    config=None,
    status=1
):
    """
    Method to create a tenant with administrator account
    
    Parameters:
    account: Administrator account (email) - Required
    password: Administrator password - Required
    name: Tenant display name - Required
    country: Company code - Required
    legal_name: Legal name - Optional
    notes: Notes - Optional
    config: Configuration dict - Optional
    status: Tenant status (0=Inactive, 1=Active, 2=Suspended, 3=Stopped, 4=Disabled, 5=Deleted) - Default: 1
    """
    
    # Parameter validation
    if not account or account.strip() == "":
        print("Error: Administrator account cannot be empty")
        sys.exit(1)
    
    if not password or password.strip() == "":
        print("Error: Administrator password cannot be empty")
        sys.exit(1)
    
    if not name or name.strip() == "":
        print("Error: Tenant name cannot be empty")
        sys.exit(1)
    
    if not country or country.strip() == "":
        print("Error: Country (company code) cannot be empty")
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
        
        # 1. Insert into tenants table
        tenant_data = {
            'name': name.strip(),
            'country': country.strip(),
            'status': status,
            'created_time': current_time
        }
        
        # Add optional fields
        if legal_name and legal_name.strip():
            tenant_data['legal_name'] = legal_name.strip()
        
        if notes and notes.strip():
            tenant_data['notes'] = notes.strip()
        
        if config:
            try:
                tenant_data['config'] = json.dumps(config)
            except Exception as e:
                print(f"Error: Invalid config format: {e}")
                sys.exit(1)
        
        print(f"Creating tenant: {tenant_data}")
        tenant_id = Tenants().insert(tenant_data)
        
        if not tenant_id:
            print("Error: Failed to create tenant")
            sys.exit(1)
        
        print(f"Successfully created tenant, Tenant ID: {tenant_id}")
        
        # 2. Create administrator user and insert into users table
        # Generate password salt (using timestamp as salt, consistent with auth.py validation logic)
        password_salt = str(int(current_time.timestamp()))
        
        # Use the same encryption method as fake_hash_password in auth.py: MD5(MD5(password) + salt)
        password_with_salt = hashlib.md5(
            (hashlib.md5(password.encode()).hexdigest() + password_salt).encode()
        ).hexdigest()
        
        user_data = {
            'team_id': 1,  # Default team_id, will be updated when team is created
            'role': 1,  # Administrator role
            'role_id': 1,
            'tenant_id': tenant_id,  # Associate with the created tenant
            'inviter_id': 0,
            'email': account.strip(),
            'nickname': 'administrator',
            'password': password_with_salt,
            'password_salt': password_salt,
            'created_time': current_time,
            'status': 1,
            'language': 'en'
        }
        print(f"Creating administrator user: {user_data}")
        user_id = Users().insert(user_data)
        
        if not user_id:
            print("Error: Failed to create administrator user")
            sys.exit(1)
        
        print(f"Successfully created administrator user, User ID: {user_id}")
        
        print(f"\nTenant '{name}' created successfully!")
        print(f"Tenant ID: {tenant_id}")
        print(f"Administrator User ID: {user_id}")
        print(f"Administrator Email: {account.strip()}")
        
    except Exception as e:
        print(f"Error occurred while creating tenant: {e}")
        sys.exit(1)


# Usage example
if __name__ == "__main__":
    # Can be called via command line arguments or direct function call
    if len(sys.argv) >= 5:
        account = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3]
        country = sys.argv[4]
        legal_name = sys.argv[5] if len(sys.argv) > 5 else None
        notes = sys.argv[6] if len(sys.argv) > 6 else None
        
        create_tenants(
            account=account,
            password=password,
            name=name,
            country=country,
            legal_name=legal_name,
            notes=notes
        )
    else:
        print("Usage: python create_tenants.py <account> <password> <name> <country> [legal_name] [notes]")
        print("Example: python create_tenants.py 'admin@example.com' 'password123' 'Acme Corporation' 'US' 'Acme Corp LLC' 'Main tenant'")
        print("\nRequired parameters:")
        print("  account      - Administrator email address")
        print("  password     - Administrator password")
        print("  name         - Tenant display name")
        print("  country      - Company code")
        print("\nOptional parameters:")
        print("  legal_name   - Legal name of the company")
        print("  notes        - Additional notes")
        # Or call function directly for testing
        # create_tenants(
        #     account="admin@example.com",
        #     password="password123",
        #     name="Test Tenant",
        #     country="US",
        #     legal_name="Test Tenant LLC",
        #     notes="This is a test tenant"
        # )