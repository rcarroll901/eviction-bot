import os
import sys
sys.path.append('/opt')
import json
import boto3

def upload(case_ids):
    """
    Args:
        case_ids (list(str)): List of case ids to scrape
    """

    sqs = boto3.client('sqs', region_name='us-east-1')
    queue_url = os.environ["SQS_URL"]
    
    for c in case_ids:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(c)
        )
    
    return "Complete"

def test():
    status = upload([{'record_id': 'rec000bwe4zwJ7PUZ', 'case_id': '2046164'}])
    print(status)

if __name__ == '__main__':
    test()