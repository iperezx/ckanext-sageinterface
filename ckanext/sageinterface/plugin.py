import logging
import sys
import json
from pylons import config
import ckan.plugins as p
import ckanext.resourceproxy.plugin as proxy
from ckanext.sageinterface.lib.helpers import (get_data, get_metadata)
import ckanext.sageinterface.logic.action as action

log = logging.getLogger('ckanext.sageinterface')

class SageinterfacePlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IResourceView, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)
    p.implements(p.IRoutes, inherit=True)
    proxy_enabled = False

    # IConfigurer
    def update_config(self, config_):
        p.toolkit.add_template_directory(config_, 'templates')
        p.toolkit.add_public_directory(config_, 'public')
        p.toolkit.add_resource('public', 'ckanext-sageinterface')
        self.proxy_enabled = p.plugin_loaded('resource_proxy')
    
    # IResourceView
    def can_view(self, data_dict): 
        datastoreActive = data_dict['resource'].get('datastore_active', False)
        log.info('can_view::proxy_enabled: {0}'.format(self.proxy_enabled))
        log.info('can_view::datastoreActive: {0}'.format(datastoreActive))
        return self.proxy_enabled and not datastoreActive
    
    def can_preview(self, data_dict):
        resource = data_dict['resource']
        formatVal = resource['format']
        datastore_active = data_dict['resource'].get('datastore_active', False)
        if self.proxy_enabled  & datastore_active:
            return {'can_preview': True, 'quality': 2}
        else:
            return {'can_preview': True,
                    'fixable': 'Enable resource_proxy',
                    'quality': 2}
        return {'can_preview': False}
    
    def info(self):
        name = 'sageinterfaceview'
        title = 'Data View'
        viewConfig = {'name': name,'title':title,'always_available': True, 'default_title': title, 'icon': 'server'}
        return viewConfig
    
    def can_view(self, data_dict):
        proxy_enabled = p.plugin_loaded('resource_proxy')
        datastore_active = data_dict['resource'].get('datastore_active', False)
        log.info('proxy_enabled: {0}'.format(self.proxy_enabled))
        log.info('datastoreActive: {0}'.format(datastore_active))
        return self.proxy_enabled and not datastore_active
    
    def setup_template_variables(self, context, data_dict):
        self.data = get_data(data_dict['resource'])
        log.info('view: {0}'.format(json.dumps(data_dict['resource_view'])))
        # log.info('url: {0}'.format(json.dumps(url)))
        return {'resource_view': json.dumps(data_dict['resource_view']),
                'resource_data': json.dumps(self.data["data"])}

    def preview_template(self, context, data_dict):
        return 'sageinterface_recline.html'

    def view_template(self, context, data_dict):
        return 'sageinterface_recline.html'

    # ITemplateHelpers
    def get_helpers(self):
        return {'get_metadata': get_metadata}

    # IActions
    def get_actions(self):
        actions = { 'sagecommons_create': action.sagecommons_create}
        return actions

   # IRoutes
    def before_map(self, m):
        m.connect(
            '/sageinterface/dump/{resource_id}',
            controller='ckanext.sageinterface.controller:SageInterfaceController',
            action='dump')
        return m