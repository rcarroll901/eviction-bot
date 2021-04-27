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

import sheet_ops as so
import sqs_ops as sq
from eviction_scraper import EvictionScraper

print('Loading bot function...')


def lambda_handler(event, context):
    call('rm -rf /tmp/*', shell=True)
    
    service = so.get_google_service()
    # if cloudwatch event, then upload to SQS
    if not event.get('Records'):
        print('Invoked by CloudWatch')
        case_ids = so.get_case_ids(service)
        sq.upload(case_ids)
        print('SQS cases upload complete')
    else: # then sqs event
        message = event['Records'][0]['body']
        message = json.loads(message)
        case_id = message['case_id']
        
        print(f'Invoked by SQS: {case_id}')
        if os.environ.get('LAMBDA_ENV') is not None:
            driver = EvictionScraper()
        else:
            driver = EvictionScraper(chrome_path=None, driver_path="/usr/local/bin/chromedriver")
        
        info = driver.scrape_info(case_id=case_id)
        info_list = EvictionScraper.format_scrape_data(info)
        driver.quit()
        
        rows = so.get_rows_to_update(service, case_id)
        so.update_rows(service=service, info=info_list, rows=rows)
        print('Upload of case info succeeded')


# for one-off
def test():
    message = {'case_id': '2074895'}
    sqs_event = {'Records': [{'body': json.dumps(message)}]}
    lambda_handler(event=sqs_event, context=None)
    print("Success")

if __name__ == '__main__':
    test()
