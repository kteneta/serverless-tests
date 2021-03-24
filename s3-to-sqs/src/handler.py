import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_URL = os.getenv('QUEUE_URL')
SQS = boto3.client('sqs')


def read_file_from_s3(event):
    s3 = boto3.client('s3')
    bucketname = event['Records'][0]['s3']['bucket']['name']
    itemname = event['Records'][0]['s3']['object']['key']
    with open('FILE_NAME', 'wb') as f:
        s3.download_fileobj(bucketname, itemname, f)
        print(f)
    
    


    # obj = s3.Object(bucketname, itemname)
    # body = obj.get()['Body'].read()
    # print(body)
    os.exit(0)

def producer(event, context):
    read_file_from_s3(event)
    status_code = 200
    message = ''

    if not event['body']:
        return {'statusCode': 400, 'body': json.dumps({'message': 'No body was found'})}

    try:
        message_attrs = {
            'AttributeName': {'StringValue': 'AttributeValue', 'DataType': 'String'}
        }
        SQS.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=event['body'],
            MessageAttributes=message_attrs,
        )
        message = 'Message accepted!'
    except Exception as e:
        logger.exception('Sending message to SQS queue failed!')
        message = str(e)
        status_code = 500

    return {'statusCode': status_code, 'body': json.dumps({'message': message})}


def consumer(event, context):
    for record in event['Records']:
        logger.info(f'Message body: {record["body"]}')
        logger.info(
            f'Message attribute: {record["messageAttributes"]["AttributeName"]["stringValue"]}'
        )