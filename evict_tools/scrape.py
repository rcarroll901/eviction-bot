
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

import os
import requests as rq
from bs4 import BeautifulSoup

class EvictionScraper:
    
    CASE_LINK = os.environ["CASE_LINK"]
    
    def scrape_info(self, case_id):
        page = rq.get(self.CASE_LINK.format(case_id))

        if 'No case was found' in page.text:
            return {}
        
        soup = BeautifulSoup(page.text, 'html.parser')
        scrape_dict = {'Scraper Confirmed (Case No.)': 'Yes'}

        last_date = self._scrape_last_court_date(soup)
        scrape_dict.update(last_date)

        sched_date = self._scrape_scheduled_court_date(soup)
        scrape_dict.update(sched_date)

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

        # this message will appear if there is not a court date scheduled
        if 'No case events were found' in soup.text:
            return {}
        
        # Airtable column names
        scheduled_headings = ['Next Court Date Description', 'Next Court Date', 'Next Court Date Room', 'Next Court Date Location', 'Next Court Date Judge']
        
        # scrape info
        next_date_info = list(soup.select_one('a[name="events"] > table').select('tr')[-1].stripped_strings)
        next_date_info[1:3] = [' '.join(next_date_info[1:3])] # combine date and time entries of list
        scrape_dict = dict(zip(scheduled_headings, case_event_schedule)) # zip together dict
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

if __name__ == '__main__':
    test()