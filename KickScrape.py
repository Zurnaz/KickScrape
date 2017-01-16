'''
Scrape details of the current active campaigns and their pledges.
Creates a database of all the possible pledges so you can search for stuff you like.
'''

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sqlite3 as lite
import sys
import os
import json
import re
import locale


class Database:

    def __init__(self, campaign_table, pledge_table):
        file_location = os.path.dirname(os.path.realpath(__file__))+"\\"
        file_name = "KickScrape"+time.strftime("%Y%m%d")+"_"+time.strftime("%H%M")+".sqlite"
        self.sqlite_file = file_location + file_name
        self.campaign = campaign_table
        self.pledge = pledge_table
        self.conn = None
        self.cur = None


    def create_tables(self):
        conn = lite.connect(self.sqlite_file)
        cur = conn.cursor()
        try:
            cur.execute ('''CREATE TABLE campaigns (id INTEGER PRIMARY KEY
                                                    , title VARCHAR(255)
                                                    , blurb VARCHAR(255)
                                                    , link VARCHAR(255)
                                                    , ending_date DATETIME
                                                    , currency VARCHAR(10))''')

            cur.execute('''CREATE TABLE pledges (id INTEGER PRIMARY KEY
                                                , campaign_id INTEGER
                                                , title VARCHAR(255)
                                                , body VARCHAR(255)
                                                , amount decimal(12,4))''')

        except lite.IntegrityError:
            print('ERROR: Unable to create tables {}'.format(id))
            cur.close()
        conn.commit()
        cur.close()

    def add_pledge(self, campaign_id, pledge_id, title, body, amount):
        conn = lite.connect(self.sqlite_file)
        cur = conn.cursor()

        try:
            sql = ''' INSERT INTO pledges (id, campaign_id, title, body, amount)
            VALUES (?,?,?,?,?) '''
            task = (pledge_id, campaign_id, title, body, amount)
            cur.execute(sql, task)

        except lite.IntegrityError:
            print('ERROR: ID already exists in the pledge tables id column {}'.format(pledge_id))
        conn.commit()
        cur.close()

    def add_campaign(self, campaign_id, title, blurb, link, ending_date, currency):
        conn = lite.connect(self.sqlite_file)
        cur = conn.cursor()
        try:
            sql = ''' INSERT INTO campaigns (id, title, blurb, link, ending_date, currency)
            VALUES (?,?,?,?,?,?) '''
            task = (campaign_id, title, blurb, link, ending_date, currency)
            cur.execute(sql, task)

        except lite.IntegrityError:
            print('ERROR: ID already exists in the campaign tables id column {}'.format(campaign_id))
        conn.commit()
        cur.close()

    def open_connection(self):
        self.conn = lite.connect(self.sqlite_file)
        self.cur = conn.cursor()

    def close_connection(self):
        self.conn.commit()
        self.cur.close()

def init_driver():

    driver = webdriver.Firefox()
    #driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 5)
    return driver

class DataObject:
    def __init__(self,data_string):
        self.data = data_string

    def read(self):
        return self.data

def clean_currency_string(input_string):
    '''
    This function/method is slighly modified from:
    http://stackoverflow.com/a/27128381
    '''
    decimal_point_char = locale.localeconv()['decimal_point']
    clean = re.sub(r'[^0-9'+decimal_point_char+r']+', '', input_string)
    # probably going to regret using a float for a currency
    value = float(clean)
    return value

def lookup(driver):
    URL = "https://www.kickstarter.com/discover/advanced"
    QUERY_STRING = "?state=live&raised=2&sort=end_date&format=json&page="
    page = 1
    campaign_database = Database("Campaigns","Pledges")
    campaign_database.create_tables()
    while page > 0:
        driver.get(URL+QUERY_STRING+str(page))
        try:
            button = driver.wait.until(EC.element_to_be_clickable(
                (By.ID, "tab-1")))
            button.click()
        except TimeoutException:
            print("Button not found on page")

        time.sleep(5)
        pre = DataObject(driver.find_element_by_tag_name("pre").text)

        data = json.load(pre)
        if len(data["projects"]) > 0:
            for project in data["projects"]:
                campaign_database.add_campaign(project["id"]
                , project["name"]
                , project["blurb"]
                , project["urls"]["web"]["project"]
                , time.strftime('%m/%d/%Y %H:%M:%S',  time.gmtime(project["deadline"]))
                , project["currency"])

                driver.get(project["urls"]["web"]["rewards"])
                campaign_id = project["id"]
                extracted_data = driver.execute_script("""
                var results = {pledges:[]};
                var buffer = $( ".pledge-selectable-sidebar" );
                for(var i = 0; i < buffer.length; i++){
                    var data_temp ={"pledge_id" : '',
                                "title" : '',
                                "body" : '',
                                "amount" : ''};
                    if($(buffer[i]).attr("data-reward-id")>0)
                        {
                            data_temp["pledge_id"] = $(buffer[i]).attr("data-reward-id");
                            data_temp["title"] = $(buffer[i]).find(".pledge__title")[0].innerText;
                            data_temp["body"] = $(buffer[i]).find(".pledge__reward-description")[0].innerText;
                            data_temp["amount"] = $(buffer[i]).find(".money")[0].innerText;
                            results.pledges.push(data_temp);
                        }
                }
                return results;
                """)
                for pledge in extracted_data["pledges"]:
                    campaign_database.add_pledge(campaign_id
                    , pledge["pledge_id"]
                    , pledge["title"]
                    , pledge["body"]
                    , clean_currency_string(pledge["amount"]))

            page += 1

            if data["has_more"] == "true":
                page = 0
                break
        else:
            page = 0
            break


if __name__ == "__main__":
    driver = init_driver()
    lookup(driver)
    time.sleep(5)
    driver.quit()
