from fastapi import APIRouter, Depends
from core.database.models import Suppliers, SupplierConfigurations, Models, ModelConfigurations, Users
from api.utils.common import response_success, response_error
from api.utils.jwt import get_current_user
from api.schema.supplier import OperationResponse, SupplierRequest, SupplierListResponse, ModelSwitchRequest
from languages import get_language_content
from config import model_config, model_type
from api.utils.jwt import *

router = APIRouter()


@router.get("/suppliers_list", response_model=SupplierListResponse)
async def get_suppliers_list(userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve a list of suppliers and their models.
    """
    team_id = userinfo.team_id
    # Simplified dictionary comprehension
    supplier_config_data = {model['supplier']: model for model in model_config}
    # Fetch online suppliers
    suppliers_data = Suppliers().get_supplier_model_online_list(team_id)
    unique_suppliers = {}

    # Process each supplier
    for supplier in suppliers_data:
        # Get the supplier configuration for the current team
        supplier_configuration = SupplierConfigurations().get_supplier_config_id(supplier['supplier_id'], team_id)
        supplier_config = supplier_configuration['config'] if supplier_configuration else {}
        supplier_id = supplier['supplier_id']

        # If the supplier is not already in the unique_suppliers dictionary, add it
        if supplier_id not in unique_suppliers:
            unique_suppliers[supplier_id] = {
                'supplier_id': supplier_id,
                'supplier_name': supplier['supplier_name'],
                'supplier_config': supplier_config,
                'authorization': 1 if supplier_config else 0,
                'models': []
            }

        # Add model information to the supplier if available
        if supplier.get('model_id') and supplier.get('model_name'):
            unique_suppliers[supplier_id]['models'].append({
                'model_id': supplier['model_id'],
                'model_name': supplier['model_name'],
                'support_image': supplier['support_image'],
                'model_type': supplier['model_type'],
                'model_default_used': supplier['model_default_used'],
                'sort_order': supplier['sort_order']
            })

    # Sort suppliers by supplier_id in ascending order
    suppliers = sorted(unique_suppliers.values(), key=lambda x: x['supplier_id'])
    for supplier in suppliers:
        if supplier.get('models'):
            # Sort models by sort_order in ascending order
            supplier['models'] = sorted(supplier['models'], key=lambda x: x['sort_order'])

    # Initialize result dictionary
    result = {'suppliers_list': [], 'models_list': []}

    # Process each supplier to build the result
    for supplier in suppliers:
        supplier_id = supplier['supplier_id']
        supplier_name = supplier['supplier_name']
        supplier_config = supplier['supplier_config']
        default_config = supplier_config_data[supplier_name]['config']

        # Update the default configuration with the supplier's configuration
        if supplier_config:
            for key in supplier_config_data[supplier_name]['config']:
                if key['key'] in supplier_config:
                    key['value'] = supplier_config[key['key']]

        # Prepare supplier data for the response
        supplier_data = {
            'supplier_id': supplier_id,
            'supplier_name': supplier_name,
            'supplier_config': default_config,
            'authorization': 1 if supplier_config else 0,
            'models': []
        }

        # Process each model for the supplier
        for model in supplier['models']:
            if model.get('model_id') and model.get('model_name'):
                model_data = {
                    'model_id': model['model_id'],
                    'model_name': model['model_name'],
                    'support_image': model['support_image'],
                    'model_type': model['model_type'],
                    'model_type_name': model_type[model['model_type']]['type'],
                    'model_default_used': model['model_default_used']
                }
                supplier_data['models'].append(model_data)

                # Build models_list structure
                model_type_key = model['model_type']
                model_type_entry = next(
                    (entry for entry in result['models_list'] if entry['model_type'] == model_type_key), None)
                if not model_type_entry:
                    model_type_entry = {
                        'model_type': model_type_key,
                        'model_type_name': get_language_content(
                            f"{model_type[model_type_key]['type']}_MODEL_TYPE_NAME"),
                        'help': get_language_content(f"{model_type[model_type_key]['type']}_HELP"),
                        'suppliers': []
                    }
                    result['models_list'].append(model_type_entry)

                model_info = {
                    'supplier_id': supplier_id,
                    'supplier_name': supplier_name,
                    'models': [{
                        'model_id': model['model_id'],
                        'model_name': model['model_name'],
                        'support_image': model['support_image'],
                        'model_default_used': model['model_default_used']
                    }]
                }
                # Check if the supplier already exists under this model type
                existing_supplier = next(
                    (s for s in model_type_entry['suppliers'] if s['supplier_id'] == supplier['supplier_id']), None)
                if existing_supplier:
                    existing_supplier['models'].append(model_info['models'][0])  # Add model to existing supplier
                else:
                    model_type_entry['suppliers'].append(model_info)  # Add new supplier

        result['suppliers_list'].append(supplier_data)

    # Return success response with the result
    return response_success(result)


@router.post("/supplier_authorize", response_model=OperationResponse)
async def supplier_authorize(supplier_request: SupplierRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Authorize a supplier with the provided configuration.
    """
    team_id = userinfo.team_id
    supplier_id = supplier_request.supplier_id
    config = supplier_request.config

    # Check if the user has permission to authorize the supplier
    role = Users().get_user_id_role(userinfo.uid)
    if not role:
        return response_error(get_language_content("do_not_have_permission"))

    # Fetch the supplier based on the provided supplier_id
    supplier = Suppliers().get_supplier_id(supplier_id)

    # If the supplier is not found, return an error response
    if not supplier:
        return response_error(get_language_content("supplier_not_found"))

    # Fetch the existing supplier configuration
    supplier_config = SupplierConfigurations().get_supplier_config_id(supplier_id, team_id)

    # Convert the front-end config list to a dict
    config_data = {config_item['key']: config_item['value'] for config_item in config}

    if supplier_config:
        # Merge new config with existing config without replacing unrelated keys
        existing_config = supplier_config.get('config', {})
        updated = False
        for key, value in config_data.items():
            if key not in existing_config or existing_config[key] != value:
                existing_config[key] = value
                updated = True
        if updated:
            new_config = {
                'supplier_id': supplier_id,
                'config': existing_config,
                'team_id': team_id
            }
            column = [{'column': 'id', 'value': supplier_config['id']}]
            SupplierConfigurations().update(column, new_config)
    else:
        new_config = {
            'supplier_id': supplier_id,
            'config': config_data,
            'team_id': team_id
        }
        SupplierConfigurations().insert(new_config)

    # Return a success response
    return response_success(detail=get_language_content("supplier_authorized_success"))


@router.post("/switching_models", response_model=OperationResponse)
async def switching_models(model_switch_request: ModelSwitchRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Switch the default model for a given type.
    For a given type and team, only one model may be set as default.
    If multiple defaults exist, reset all (except the chosen one) to 0.
    """
    team_id = userinfo.team_id

    # Fetch the target model configuration based on provided model_id
    new_model_config = ModelConfigurations().select_one(
        columns=['id'],
        joins=[['inner', 'models', 'model_configurations.model_id = models.id']],
        conditions=[
            {'column': 'models.id', 'value': model_switch_request.model_id},
            {'column': 'models.type', 'value': model_switch_request.type},
            {'column': 'models.mode', 'value': 1},
            {'column': 'model_configurations.team_id', 'value': team_id}
        ]
    )
    if not new_model_config:
        return response_error(get_language_content("model_not_found"))

    # Fetch all model configurations for given type, team and mode=1
    all_configs = ModelConfigurations().select(
        columns=['id'],
        joins=[['inner', 'models', 'model_configurations.model_id = models.id']],
        conditions=[
            {'column': 'models.type', 'value': model_switch_request.type},
            {'column': 'models.mode', 'value': 1},
            {'column': 'model_configurations.team_id', 'value': team_id}
        ]
    )
    # Update all configs with id not equal to new_model_config['id'] to default_used 0.
    for config in all_configs:
        if config['id'] != new_model_config['id']:
            ModelConfigurations().update(
                {'column': 'id', 'value': config['id']},
                {'default_used': 0}
            )

    # Finally, set the chosen model configuration as default.
    ModelConfigurations().update(
        {'column': 'id', 'value': new_model_config['id']},
        {'default_used': 1}
    )
    return response_success(detail=get_language_content("model_switching_success"))