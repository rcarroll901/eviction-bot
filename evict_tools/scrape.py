
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

import os
from datetime import datetime as dt
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



class EvictionScraper(Chrome):
    
    CASE_LINK = os.environ["CASE_LINK"]
    
    def __init__(self, chrome_path="/opt/bin/headless-chromium", driver_path="/opt/bin/chromedriver"):
        chrome_options = EvictionScraper.get_chrome_options(chrome_path)
        super().__init__(executable_path = driver_path, options=chrome_options)

    @staticmethod
    def get_chrome_options(chrome_path=None):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--single-process")
        if chrome_path:
            chrome_options.binary_location = chrome_path
        return chrome_options
    
    def scrape_info(self, case_id):
        self.get(self.CASE_LINK.format(case_id))

        scrape_dict = {'Scraper Confirmed (Case No.)': 'Yes'}

        last_date = self._scrape_last_court_date()
        scrape_dict.update(last_date)

        sched_date = self._scrape_scheduled_court_date()
        scrape_dict.update(sched_date)

        return scrape_dict

    def _scrape_last_court_date(self):
        prev_date_headings = ['Previous Event Date', 'Previous Event Description', 'Previous Event Entry']

        # get last docket event
        dets_xpath = '(//a[@name="dockets"]//tr[@valign="top"])[last()]'
        last_docket_entry_dets = [d.get_attribute('textContent') for d in self.find_elements_by_xpath(dets_xpath+'/td')]
        date = dt.strptime(last_docket_entry_dets[0], "%d-%b-%Y%I:%M %p").strftime("%m-%d-%Y %I:%M %p")
        desc = last_docket_entry_dets[1]
        
        entry_desc = self.find_element_by_xpath(dets_xpath + '/following-sibling::tr[1]/td[2]')
        entry_text = entry_desc.get_attribute('textContent')

        prev_event_scrape_dict = dict(zip(prev_date_headings, [date, desc, entry_text]))
        return prev_event_scrape_dict

    def _scrape_scheduled_court_date(self):
        # get scheduled event
        sched_xpath = '//a[@name="events"]//tr[@valign="top"]/td'
        case_event_schedule = [d.get_attribute('textContent') for d in self.find_elements_by_xpath(sched_xpath)]
        date_colname = 'Next Court Date'  # used multiple times, so keep separate
        scheduled_headings = ['Next Court Date Description', date_colname, 'Next Court Date Room', 'Next Court Date Location', 'Next Court Date Judge']

        if not case_event_schedule:
            scrape_dict = dict(zip(scheduled_headings, [None]*5)) # all are null
        else:
            case_event_schedule = case_event_schedule[-5:] # if multiple settings, grab last/updated one
            scrape_dict = dict(zip(scheduled_headings, case_event_schedule)) # zip together dict
            scrape_dict[date_colname] = dt.strptime(scrape_dict[date_colname], "%d-%b-%Y%I:%M %p").strftime("%m-%d-%Y %I:%M %p") if scrape_dict[date_colname] != '' else ''
        return scrape_dict
