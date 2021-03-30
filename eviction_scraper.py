
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

from datetime import datetime as dt
from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



class EvictionScraper(Chrome):
    
    CASE_LINK = "https://gscivildata.shelbycountytn.gov/pls/gnweb/ck_public_qry_doct.cp_dktrpt_docket_report?backto=D&case_id={}"
    
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

        scrape_dict = {}

        last_date = self._scrape_last_court_date()
        scrape_dict.update(last_date)

        sched_date = self._scrape_scheduled_court_date()
        scrape_dict.update(sched_date)

        return scrape_dict

    def _scrape_last_court_date(self):
        scrape_dict = {}

        # get last docket event
        dets_xpath = '(//a[@name="dockets"]//tr[@valign="top"])[last()]'
        last_docket_entry_dets = [d.get_attribute('textContent') for d in self.find_elements_by_xpath(dets_xpath+'/td')]
        scrape_dict['prev_event_date'] = dt.strptime(last_docket_entry_dets[0], "%d-%b-%Y%I:%M %p").strftime("%m-%d-%Y %I:%M %p")
        scrape_dict['prev_event_desc'] = last_docket_entry_dets[1]
        
        entry_desc = self.find_element_by_xpath(dets_xpath+'/following-sibling::tr[1]/td[2]')
        scrape_dict['prev_event_entry'] = entry_desc.get_attribute('textContent')

        return scrape_dict

    def _scrape_scheduled_court_date(self):
        # get scheduled event
        sched_xpath = '//a[@name="events"]//tr[@valign="top"]/td'
        case_event_schedule = [d.get_attribute('textContent') for d in self.find_elements_by_xpath(sched_xpath)]
        scheduled_headings = ['scheduled_event', 'scheduled_date', 'scheduled_room', 'scheduled_loc', 'scheduled_judge']

        if not case_event_schedule:
            scrape_dict = dict(zip(scheduled_headings, ['']*5)) # all are null
        else:
            assert len(case_event_schedule) == 5, "case event schedule should be length 5"
            scrape_dict = dict(zip(scheduled_headings, case_event_schedule)) # zip together dict
            scrape_dict['scheduled_date'] = dt.strptime(scrape_dict['scheduled_date'], "%d-%b-%Y%I:%M %p").strftime("%m-%d-%Y %I:%M %p")
        return scrape_dict

    @staticmethod
    def format_scrape_data(info):
        order = ['scheduled_event', 'scheduled_date', 'scheduled_room', 'scheduled_loc', 'scheduled_judge', 'prev_event_date', 'prev_event_desc', 'prev_event_entry']
        return [info[d] for d in order]