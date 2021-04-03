# encoding: utf-8

from ckan.plugins.toolkit import (
    Invalid,
    ObjectNotFound,
    NotAuthorized,
    get_action,
    get_validator,
    _,
    request,
    response,
    BaseController,
    abort,
    render,
    c,
    h,
)
from ckanext.datastore.writer import (
    csv_writer,
    tsv_writer,
    json_writer,
    xml_writer,
)
from ckan.logic import (
    tuplize_dict,
    parse_params,
)
import ckan.lib.navl.dictization_functions as dict_fns

from itertools import izip_longest

import ckan.plugins as p

from ckan.common import c

from ckanext.sageinterface.lib.helpers import (get_data,convert_datastorefmt)

int_validator = get_validator('int_validator')
boolean_validator = get_validator('boolean_validator')

DUMP_FORMATS = 'csv', 'json'
PAGINATE_BY = 32000


class SageInterfaceController(BaseController):
    def dump(self, resource_id):
        try:
            offset = int_validator(request.GET.get('offset', 0), {})
        except Invalid as e:
            abort(400, u'offset: ' + e.error)
        try:
            limit = int_validator(request.GET.get('limit'), {})
        except Invalid as e:
            abort(400, u'limit: ' + e.error)
        bom = boolean_validator(request.GET.get('bom'), {})
        fmt = request.GET.get('format', 'csv')

        if fmt not in DUMP_FORMATS:
            abort(400, _(
                u'format: must be one of %s') % u', '.join(DUMP_FORMATS))
        
        context = {"for_view": True, "user": c.user, "auth_user_obj": c.userobj}
        resource = p.toolkit.get_action('resource_show')(context, {'id': resource_id})

        try:
            dump_to(
                resource,
                resource_id,
                response,
                fmt=fmt,
                offset=offset,
                limit=limit,
                options={u'bom': bom})
        except ObjectNotFound:
            abort(404, _('Sageinterface unable to provide data in {0} format'.format(fmt)))

def dump_to(resource,resource_id, output, fmt, offset, limit, options):
    if fmt == 'csv':
        writer_factory = csv_writer
        records_format = 'csv'
    elif fmt == 'json':
        writer_factory = json_writer
        records_format = 'lists'

    def start_writer(fields):
        bom = options.get(u'bom', False)
        return writer_factory(output, fields, resource_id, bom)

    def result_page(offs, lim):
        data = get_data(resource)
        dataStoreFmt = convert_datastorefmt(data)
        return dataStoreFmt
        # return get_action('datastore_search')(None, {
        #     'resource_id': resource_id,
        #     'limit':
        #         PAGINATE_BY if limit is None
        #         else min(PAGINATE_BY, lim),
        #     'offset': offs,
        #     'sort': '_id',
        #     'records_format': records_format,
        #     'include_total': False,
        # })

    result = result_page(offset, limit)

    with start_writer(result['fields']) as wr:
        # while True:
        #     if limit is not None and limit <= 0:
        #         break

        records = result['records']
        wr.write_records(records)

            # if records_format == 'objects' or records_format == 'lists':
            #     if len(records) < PAGINATE_BY:
            #         break
            # elif not records:
            #     break

            # offset += PAGINATE_BY
            # if limit is not None:
            #     limit -= PAGINATE_BY
            #     if limit <= 0:
            #         break

            # result = result_page(offset, limit)
