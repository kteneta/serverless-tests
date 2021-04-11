import json
import logging
import os
import sys
import boto3
import time
import uuid

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

QUEUE_URL = os.getenv('QUEUE_URL')
SQS = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')


def consumer(event, context):
    for record in event['Records']:
        logger.info(f'Message body: {record["body"]}')
        logger.info(
            f'Message attribute: {record["messageAttributes"]["AttributeName"]["stringValue"]}'
        )
        create(record["body"])

def create(text):  
    timestamp = str(time.time())

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # write the todo to the database
    table.put_item(Item=item)
