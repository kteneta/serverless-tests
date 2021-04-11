from aws_cdk import core as cdk

from aws_cdk import core
  
from aws_cdk import (
    aws_sqs as sqs,
    aws_iam as iam,
    aws_apigateway as _apigw,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_events as _events,
    aws_events_targets as _events_targets,
    aws_s3_notifications,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_source,
    core
)

class CdkAppStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        

        # ----------------------------------------------------------------
        # create dynamo table
        dynamo_table = _dynamodb.Table(
            self, "cdk_app_table",
            partition_key=_dynamodb.Attribute(
                name="id",
                type=_dynamodb.AttributeType.STRING
            )
        )

        # create producer lambda function
        write_to_dynamo_lambda = _lambda.Function(self, "write_to_dynamo_table",
                                              runtime=_lambda.Runtime.PYTHON_3_6,
                                              handler="dynamo_write.lambda_handler",
                                              code=_lambda.Code.asset("./src"))

        write_to_dynamo_lambda.add_environment("TABLE_NAME", dynamo_table.table_name)

        # grant permission to lambda to write to demo table
        dynamo_table.grant_write_data(write_to_dynamo_lambda)

        # create consumer lambda function
        get_from_dynamo_lambda = _lambda.Function(self, "get_from_dynamo_lambda_function",
                                              runtime=_lambda.Runtime.PYTHON_3_6,
                                              handler="dynamo_get.lambda_handler",
                                              code=_lambda.Code.asset("./src"))

        get_from_dynamo_lambda.add_environment("TABLE_NAME", dynamo_table.table_name)

        # grant permission to lambda to read from demo table
        dynamo_table.grant_read_data(get_from_dynamo_lambda)

        # ----------------------------------------------------------------


        # ----------------------------------------------------------------
        #Create the SQS queue
        queue = sqs.Queue(self, "SQSQueue")
        # ----------------------------------------------------------------


        # ----------------------------------------------------------------
        # s3 Trigger
        # create lambda function
        s3_consumer = _lambda.Function(self, "s3_consumer",
                                    runtime=_lambda.Runtime.PYTHON_3_8,
                                    handler="s3_consumer.main",
                                    code=_lambda.Code.asset("./src"))

        s3_consumer.add_environment("SQS_ARN", queue.queue_arn)

        # create s3 bucket
        s3 = _s3.Bucket(self, "cdkapps3bucket")

        # create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(s3_consumer)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)
        # ----------------------------------------------------------------


        # ---------------------------------------------------------------
        # Create an API GW Rest API
        
        base_api = _apigw.RestApi(self, 'cdk-api',
        rest_api_name='cdk-api')

        base_path = base_api.root.add_resource('resource')
        
        resource_lambda_integration = _apigw.LambdaIntegration(get_from_dynamo_lambda, proxy=True)
        
        base_path.add_method('GET', resource_lambda_integration)
        # ----------------------------------------------------------------