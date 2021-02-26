import re
import os
import urlparse
import urllib
import urllib2
import logging
import json
from pylons import config
from requests import Session, Request
import ckan.model as model
from ckan.lib.base import (c, request, response, abort)
from ckanext.archiver.model import Archival
import ckanext.resourceproxy.plugin as proxy
from ckan.plugins import toolkit as tk

log = logging.getLogger('ckanext.sageinterface.lib.helpers')

def identify_resource(resource_id,dataset_name):
    '''Returns a printable identity of a resource object.
    e.g. '/dataset/energy-data/d1bedaa1-a1a3-462d-9a25-7b39a941d9f9'
    '''
    # FIX: add group name later
    return '/dataset/{0}/resource/{1}'.format(dataset_name, resource_id)

def get_url(resource,dataset_name,query):
    from requests.exceptions import InvalidURL

    url = None
    archived = False
    query['mimetype'] = None
    resource_id = resource.get('id')
    direct_url = resource.get('url')
    archival = Archival.get_for_resource(resource_id)
    resource_url = identify_resource(resource_id,dataset_name)
    
    if archival:
        # Look for a local cache of the data file
        if archival.cache_filepath:
            if os.path.exists(archival.cache_filepath.encode('utf8')):
                log.debug('Previewing local cached data: %s', archival.cache_filepath)
                url = archival.cache_filepath
                archived = True
            else:
                log.debug('Local cached data file missing: %s', archival.cache_filepath)
        else:
            log.debug('No cache_filepath for resource %s', resource_url)

        # Otherwise try the cache_url
        if not url:
            if archival.cache_url:
                try:
                    u = fix_url(archival.cache_url)
                except InvalidURL:
                    log.error("Unable to fix the URL for resource: %s" % resource_url)
                    return None, False
                try:
                    req = urllib2.Request(u)
                    req.get_method = lambda: 'HEAD'

                    r = urllib2.urlopen(req)
                    if r.getcode() == 200:
                        url = u
                        query['length'] = r.info().get("content-length", 0)
                        query['mimetype'] = r.info().get('content-type', None)
                        log.debug('Previewing cache URL: %s', url)
                except Exception, e:
                    log.error(u"Request {0} with cache url {1}, {2}".format(resource_url, u, e))
            else:
                log.debug('No cache_url for resource %s', resource_url)
    else:
        log.debug('Resource is not archived: %s', resource_url)
    
    return url,archived

def get_data(data_dict):
    package_name = data_dict['package']['name']
    resource = data_dict['resource']
    query = dict()
    url,archived = get_url(resource,package_name,query)
    if not archived:
        url = resource.get('url')
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    data_str = r.read()
    data_json = json.loads(data_str)
    return data_json

def getFieldsTemplate():
    template = {
                "id": None,
                "type": None,
                "label": None,
                "description": None
            }
    return template

def get_metadata(resource):
    url = resource.get('url')
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    data_str = r.read()
    data_json = json.loads(data_str)
    return data_json["metadata"]