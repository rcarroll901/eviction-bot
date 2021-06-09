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
    call("rm -rf /tmp/*", shell=True)

    # if cloudwatch event, then upload all cases to SQS
    if not event.get("Records"):
        print("Invoked by CloudWatch")
        case_ids = so.get_case_ids()
        sq.upload(case_ids)
        print("SQS cases upload complete")
    else:  # if not, then sqs event = scrape case

        # parse json message from SQS queue
        message = event["Records"][0]["body"]
        message = json.loads(message)
        case_id = message["case_id"]
        record_id = message["record_id"]
        print(f"Invoked by SQS: {case_id}")

        # case_id's in Airtable are being changed to nonsensical values
        # so we test them here (since they should be all numbers/no letters)
        try:
            test = int(case_id)
        except ValueError:
            print(f"Invalid Case ID: {case_id}")
            return "Fail"
        # scrape info using case number
        scr = EvictionScraper()
        info = scr.scrape_info(case_id=case_id)

        # write to Airtable
        so.update_row(record_id, info)
        print("Upload of case info succeeded")
        return "Success"


# for one-off
def test():
    message = {"record_id": "recEIgQdwtZlHM5KG", "case_id": "1681222"}
    sqs_event = {"Records": [{"body": json.dumps(message)}]}
    print(sqs_event)
    lambda_handler(event=sqs_event, context=None)
    print("Success")


if __name__ == "__main__":
    test()
