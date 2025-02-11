import sys, os
from pathlib import Path
from typing import Any, Dict

sys.path.append(str(Path(__file__).absolute().parent.parent))
os.environ['DATABASE_AUTO_COMMIT'] = 'True'

from config import model_config 
from core.database.models import ModelConfigurations, SupplierConfigurations, Suppliers, Models

def check_supplier_exists(name: str) -> int:
    """Check if supplier exists by name and return supplier_id or None"""
    supplier = Suppliers().select_one(
        columns=['id'],
        conditions={
            'column': 'name',
            'value': name,
            'op': '='
        }
    )
    return supplier.get('id') if supplier else None

def check_model_exists(supplier_id: int, name: str) -> int:
    """Check if model exists by supplier_id and name, return model_id or None"""
    model = Models().get_models_by_supplier_id(supplier_id)
    if model:
        for item in model:
            if item['name'] == name:
                return item['id']
    return None

def check_supplier_config_exists(supplier_id: int, team_id: int) -> Dict:
    """Check if supplier configuration exists"""
    return SupplierConfigurations().get_supplier_config_id(supplier_id, team_id)

model_type_map = {
    "text-generation": 1,
    "embeddings": 2, 
    "reranking": 3,
    "speech2text": 4,
    "tts": 5,
    "text2img": 6,
    "moderation": 7
}

# Initialize database
for supplier in model_config:
    # 1. Process supplier
    supplier_id = check_supplier_exists(supplier['supplier'])
    if not supplier_id:
        supplier_data = {
            'name': supplier['supplier'],
            'mode': supplier['mode'],
            'status': 1
        }
        print(f"Adding supplier: {supplier_data}")
        supplier_id = Suppliers().insert(supplier_data)
    
    # 2. Process supplier configuration 
    supplier_config = {}
    for config_item in supplier['config']:
        if config_item.get('value') != '':
            supplier_config[config_item['key']] = config_item['value'] or config_item['default_value']
    
    if supplier_config and not check_supplier_config_exists(supplier_id, 1):
        SupplierConfigurations().insert({
            'team_id': 1,
            'supplier_id': supplier_id,
            'config': supplier_config,
            'status': 1
        })
    
    # 3. Process models and their configurations
    models = supplier['models']
    for model_type, model_list in models.items():
        for model_config_item in model_list:
            model_name = model_config_item['model_name']
            model_id = check_model_exists(supplier_id, model_name)
            
            if not model_id:
                model_data = {
                    'supplier_id': supplier_id,
                    'name': model_name,
                    'type': model_type_map[model_type],
                    'mode': supplier['mode'],
                    'max_context_tokens': model_config_item.get('max_context_tokens', {}).get('default_value', 0),
                    'max_output_tokens': model_config_item.get('max_output_tokens', {}).get('default_value', 0),
                    'status': 1
                }
                print(f"Adding model: {model_data}")
                model_id = Models().insert(model_data)
            
            # 4. Process model configuration
            if model_config_item.get('config'):
                model_config_data = {}
                for config in model_config_item['config']:
                    if config.get('value') is not None:
                        model_config_data[config['key']] = config['value']
                    else:
                        model_config_data[config['key']] = config['default_value']
                
                if model_config_data:
                    ModelConfigurations().insert({
                        'team_id': 1,
                        'model_id': model_id,
                        'config': model_config_data,
                        'default_used': 0,
                        'status': 1
                    })

print("Database initialization completed!")
