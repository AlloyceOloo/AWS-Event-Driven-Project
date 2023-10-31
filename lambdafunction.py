import json
import boto3
import csv
import os
import logging

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# Define your S3 bucket name and SQS queue URL
S3_BUCKET_NAME = ''
SQS_QUEUE_URL = ''
MAX_ROWS_PER_CSV = 100 # Maximum number of rows to be processed per CSV file

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Fetching objects from S3 bucket: {}".format(S3_BUCKET_NAME))

    try:
        # List all objects in the S3 bucket
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
        
        for obj in response.get('Contents', []):
            s3_object_key = obj['Key']
            rows_processed = 0
            
            # Download the CSV file from S3
            local_file_path = '/tmp/file.csv'
            s3.download_file(S3_BUCKET_NAME, s3_object_key, local_file_path)
            
            # Process the CSV file and send rows to SQS in batches of 10
            with open(local_file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                rows = list(csvreader)
                batch_size = 10
                for i in range(0, len(rows), batch_size):
                    if rows_processed >= MAX_ROWS_PER_CSV:
                        break
                    
                    batch_rows = rows[i:i + batch_size]
                    # Limit processing to MAX_ROWS_PER_CSV per CSV file
                    batch_rows = batch_rows[:MAX_ROWS_PER_CSV - rows_processed]
                    # Send rows to SQS
                    response = sqs.send_message_batch(
                        QueueUrl=SQS_QUEUE_URL,
                        Entries=[
                            {
                                'Id': str(idx),
                                'MessageBody': json.dumps(row)
                            } for idx, row in enumerate(batch_rows)
                        ]
                    )
                    logger.info(response)
                    rows_processed += len(batch_rows)
            
            # Clean up the local CSV file
            os.remove(local_file_path)

        return {
            'statusCode': 200,
            'body': json.dumps('Processing and sending messages to SQS complete!')
        }

    except Exception as e:
        logger.error("Error processing S3 objects: " + str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing S3 objects')
        }

