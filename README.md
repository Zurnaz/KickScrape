#KickScrap

Simple Kickstarter webs scraper python script that gets basic details of currently live campaigns and the pledges using selenium.

Uses SQLite as the database and stores the data into two tables campaigns and pledges.

## Installing

You need Selenium, SQLite and geckodriver.

I also could only get it working on the Firefox nightly build due to something with the geckodriver and ended up working around the JSON viewer. It should be enabled by default.

## Basic Usage

The script requires no parameters and the database is named KickScrapeYEAR_TIME.SQLite

You can modify the QUERY_STRING to change the filtering on the script. An easy way to do this is to go to www.kickstarter.com/discover/advanced?raised=1 and play around with the advanced setting and other options until your happy then at the end add "&format=json&page="

I use DBeaver to query the database but you can use whatever you want.

### Example SQL Query
Here is a query I generally use changing %shirt% to an item your interested in as reward. Try to go for generic terms unless you know specifically what your looking for like cards, dice, etc.

SELECT  
campaigns.title, campaigns.blurb, pledges.body, campaigns.currency, pledges.amount, campaigns.ending_date   
FROM  
pledges join campaigns on  pledges.campaign_id = campaigns.id
WHERE
body like '%shirt%' AND amount < 50

### Licence
This project is licensed under the terms of the MIT license.
