import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get the bucket names from environment variables
    target_bucket_1 = os.environ['TARGET_BUCKET_1']
    target_bucket_2 = os.environ['TARGET_BUCKET_2']
    
    # Get bucket and file details from the event
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    # Get the file content
    response = s3.get_object(Bucket=source_bucket, Key=file_key)
    file_content = response['Body'].read().decode('utf-8')

    # Check file content and decide the target bucket
    if file_content.strip() == "":
        target_bucket = target_bucket_1
    else:
        target_bucket = target_bucket_2

    # Move the object to the target bucket
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={'Bucket': source_bucket, 'Key': file_key},
        Key=file_key
    )
    
    # Delete the object from the source bucket
    s3.delete_object(Bucket=source_bucket, Key=file_key)

    return {
        'statusCode': 200,
        'body': f'File {file_key} moved to {target_bucket} and deleted from {source_bucket}.'
    }
