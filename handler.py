import os

try:
    import unzip_requirements
except ImportError:
    pass

import json
import uuid
import boto3
import requests
from botocore.config import Config

import secret

dynamoDb = boto3.resource('dynamodb')
blobs_table = dynamoDb.Table('blobs')
urls_table = dynamoDb.Table('callback_urls')
s3_client = boto3.client('s3', config=Config(signature_version='s3v4'),
                         aws_access_key_id=secret.aws_access_key_id,
                         aws_secret_access_key=secret.aws_secret_access_key,
                         region_name=secret.region_name)
bucket_name = secret.bucket_name


def build_response(status_code, body=None):
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)

    return response


def save_blob(event, context):
    print()
    request_body = json.loads(event['body'])
    callback_url = request_body['callback_url']
    file_name = request_body['file_name']

    item = {
        'file_name': file_name,
        'callback_url': callback_url
    }
    urls_table.put_item(Item=item)
    upload_url = create_presigned_url(file_name, 'put_object')
    return build_response(200, {'Url to upload': upload_url})


def create_presigned_url(file_name, client_method, expiration=3600):
    url = s3_client.generate_presigned_url(
        ClientMethod=client_method,
        Params={
            'Bucket': bucket_name,
            'Key': file_name
        },
        ExpiresIn=expiration
    )
    return url


def get_blob(event, context):
    blob_id = event['pathParameters']['blobId']
    response = blobs_table.get_item(
        Key={
            'id': blob_id
        }
    )

    if 'Item' in response:
        download_blob_url = response['Item']['url']
        return build_response(200, {'download_url': download_blob_url})

    return build_response(404, {'Message': f'There is no blob with id={blob_id}'})


def upload_file_event(event, context):
    key = event['Records'][0]['s3']['object']['key']
    blob_id = put_blob(key)
    url_item = urls_table.get_item(
        Key={
            'file_name': key
        }
    )

    callback_url = url_item['Item']['callback_url']
    response = {
        'message': 'Uploading file has been successfully completed.',
        'blob_id': blob_id
    }
    requests.post(callback_url, json=response)


def put_blob(object_name):
    download_url = create_presigned_url(object_name, 'get_object')
    blob_id = generate_uuid()
    blob_item = {
        'id': blob_id,
        'url': download_url
    }
    blobs_table.put_item(Item=blob_item)
    return blob_id


def generate_uuid():
    return str(uuid.uuid4())
