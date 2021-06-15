import os
import sys

sys.path.append("/opt")
sys.path.append("package")
sys.path.append("package/bin")

from airtable import Airtable

# get Airtable
base_key = os.environ["AT_BASE_KEY"]
evictions_table_name = os.environ["AT_TABLE_NAME"]
api_key = os.environ["AT_API_KEY"]
applications_table_name = os.environ["AT_TABLE_NAME_APPLICANT"]


class AirTableClass:
    def __init__(self):
        self.airtable_evictions = Airtable(
            base_key=base_key, table_name=evictions_table_name, api_key=api_key
        )
        self.airtable_applications = Airtable(
            base_key=base_key,
            table_name=applications_table_name,
            api_key=api_key,
        )

    def get_case_ids(self):
        # read in all eviction record_id + case numbers
        response = self.airtable_evictions.get_all(
            fields=["Eviction Case Number"],
            formula='AND({Eviction Case Number}!="", {Eviction Case Number}!="2031057")',
        )
        return [
            {
                "record_id": r["id"],
                "case_id": r["fields"]["Eviction Case Number"][0],
            }
            for r in response
        ]

    def get_names(self):
        # read in all applicant record_id + first and last names
        response = self.airtable_applications.get_all(
            fields=["First name", "Last name", "Eviction Cases"]
        )
        valid_response = [
            record
            for record in response
            if "First name" in record["fields"]
            and "Last name" in record["fields"]
            and "Eviction Cases" not in record["fields"]
        ]
        return [
            {
                "record_id": r["id"],
                "first_name": r["fields"]["First name"],
                "last_name": r["fields"]["Last name"],
            }
            for r in valid_response
        ]

    def get_records(self):
        # get the case ids and names for both the case number and the partial name searches
        _case_ids = self.get_case_ids()
        _names = self.get_names()
        return _case_ids + _names

    def update_row(self, record_id, scrape_dict):
        # update airtable data. if the dictionary contains the applications_record_id field, then it has to
        # create a new record in evictions and then link it to the corresponding applications record.
        if (
            type(scrape_dict) == list
            and "applications_record_id" in scrape_dict[0]
        ):
            new_record_ids = []
            for _dict in scrape_dict:
                evictions_record = _dict.copy()
                evictions_record.pop("applications_record_id")
                resp = self.airtable_evictions.insert(evictions_record)
                new_record_ids.append(resp["id"])
                # update the applications table to point to the new eviction record(s)
            self.airtable_applications.update(
                scrape_dict[0]["applications_record_id"],
                {"Eviction Cases": new_record_ids},
            )
        else:
            self.airtable_evictions.update(record_id, scrape_dict)

        return "Success"


if __name__ == "__main__":
    airtable_interface = AirTableClass()
    response = airtable_interface.get_records()
