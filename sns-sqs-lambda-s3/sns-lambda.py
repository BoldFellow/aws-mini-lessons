import json
import boto3
import os

s3 = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    for record in event['Records']:
        sns = record['Sns']

        # Extract SNS message content
        sns_message = sns.get('Message', 'No message content')

        # Extract subject
        subject = sns.get('Subject', 'default-subject')

        # Sanitize filename (important in real systems)
        file_name = f"{subject}.txt".replace(" ", "_")

        try:
            s3.put_object(
                Bucket=bucket_name,
                Key=file_name,
                Body=sns_message
            )
            print(f"File {file_name} created successfully in bucket {bucket_name}.")
        except Exception as e:
            print(f"Error uploading file to S3: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Processed SNS messages successfully')
    }