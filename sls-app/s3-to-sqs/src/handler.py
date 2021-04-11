import json
import logging
import os
import sys
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_URL = os.getenv('QUEUE_URL')
SQS = boto3.client('sqs')


def read_file_from_s3(event):
    s3 = boto3.resource('s3')
    message = []
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        obj = s3.Object(bucket, key)
        base = obj.get()['Body'].read().decode('utf8')
        message.append(base)
    return message


def producer(event, context):
    queue_message = read_file_from_s3(event)
    status_code = 200
    message = ''

    # if not event['body']:
    #     return {'statusCode': 400, 'body': json.dumps({'message': 'No body was found'})}

    try:
        message_attrs = {
            'AttributeName': {'StringValue': 'AttributeValue', 'DataType': 'String'}
        }
        for message in queue_message:
            SQS.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=message,
                MessageAttributes=message_attrs,
            )
            message = 'Message accepted!'
    except Exception as e:
        logger.exception('Sending message to SQS queue failed!')
        message = str(e)
        status_code = 500

    return {'statusCode': status_code, 'body': json.dumps({'message': message})}
