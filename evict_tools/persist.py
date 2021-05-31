import os
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

from airtable import Airtable

# get Airtable 
base_key = os.environ['AT_BASE_KEY']
table_name = os.environ['AT_TABLE_NAME']
api_key = os.environ['AT_API_KEY']
applicant_table_name = os.environ['AT_TABLE_NAME_APPLICANT']

airtable = Airtable(base_key=base_key, table_name=table_name, api_key=api_key)


def get_case_ids():
    # read in all eviction record_id + case numbers
    response = airtable.get_all(fields=['Eviction Case Number'], formula='AND({Eviction Case Number}!="", {Eviction Case Number}!="2031057")')
    return [{'record_id': r['id'], 'case_id': r['fields']['Eviction Case Number'][0]} for r in response]

def update_row(record_id, scrape_dict):
    airtable.update(record_id, scrape_dict)
    return "Success"

def get_names():
    # read in all applicant record_id + first and last names
    airtable = Airtable(base_key=base_key, table_name=applicant_table_name, api_key=api_key)
    response = airtable.get_all(fields=['First name', 'Last name'], formula='AND({Last name}!="", {First name}!="", {Eviction Case Number}=="")')
    return [{'record_id': r['id'], 'first_name': r['fields']['First name'], 'last_name': r['fields']['Last name']} for r in response]

if __name__ == "__main__":
    response = get_names()
    print(response)