
import sys
sys.path.append('/opt')
import json
import boto3

def upload(case_ids):
    sqs = boto3.client('sqs', region_name='us-east-1')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/494557780599/dev-eviction-bot'
    
    for c in case_ids:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({"case_id": c})
        )
    
    return "Complete"