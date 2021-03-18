import re
import os
import urlparse
import urllib
import urllib2
import logging
import json
import ssl
from pylons import config
from requests import Session, Request
import ckan.model as model
from ckan.lib.base import (c, request, response, abort)
from ckanext.archiver.model import Archival
import ckanext.resourceproxy.plugin as proxy
from ckan.plugins import toolkit as tk

log = logging.getLogger('ckanext.sageinterface.lib.helpers')
sagecommons_formats = ['json']
data_keyword = 'data'
meta_keyword = 'metadata'
honeyhouse_keyword='honeyhouse'

def identify_resource(resource_id,dataset_name):
    '''Returns a printable identity of a resource object.
    e.g. '/dataset/energy-data/d1bedaa1-a1a3-462d-9a25-7b39a941d9f9'
    '''
    # FIX: add group name later
    return '/dataset/{0}/resource/{1}'.format(dataset_name, resource_id)

def query_to_dict(query):
    if type(query)== dict or query is None:
        query_json = json.dumps(query)
    else:
        query_dict = eval(query)
        query_json = json.dumps(query_dict)
    return query_json


def get_rawdata(url,query):
    context = ssl._create_unverified_context()
    empty_dict = {data_keyword:[],meta_keyword:[]}
    query_json = query_to_dict(query)
    try:
        if query is None:
            req = urllib2.Request(url)
        else:
            req = urllib2.Request(url,query_json)
        r = urllib2.urlopen(req,context=context)
    except Exception, e:
        log.error(u"Request {0}, {1}".format(url, e))
        return empty_dict

    data_str = r.read()
    if honeyhouse_keyword in url:
        data_json = [json.loads(str(item)) for item in data_str.strip().split('\n')]
    else:
        data_json = json.loads(data_str)
    
    if type(data_json) == dict:
        if data_keyword in data_json.keys() and meta_keyword in data_json.keys():
            data = {data_keyword: data_json[data_keyword],
                    meta_keyword:data_json[meta_keyword]}
        else:
            return empty_dict
    else:
        data = {data_keyword: data_json,meta_keyword:[]}
    return data



def get_data(data_dict):
    package_name = data_dict['package']['name']
    resource = data_dict['resource']
    query = resource.get('query')
    url = resource.get('url')
    data = get_rawdata(url,query)
    return data

def getFieldsTemplate():
    template = {
                "id": None,
                "type": None,
                "label": None,
                "description": None
            }
    return template

def get_metadata(resource):
    datastore_active = resource.get('datastore_active')
    formatType = resource.get('format').lower()
    if not datastore_active and formatType in sagecommons_formats:
        url = resource.get('url')
        query = resource.get('query')
        data = get_rawdata(url,query)
        if type(data) == dict:
            if meta_keyword in data.keys():
                return data[meta_keyword]
    return None