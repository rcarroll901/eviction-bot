#!/usr/bin/env python3

import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

import os
import json
import time
from datetime import datetime as dt
from subprocess import call

import evict_tools.persist as so
import evict_tools.message as sq
from evict_tools.scrape import EvictionScraper

print('Loading bot function...')

def lambda_handler(event, context):
    call('rm -rf /tmp/*', shell=True)
    
    # if cloudwatch event, then upload all cases to SQS
    if not event.get('Records'):
        print('Invoked by CloudWatch')
        case_ids = so.get_case_ids()
        sq.upload(case_ids)
        print('SQS cases upload complete')
    else: # if not, then sqs event = scrape case
        print(f'Invoked by SQS: {case_id}')

        # parse json message from SQS queue
        message = event['Records'][0]['body']
        message = json.loads(message)
        case_id = message['case_id']
        record_id = message['record_id']
        
        # scrape info using case number
        scr = EvictionScraper()
        info = scr.scrape_info(case_id=case_id)
        
        # write to Airtable
        so.update_row(record_id, info)
        print('Upload of case info succeeded')


# for one-off
def test():
    message = {'record_id': 'rec000bwe4zwJ7PUZ', 'case_id': '2046164'}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")

if __name__ == '__main__':
    test()
