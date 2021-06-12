#!/usr/bin/env python3

import sys

sys.path.append("/opt")
sys.path.append("package")
sys.path.append("package/bin")

import os
import json
import time
from datetime import datetime as dt
from subprocess import call

import evict_tools.persist as so
import evict_tools.message as sq
from evict_tools.scrape import EvictionScraper

print("Loading bot function...")


def lambda_handler(event, context):
    call('rm -rf /tmp/*', shell=True)
    
    airtable = so.AirTableClass()
    # if cloudwatch event, then upload all cases to SQS
    if not event.get('Records'):
        print('Invoked by CloudWatch')
        records = airtable.get_records()
        sq.upload(records)
        print('SQS cases upload complete')
    else: # if not, then sqs event = scrape case
        # parse json message from SQS queue
        message = event["Records"][0]["body"]
        message = json.loads(message)
        record_id = message['record_id']
        #print(f'Invoked by SQS: {case_id}')

        # scrape info using case number
        scr = EvictionScraper()
        info = scr.get_case(message=message)
        
        # write to Airtable
        airtable.update_row(record_id, info)
        print('Upload of case info succeeded')


# for one-off
def test_case():
    message = {'record_id': 'recTxh0dxxzaAocnD', 'case_id': '2072380'}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")

# for one-off
def test_name():
    message = {'record_id': 'recQENZIuEoEZgTmf', 
    'last_name': os.getenv('TEST_LAST_NAME_MULTIPLE_CASES'), 'first_name': os.getenv('TEST_FIRST_NAME_MULTIPLE_CASES')}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")


# for one-off
def test_name2():
    message = {'record_id': 'recFxXJpDBtq2wvwH', 
    'last_name': os.getenv('TEST_LAST_NAME_MATCH'), 'first_name': os.getenv('TEST_FIRST_NAME_MATCH')}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")


if __name__ == '__main__':
    test_case()
    test_name()
    test_name2()
