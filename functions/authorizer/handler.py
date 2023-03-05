import os
import json
import logging
import time
import urllib.request
import jwt

logger = logging.getLogger()
level_name = os.environ['LOG_LEVEL']
level = logging.getLevelName(level_name)
logger.setLevel(level)

FRONTEGG_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwoEkXCidyAc4gOrrLjNz
UwSibLRjXbMYriXWkHkJVaXx4raVeVPMtEQx2OU8O+397K3HUwWz71czyDOHLoY9
LOTxw+b6x5HTka/URYxSVpNXVOe33rgwrptWhK5VLM8yaKKE+dzEz3iiScSi/Nm2
CQHcecWyEvq1MTUvqnV9U4v1hC2+N8+piMgSlY92GPFBwiwJuTXkwfpsQ6Y3QWDz
cXobFG3so4wv4Z0UvJelxf3PNpEVB7mJsDGQTYh3b8Qm9WH8efHur1WsYCzYdgzb
qQ5qy2KNQ/pelH8d3xsHbz9dBptuuRx/mO+DasEJ4KTstY+ev1ehYsMmiuRe/DkU
uwIDAQAB
-----END PUBLIC KEY-----
'''
FRONTEGG_ACCESS_TOKEN = ''
FRONTEGG_ACCESS_TOKEN_EXP = 0

def get_jwt_token(frontegg_client_id, frontegg_secret_key):
    global FRONTEGG_ACCESS_TOKEN
    global FRONTEGG_ACCESS_TOKEN_EXP
    if int(time.time()) < FRONTEGG_ACCESS_TOKEN_EXP:
        logger.info('recycle token')
        return FRONTEGG_ACCESS_TOKEN

    url = 'https://app-w7ldic3ylusp.frontegg.com/identity/resources/auth/v1/api-token'
    data = {
        'clientId': frontegg_client_id,
        'secret': frontegg_secret_key
    }
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = json.loads(res.read())
        FRONTEGG_ACCESS_TOKEN = body['accessToken']
        FRONTEGG_ACCESS_TOKEN_EXP = int(time.time()) + 60
        return FRONTEGG_ACCESS_TOKEN

route_dict = {
    'GET /suicauser': 'prod_NRtvOSGCbjHHoE',
    'GET /ekiuser': 'prod_NRtuh8HRO3yaR1',
    'GET /zaisen': 'prod_NRtte5JlrvMQst',
    'GET /kaisatsu': 'prod_NRtsoODDGXr1JF'
}

def lambda_handler(event, context):
    frontegg_client_id, frontegg_secret_key = event['identitySource']
    jwt_token = get_jwt_token(frontegg_client_id, frontegg_secret_key)
    identity = jwt.decode(jwt_token, FRONTEGG_PUBLIC_KEY, audience="f707d5ce-9584-4bd1-87b5-85f4ea96327d" ,algorithms=["RS256"])
    response = {
        "isAuthorized": False,
        "context": {
            "tenantId": identity['tenantId'],
        }
    }

    hit_permissions = [p for p in identity['permissions'] if p.split('.')[0] == route_dict[event['routeKey']]]
    if len(hit_permissions) == 1:
        response['isAuthorized'] = True
        response['context']['subscriptionId'] = hit_permissions[0].split('.')[1]

    return response
