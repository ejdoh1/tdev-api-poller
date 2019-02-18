import json
import boto3
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
import logging 
import jsonschema
import os 
from decimal import Decimal

SSM = boto3.client('ssm') 
S3 = boto3.client('s3')

DATA_BUCKET = os.environ['DATA_BUCKET']

DEVICES_SCHEMA_FILEPATH = "./schemas/devices.json"
DATA_TMP_FILEPATH = "/tmp/data.json"
DATA_S3_KEY = "devices/data.json"

TOKEN_URL = "https://tapi.telstra.com/v2/oauth/token"
TAPI_DEVICES_URL = "https://tapi.telstra.com/application/lot/v1/devices"

SCOPE = "LOT_DEVICES_READ"
SSM_NAME_KEY = "TDevAPIKey"
SSM_NAME_SECRET = "TDevAPISecret"
 
HTTP_OK = 200

log = logging.getLogger()
log.setLevel(logging.INFO) 

def get_secret(key,decrypt):
	r = SSM.get_parameter(
		Name=key,
		WithDecryption=decrypt
	)
	return r['Parameter']['Value']

def get_client_key_and_secret():
    log.info('getting SSM params API client key and secret')
    key = get_secret(SSM_NAME_KEY,False)
    secret = get_secret(SSM_NAME_SECRET,True)
    log.info('got SSM params API client key and secret')
    return key, secret

def get_access_token(key,secret):
    client = BackendApplicationClient(client_id=key)
    oauth = OAuth2Session(
        client=client,
        scope=SCOPE
    )
    log.info('fetching oauth token')
    token = oauth.fetch_token(
        token_url=TOKEN_URL,
        client_id=key,
        client_secret=secret
    )
    # token_type = token['token_type']
    # expires_in = token['expires_in']
    # expires_at = token['expires_at']
    return token['access_token']

def get_devices_data(access_token):
    # Use the access token to try get some data from LoT
    log.info("Doing GET on: " + TAPI_DEVICES_URL)
    r = requests.get(
        TAPI_DEVICES_URL,
        headers = {
            "Authorization":"Bearer " + access_token
        }
    )
    log.info("received response code: " + str(r.status_code))
    if r.status_code != HTTP_OK:
        log.fatal("status code not 200")
        return
    log.info("status code 200")
    log.info("received response content: " + r.content)
    data = json.loads(r.content)
    return data

def write_json_data_to_file(data,filepath):
    with open(filepath,'w') as outfile:
        json.dump(data,outfile,indent=2)

def validate_data(data,schema):
    try:
        jsonschema.validate(data,schema)
    except jsonschema.exceptions.ValidationError:
        log.fatal("validation error")

def read_in_schema(filepath):
    return json.loads(open(filepath,'r').read())

def upload_data_to_s3(local_filepath,key,bucket):
    S3.put_object(
        Bucket=bucket,
        Body=open(local_filepath,'rb').read(),
        Key=key,
    )
 
def handler(event, context):
    try:
        key,secret = get_client_key_and_secret()
        access_token = get_access_token(key,secret)
        data = get_devices_data(access_token)
        log.info("Polled data for number of devices:" + str(len(data)))
        schema = read_in_schema(DEVICES_SCHEMA_FILEPATH)
        validate_data(data,schema)
        write_json_data_to_file(data,DATA_TMP_FILEPATH)
        upload_data_to_s3(DATA_TMP_FILEPATH,DATA_S3_KEY,DATA_BUCKET)
    except Exception as e:
        log.fatal(e)
