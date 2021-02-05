import logging
import sys
from pylons import config
import ckan.plugins as p
from ckan.plugins import implements, toolkit
import ckanext.resourceproxy.plugin as proxy

log = logging.getLogger('ckanext.sageinterface')

class SageinterfacePlugin(p.SingletonPlugin):
    implements(p.IConfigurer, inherit=True)
    implements(p.IResourceView, inherit=True)
    proxy_enabled = False

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'sageinterface')
        self.proxy_enabled = p.plugin_loaded('resource_proxy')

    def can_view(self, data_dict): 
        # IResourceView
        # Make it a requirement that I need to add resource_proxy to my plugins
        # So this can work
        datastoreActive = data_dict['resource'].get('datastore_active', False)
        log.info('can_view::proxy_enabled: {0}'.format(self.proxy_enabled))
        log.info('can_view::datastoreActive: {0}'.format(datastoreActive))
        return self.proxy_enabled and not datastoreActive
    
    def can_preview(self, data_dict):
        # IResourceView
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
        # IResourceView 
        # Add another option to the Views section called Data view with a new icon
        name = 'sageinterfaceview'
        title = 'Data View'
        viewConfig = {'name': name,'title':title,'always_available': True, 'default_title': title, 'icon': 'server'}
        return viewConfig
    
    def can_view(self, data_dict):
        # IResourceView
        # Make it a requirement that I need to add resource_proxy to my plugins
        # So this can work
        proxy_enabled = p.plugin_loaded('resource_proxy')
        datastore_active = data_dict['resource'].get('datastore_active', False)
        log.info('proxy_enabled: {0}'.format(self.proxy_enabled))
        log.info('datastoreActive: {0}'.format(datastore_active))
        return self.proxy_enabled and not datastore_active 