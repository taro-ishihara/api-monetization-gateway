import os
import logging
import urllib.request
from moesif_aws_lambda.middleware import *

logger = logging.getLogger()
level_name = os.environ['LOG_LEVEL']
level = logging.getLevelName(level_name)
logger.setLevel(level)

def identify_user(event, context):
    user = event['requestContext']['authorizer']['lambda']['tenantId']
    return user


def identify_company(event, context):
    company = event['requestContext']['authorizer']['lambda']['subscriptionId']
    return company


def get_metadata(event, context):
    metadata = {
        'trace_id': event['requestContext']['requestId'],
        'api_name': '利用者情報統計データAPI',
    }
    return metadata

def mask_event(eventmodel):
  del eventmodel.request.headers['frontegg-client-id'], eventmodel.request.headers['frontegg-secret-key']
  return eventmodel

moesif_options = {
    'LOG_BODY': True,
    'DEBUG': True,
    'IDENTIFY_USER': identify_user,
    'IDENTIFY_COMPANY': identify_company,
    'GET_METADATA': get_metadata,
    'MASK_EVENT_MODEL': mask_event,
}
@MoesifLogger(moesif_options)
def lambda_handler(event, context):
    url = 'https://example.com'

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as res:
        body = res.read()

    return {
        'statusCode': 200,
        'isBase64Encoded': False,
        'body': body,
        'headers': {
            'Content-Type': 'text/html'
        }
    }
