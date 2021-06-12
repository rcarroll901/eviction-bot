
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

import re
import os
import requests as rq
from bs4 import BeautifulSoup


class EvictionScraper:    
    def __init__(self):
        self.case_link = os.environ["CASE_LINK"]
        self.name_search_link = os.environ["NAME_SEARCH_LINK"]
    
    def scrape_info(self, case_id, get_case_title: bool=False):
        page = rq.get(self.case_link.format(case_id))

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

        Args:
            query_args: dictionary of query arguments used to identify and verify a case by a name search

        Returns:
            dictionary of case information, if available
        """
        query_args_ = self._clean_names(query_args)

        page = rq.get(self.name_search_link.format(
            last_name=query_args_['last_name'],
            first_name=query_args_['first_name']
            )
        )
        if 'No records found.' in page.text:
            return {}
        
        if 'Search Error' in page.text:
            return {'Name Search Error': 'Yes'}
        
        soup = BeautifulSoup(page.text, 'html.parser')
        case_id_el = soup.find_all('a', attrs={'href': re.compile('ck_public_qry_doct.cp_dktrpt_frames')})

        if len(case_id_el)> 1:
            case_title_els = soup.find_all('b', text=re.compile('Case:'))
            case_titles = ', '.join([' '.join(list(x.find_next('i').stripped_strings)) for x in case_title_els])
            return {
                'Multiple Cases Returned': case_titles,
                'Potential Eviction': True
            }

        # extract the case title so staff can review whether it is a true match
        case_title_el = soup.find('b', text=re.compile('Case:')).find_next('i')
        case_title = ' '.join(list(case_title_el.stripped_strings))

        case_id = case_id_el[0].get_text(strip=True)
        scrape_dict = self.scrape_info(case_id, get_case_title=True)
        scrape_dict.update({
            'Potential Eviction': True, 
            'Case Title': case_title, 
            }
        )
        return scrape_dict

    def _clean_names(self, query_args):
        query_args['last_name'] = re.sub(r"\([^()]*\)", "", query_args['last_name']).strip()
        query_args['first_name'] = re.sub(r"\([^()]*\)", "", query_args['first_name']).strip()
        return query_args

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
        
        # sometimes date + time are not listed
        if len(next_date_info) == 6: # listed
            next_date_info[1:3] = [' '.join(next_date_info[1:3])] # combine date and time entries of list
        elif len(next_date_info) == 4: # not listed
            next_date_info.insert(1, None)
        else:
            raise ValueError(f'returned list {next_date_info} should be length 4 or 6')

        # zip together dict
        scrape_dict = dict(zip(scheduled_headings, next_date_info)) 

        return scrape_dict
    
    def _scrape_case_title(self, soup):
        
        # Airtable column names
        scheduled_headings = ['Case Title']

        # scrape info
        case_title = list(soup.select_one('a[name="description"] > table').select('tr')[0].stripped_strings)
        case_title = [case_title[1].replace('\n', '')]
        scrape_dict = dict(zip(scheduled_headings, case_title)) # zip together dict
        return scrape_dict
    
    def get_case(self, message):
        if 'first_name' in message:
            scrape_dict = self.scrape_by_name(message)
            scrape_dict.update({'applications_record_id': message['record_id']}) # need to include so we can link the new evictions record to the application
        else:
            scrape_dict = self.scrape_info(message['case_id'])
        print(scrape_dict)
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

    # one date with no date/time
    case_id1b = '2065712'
    info1b = scr.scrape_info(case_id1b)

    # two scheduled dates
    case_id2 = '2062450'
    info2 = scr.scrape_info(case_id2)

    print("Success")

def test_name_search():
    scr = EvictionScraper()

    # no case exists, test returns empty dictionary
    query_args = {'last_name': os.getenv('TEST_LAST_NAME_MATCH'), 'first_name': os.getenv('TEST_FIRST_NAME_MATCH')}
    info0 = scr.scrape_by_name(query_args)
    print(info0)
    assert 'Next Court Date' in info0

    # no case exists, test returns empty dictionary
    query_args = {'last_name': 'person', 'first_name': 'not'}
    info0 = scr.scrape_by_name(query_args)
    assert not info0

    # test to ensure parentheses and the text inside them are removed
    # this happens occasionally and would cause an error in the query
    query_args = {'last_name': 'person (true)', 'first_name': 'this (is not)'}
    clean_query_args = scr._clean_names(query_args)
    assert clean_query_args['last_name'] == 'person'
    assert clean_query_args['first_name'] == 'this'
    
    # test multiple cases returned
    query_args = {'last_name': os.getenv('TEST_LAST_NAME_MULTIPLE_CASES'), 'first_name': os.getenv('TEST_FIRST_NAME_MULTIPLE_CASES')}
    info0 = scr.scrape_by_name(query_args)
    assert 'Multiple Cases Returned' in info0.keys()


if __name__ == '__main__':
    test()
    test_name_search()
    