from urllib import quote, urlencode
from django.conf import settings
import requests

client_id = settings.OUTLOOK_CLIENT_ID
client_secret = settings.OUTLOOK_CLIENT_SECRET

authority = 'https://login.microsoftonline.com'

authorize_url = '{0}{1}'.format(authority, '/common/oauth2/authorize?{0}')
token_url = '{0}{1}'.format(authority, '/common/oauth2/token')

def get_signin_url(redirect_uri):
    params = { 'client_id': client_id,
               'redirect_uri': redirect_uri,
               'response_type': 'code',
               'prompt': 'login',
             }

    signin_url = authorize_url.format(urlencode(params))

    return signin_url

def get_token_from_code(auth_code, redirect_uri):
    post_data = { 'grant_type': 'authorization_code',
                  'code': auth_code,
                  'redirect_uri': redirect_uri,
                  'resource': 'https://outlook.office365.com',
                  'client_id': client_id,
                  'client_secret': client_secret
                }
    r = requests.post(token_url, data = post_data)
    try:
        access_token = r.json()['access_token']
        return access_token
    except:
        return 'Error retrieving token: {0} - {1}'.format(r.status_code, r.text)
