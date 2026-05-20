import json
import boto3
import os

# Initialize S3 client
s3 = boto3.client('s3')

bucket_name = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    # Loop through each SQS message (in case multiple messages are received)
    for record in event['Records']:
        message = json.loads(record['body'])  # Parse the message

        # Extract the SNS message body (assuming it's a text message)
        sns_message = message.get('Message', 'No message content')  # Get SNS message

        # Extract the subject from the SNS message
        subject = message.get('Subject', 'default-subject')  # Use 'default-subject' if no subject is found
        file_name = f"{subject}.txt"  # Use the subject as part of the file name


        # Upload the SNS message content to S3 as the file content
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
