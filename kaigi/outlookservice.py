import requests
import uuid
import datetime

outlook_api_endpoint = 'https://outlook.office365.com/api/v1.0{0}'

def make_api_call(method, url, token, payload = None, parameters = None):
    headers = { 'User-Agent': 'kaigi/1.0',
                'Authorization': 'Bearer {0}'.format(token),
                'Accept': 'application/json'
              }

    request_id = str(uuid.uuid4())
    instrumentation = { 'client-request-id': request_id,
                        'return-client-request-id': 'true'
                      }

    headers.update(instrumentation)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers = headers, params = parameters)
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers = headers, params = parameters)
    elif (method.upper() == 'PATCH'):
        headers.update({ 'Content-Type': 'application/json' })
        response = requests.patch(url, headers = headers, data = payload, params = parameters)
    elif (method.upper() == 'POST'):
        headers.update({ 'Content-Type': 'application/json' })
        response = request.post(url, headers = headers, data = payload, params = parameters)

    return response

def get_my_messages(access_token):
    get_messages_url = outlook_api_endpoint.format('/Me/Messages')

    query_parameters = { '$top': '10',
                         '$select': 'DateTimeReceived,Subject,From',
                         '$orderby': 'DateTimeReceived DESC'
                       }

    r = make_api_call('GET', get_messages_url, access_token, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return '{0}: {1}'.format(r.status_code, r.text)

def get_my_events(access_token):
    get_events_url = outlook_api_endpoint.format('/me/calendarview')

    query_parameters = { 'startDateTime': (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'endDateTime': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            '$orderby': 'Start',
                       }

    r = make_api_call('GET', get_events_url, access_token, parameters = query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return '{0}: {1}'.format(r.status_code, r.text)

def get_my_info(access_token):
    get_info_url = outlook_api_endpoint.format('/me')

    r = make_api_call('GET', get_info_url, access_token)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return '{0}: {1}'.format(r.status_code, r.text)
