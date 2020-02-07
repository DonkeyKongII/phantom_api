"""This module is for shared methods across the other classes. Used for standardizing, in one place, the way
http requests/posts/etc/ are made. Additionally standardizes other functionality across all modules within
the phantom_api package.
"""

import requests
import json
from phantom_api import ph_consts

### Connection related objects/methods
_ph_connect = {
    'base_url': None,
    'username': None,
    'password': None,
    'header': None,
    'verify_cert': None
}

def setup_connection(
    auth_token=None,
    username=None,
    password=None,
    base_url='https://127.0.0.1',
    verify_cert=False
):
    """Used to setup connection for http conections to phantom REST API.

    Keyword Args:
        auth_token (string): Auth token for REST API connections to Phantom.
        username (string): GUI username
        password (string): GUI password
        base_url (string): Base url for phantom - e.g. https://192.168.116.129 or https://phantom-hostname

    Note:
        ``auth_token`` OR ``username``/``password`` combo is needed, not both... unless you are querying audit data.
        Then username/password must be used (only authentication method accepted as of 3.0.284.
    """

    _ph_connect['base_url'] = base_url
    _ph_connect['username'] = username
    _ph_connect['password'] = password
    if auth_token:
        _ph_connect['header'] = {
            'ph-auth-token': auth_token
        }
    _ph_connect['verify_cert'] = verify_cert

def ready():
    """Checks to see if connection is ready (are parameters set)

    Returns:
        bool: True if connection settings are set.
    """

    return(
        not(
            _ph_connect['header'] is None 
            and _ph_connect['username'] is None
        )
    )

def _send_request(url, method, payload=None, content_type=None):
    """Sends https post/get/put... etc. to desired phantom API endpoint. There should
    be no need to call this directly.

    Args:
        method (string): http methods to use e.g. POST, GET, PUT...
        payload (string): data to be posted to REST API endpoint.
        content_type (string): content type of request e.g. application/json.

    Returns:
        dict: returns a dictionary representing the request data that was returned.
    """
    url = _ph_connect['base_url'] + url
    request_func = getattr(requests, method.lower())
    
    auth = None
    if 'audit' in url or 'ph_user' in url or _ph_connect['header'] is None:
        auth=(_ph_connect['username'], _ph_connect['password'])

    if request_func is None:
        raise ValueError('Incorrect requests action specified')

    try:
        r = request_func(
            url,
            headers=_ph_connect['header'],
            data=payload,
            verify=_ph_connect['verify_cert'],
            auth=auth
        )

        r.raise_for_status
    except requests.exceptions.SSLError as err:
        raise Exception(
            'Error connecting to API - '
            'Likely due to the "validate server certificate" option. '
            'Details: ' + str(err)
        )
    except requests.exceptions.HTTPError as err:
        raise Exception(
            'Error calling - ' + url + ' - \n'
            'HTTP Status: ' + r.status
            + 'Reason: ' + r.reason
            + 'Details: ' + str(err)
        )
    except requests.exceptions.RequestException as err:
        raise Exception(
            'Error calling - ' + url + ' - Details: ' + str(err)
        )

    try:
        results = r.json()
    except ValueError:
        results = r.text

    return results

#Utility methods  
def _exists_in_data_set(data_set_name, data_set, data_value):
    """Check to see if a data field exists in a data set. 
    
    Mostly used to see if a data field or group of them exists in known lists in the 
    consts file. An example might be verifying that the severity selected
    for a container is a valid severity level.

    Args:
        data_set_name (string): Name of dataset to be used in error message if data cannot be found.
        data_set (dict): Data set to search
        data_value (dict or string): Values to search for or in the specificed ``data_set``.

    Raises:
        Exception: Raises exxeptoin if data cannot be found in known list.

    Returns:
        (bool): True if data was found in data_set.

    """

    if type(data_value) is str and data_value not in data_set:
        raise Exception(
            data_value + ' is not a valid ' + data_set_name + ' value.'
            + ' Select from - ' + str(data_set)
        )
    elif not any(datum in data_value for datum in data_set):
        raise Exception(
            'One of these values - ' + str(data_value) + ' - is not a valid '
            + data_set_name + 'value.'
            + ' Select from - ' + str(data_set)
        )
    return True

#modify record
def _update_record(record_type, id, data):
    """Used to update existing records

    Args:
        id (int): id of the data to update
        data (dict): dictionary representation fo the data to be updated.

    Returns:
        (dict): response object from the request connection.
    """
    
    response = _send_request(
        '/rest/' + record_type + '/' + str(id),
        'post',
        payload=json.dumps(data),
        content_type='application/json'
    )

    return response

def _delete_record(record_type, id):
    """Delete an existing record.
    
    Args:
        record_type (string): type of record to deleted (i.e. container, asset, etc.)
        id ([type]): Id of asset to delete.
    
    Returns:
        (dict): response boject from 
    """

    response = _send_request(
        '/rest/' + record_type + '/' + str(id),
        'delete'
    )

    return response
    
#query api calls
def _format_filters(filters):
    formatted_filter = ''
    for filter in filters:
        if filter['type'] not in ph_consts.QUERY_FILTERS:
            raise Exception(
                'Invalid filter selected - ' + filter['type']
                + '. Select from one of the following: ' 
                + ', '.join(ph_consts.QUERY_FILTERS) + '.'
            )
        else:
            formatted_filter += '&_filter_' + filter['field'] + '__' + filter['type'] + '='
            if filter['type'] == 'in' and type(filter['value']) == list:
                if type(filter['value'][0]) == int:
                    formatted_filter += ','.join(map(lambda x: str(x), filter['value']))
            else:
                formatted_filter += '"' + str(filter['value']) + '"'

    return formatted_filter

def _validate_pseudo_field(query_type, pseudo_field):
    if query_type not in ph_consts.PSEUDO_FIELDS:
        raise Exception('Query type - ' + query_type + ' - does not support pseudo fields.')
    elif pseudo_field not in ph_consts.PSEUDO_FIELDS[query_type]:
        raise Exception(
            'Query type - ' + query_type + ' - does not support the pseudo field - ' 
            + pseudo_field + '.'
        )

    return True

def _retrieve_single_instance(data_type, id):
    if not id:
        raise Exception('No ' + data_type + ' id was specified.')
    
    response = query(data_type, query_id=id)

    return response

def query(
    query_type,
    order='desc',
    filters=[],
    sort=None, 
    query_id=None,
    detail=None,
    pseudo_field=None,
    page=None,
    page_size=0,
    pretty=True, 
    include_expensive=False
):
    """Allows for running queries against Phantom.

    Args:
        query_type (string): type of data to be queries, can be any of the following 'action_run', 'artifact', 'asset', 'app', 'app_run', 'container', 'playbook_run', 'ph_user', 'role'
        
    Keyword Args: 
        order (string): sort order for query results (asc, desc)
        filters (list): list of dictionaries describing filter critera - see notes
        sort (string): sort field to be used in query results
        query_id (int): specific id of an object you want to query (e.g. container id, artifact id)
        detail (string): when querying a specific object (with ``query_id``), this can be used to narrow down to only one specific attribute of that object.
        pseudo_field (string): get additional information about a specific object (must use ``query_id``). See phantom docs for complete list. Example (get action runs from a container)
        page (int): if paginated results are desired, this is used to indicate page number
        page_size (int): if paginated results are desired, this indicates number of recrods returned per page
        pretty (bool): should "pretty" versions of data be returned? This adds _pretty_... values to results. (e.g. returns nicely formated date time strings, instead of isoformat)
        include_expensive (bool): include even more details that are more resource intensive.

    Example:
        The filtering capability is much simplified from using the native api. In this case just send filters in a list of dicts like so - 
        ``[{'field': 'name_of field', 'type': 'filter_type', 'value': 'filter_value'}].``::

            results = ph_base.query(
                'container',
                filters=[
                    {'field': 'create_time', 'type': 'gte', 'value': start_date},
                    {'field': 'create_time', 'type': 'lte', 'value': end_date},
                    {'field': 'label', 'type': 'iexact', 'value': 'campaign'}
                ]
            )
    """

    url = '/rest/' + query_type

    if query_id:
        url += '/' + str(query_id)
        if detail:
            url += '/' + detail
        elif pseudo_field and _validate_pseudo_field(query_type, pseudo_field):
            url += '/' + pseudo_field
    
    url_query_string = '?page_size=' + str(page_size)

    if page:
        url_query_string += '&page=' + str(page)
    if order and _exists_in_data_set('Query Sort Field', ph_consts.QUERY_SORT_ORDER, order):
        url_query_string += '&order=' + order
    if sort:
        url_query_string += '&sort=' + sort
    if pretty:
        url_query_string += '&pretty'
    if include_expensive:
        url_query_string += '&include_expensive'
    if len(filters) > 0:
        url_query_string += _format_filters(filters)

    response = _send_request(
        url + url_query_string,
        'GET'
    )

    return response

def search(
    query,
    categories=None,
    page=None,
    page_size=None
):
    """TODO: documentation coming soon
    """

    response = _send_request(
        '/rest/search?query=' + query
        + (('&categories=' + categories) if categories else '')
        + (('&page=' + page) if page else '')
        + (('@page_size=' + page_size if page_size else '')),
        'get'
    )

    return response

   
#audit data
def get_audit_data(
    audit_data=[],
    audit_format='json',
    sort='desc',
    start=None,
    end=None
):
    """Retrieves audit 
    
    Keyword Args:
        audit_data (list): a list of audit types desired to be returned, * for all, see api docs for acceptable types
        audit_format (string): json or csv
        sort (string): sort order - defaults to desc
        start (string): start date
        end (string): end date

    Notes:
        * if start and end dates aren't supplied defaults to last 30 days (i think...)
        * Must use username/password authentication for this to work - this is a current bug with Phantom API
    """

    url = ''
    if audit_format and _exists_in_data_set('Audit Format', ph_consts.AUDIT_FORMAT, audit_format):
        if(len(audit_data) > 0 and _exists_in_data_set('Audit Data Type', ph_consts.AUDIT_TYPES, [datum['type'] for datum in audit_data])):
            if len(audit_data) == 1 and audit_data[0]['id'] != '*':
                url = '/rest/' + audit_data[0]['type'] + '/' + audit_data[0]['id'] + '/audit?format=' + audit_format
            else:
                url = (
                    '/rest/audit?format=' + audit_format + '&'
                    + '&'.join([datum['type'] + '=' + str(datum['id']) for datum in audit_data])
                )
        else:
            url = '/rest/audit?format=' + audit_format

    if sort and _exists_in_data_set('Sort Order', ph_consts.QUERY_SORT_ORDER, sort):
        url += '&sort=' + sort 
    if start:
        url += '&start=' + start
    if end:
        url += '&end=' + end

    response = _send_request(
        url,
        'get'
    )

    return response