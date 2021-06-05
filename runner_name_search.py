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
        applicant_names = so.get_names()
        sq.upload(applicant_names)
        print('SQS applicant names upload complete')
    else: # if not, then sqs event = scrape case

        # parse json message from SQS queue
        message = event['Records'][0]['body']
        message = json.loads(message)
        query_args = message
        print(f'Invoked by SQS: {query_args}')

        # scrape info using case number
        scr = EvictionScraper()
        info = scr.scrape_by_name(query_args=query_args)
        
        # write to Airtable
        #TODO: need to determine which airtable table to push the data to and update accordingly.
        # potential issue if the case id search and name search return case info, but ideally they return the same information
        so.update_row(message['record_id'], info)
        print('Upload of case info succeeded')


# for one-off
def test():
    message = {'record_id': 'rec3n0wutEViyarOx', 'first_name': 'test', 'last_name': 'test'}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")

if __name__ == '__main__':
    test()
