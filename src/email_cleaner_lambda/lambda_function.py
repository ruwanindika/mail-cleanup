import boto3
def lambda_handler(event, context):
    result = "Hello World 123"
    return {
        'statusCode' : 200,
        'body': result
    }