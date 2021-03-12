# encoding: utf-8

import logging
import json
import ckan.logic as logic
import ckan.plugins as p
import ckan.lib.navl.dictization_functions
import ckanext.sageinterface.logic.schema as sageinterface_schema

log = logging.getLogger(__name__)
_validate = ckan.lib.navl.dictization_functions.validate

def _unrename_json_field(data_dict):
    return _rename_field(data_dict, 'nested', 'json')

def _rename_field(data_dict, term, replace):
    fields = data_dict.get('fields', [])
    for i, field in enumerate(fields):
        if 'type' in field and field['type'] == term:
            data_dict['fields'][i]['type'] = replace
    return data_dict

def sagecommons_create(context, data_dict):
    records = data_dict.pop('records', None)
    resource = data_dict.pop('resource', None)
    schema = context.get('schema', sageinterface_schema.create_schema())
    data_dict, errors = _validate(data_dict, schema, context)

    if records:
        data_dict['records'] = records
    if resource:
        data_dict['resource'] = resource
    if errors:
        raise p.toolkit.ValidationError(errors)

    if 'resource' in data_dict and 'resource_id' in data_dict:
        raise p.toolkit.ValidationError({
            'resource': ['resource cannot be used with resource_id']
        })

    if 'resource' not in data_dict and 'resource_id' not in data_dict:
        raise p.toolkit.ValidationError({
            'resource_id': ['resource_id or resource required']
        })
    
    if 'resource' in data_dict:
        has_url = 'url' in data_dict['resource']

    return _unrename_json_field(data_dict)
