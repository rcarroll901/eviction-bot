
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

import re
import os
import requests as rq
from bs4 import BeautifulSoup


START_DATE = '13-MAR-2020'
EVICTION_CASE_TYPE = '16%20-%20FED%20-%20OTHER'
os.environ['NAME_SEARCH_LINK'] = 'https://gscivildata.shelbycountytn.gov/pls/gnweb/ck_public_qry_cpty.cp_personcase_srch_details?backto=P&soundex_ind=&partial_ind=&last_name={last_name}&first_name={first_name}&middle_name=&begin_date={start_date}&end_date=&case_type={eviction_case_type}&id_code=&PageNo=1'
os.environ['CASE_LINK'] = 'https://gscivildata.shelbycountytn.gov/pls/gnweb/ck_public_qry_doct.cp_dktrpt_docket_report?backto=P&case_id={}&begin_date=&end_date='


class EvictionScraper:
    
    CASE_LINK = os.environ["CASE_LINK"]
    NAME_SEARCH_LINK = os.environ["NAME_SEARCH_LINK"]
    
    def scrape_info(self, case_id, get_case_title: bool=False):
        page = rq.get(self.CASE_LINK.format(case_id))

        if 'No case was found' in page.text:
            return {}
        
        soup = BeautifulSoup(page.text, 'html.parser')
        scrape_dict = {'Scraper Confirmed (Case No.)': 'Yes'}

        last_date = self._scrape_last_court_date(soup)
        scrape_dict.update(last_date)

        sched_date = self._scrape_scheduled_court_date(soup)
        scrape_dict.update(sched_date)

        if get_case_title:
            case_title = self._scrape_case_title(soup)
            scrape_dict.update(case_title)

        return scrape_dict
    

    def scrape_by_name(self, query_args):
        """
        attempt to identify an eviction case by searching for an applicant name. If a case exists, then get the hearing information.

        params:
            query_args: dictionary of query arguments used to identify and verify a case by a name search

        returns:
            dictionary of case information, if available
        """
        page = rq.get(self.NAME_SEARCH_LINK.format(
            last_name=query_args['last_name'], 
            first_name=query_args['first_name'],
            eviction_case_type=EVICTION_CASE_TYPE,
            start_date=START_DATE
            )
        )
        if 'No records found.' in page.text:
            return {}
        
        if 'Search Error' in page.text:
            #TODO: clean party names to avoid search errors (such as removing parentheses)
            return {}
        
        soup = BeautifulSoup(page.text, 'html.parser')
        case_id_el = soup.find_all('a', attrs={'href': re.compile('ck_public_qry_doct.cp_dktrpt_frames')})

        if len(case_id_el)> 1:
            print(f'MULTIPLE CASES: {query_args}')

        case_id = case_id_el[0].get_text(strip=True)
        scrape_dict = self.scrape_info(case_id, get_case_title=True)
        return scrape_dict


    def _scrape_last_court_date(self, soup):

        # column names in Airtable
        prev_date_headings = ['Previous Event Date', 'Previous Event Description', 'Previous Event Entry']

        # get last docket event
        last_date_info = list(soup.find('a', attrs={"name": "dockets"}).find_all('tr', attrs={'valign':'top'})[-1].stripped_strings)
        last_date_info[:2] = [' '.join(last_date_info[:2])] # date + time str concatenation
        last_date_info.pop(2) # get rid of extraneous "Entry"

        # zip into dict
        prev_event_scrape_dict = dict(zip(prev_date_headings, last_date_info))
        return prev_event_scrape_dict

    def _scrape_scheduled_court_date(self, soup):
        
        # Airtable column names
        scheduled_headings = ['Next Court Date Description', 'Next Court Date', 'Next Court Date Room', 'Next Court Date Location', 'Next Court Date Judge']
        
        # this message will appear if there is not a court date scheduled. Erases current entries in airtable
        if 'No case events were found' in soup.text:
            return {key: None for key in scheduled_headings}

        # scrape info
        next_date_info = list(soup.select_one('a[name="events"] > table').select('tr')[-1].stripped_strings)
        next_date_info[1:3] = [' '.join(next_date_info[1:3])] # combine date and time entries of list
        scrape_dict = dict(zip(scheduled_headings, next_date_info)) # zip together dict
        return scrape_dict
    

    def _scrape_case_title(self, soup):
        
        # Airtable column names
        scheduled_headings = ['Case Title']
        
        # this message will appear if there is not a court date scheduled. Erases current entries in airtable
        #if 'No case events were found' in soup.text:
        #    return {'Case Title': None}

        # scrape info
        case_title = list(soup.select_one('a[name="description"] > table').select('tr')[0].stripped_strings)
        case_title = [case_title[1].replace('\n', '')]
        scrape_dict = dict(zip(scheduled_headings, case_title)) # zip together dict
        return scrape_dict

# for one-off
def test():
    scr = EvictionScraper()

    # case with no next court date
    case_id0 = '2046164'
    info0 = scr.scrape_info(case_id0)

    # one scheduled dates
    case_id1 = '2070893'
    info2 = scr.scrape_info(case_id1)

    # two scheduled dates
    case_id2 = '2062450'
    info2 = scr.scrape_info(case_id2)

    print("Success")


# for one-off
def test_name_search():
    scr = EvictionScraper()

    # no case exists
    query_args = {'last_name': 'person', 'first_name': 'not'}
    info0 = scr.scrape_name_search(query_args)
    print("Success")


if __name__ == '__main__':
    test()
    test_name_search()
    