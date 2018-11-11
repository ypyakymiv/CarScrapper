import scraper
import requests
import re
from bs4 import BeautifulSoup
import time

EBAY_SEARCH_URL = "https://www.ebay.com/sch/i.html"

def getPartsToScrapeFor():
    if 'parts' not in getPartsToScrapeFor.__dict__:
        f = open("parts.txt", "r")
        raw = f.readlines()
        f.close()
        raw[:] = [s.strip() for s in raw]
        getPartsToScrapeFor.parts = raw
    return getPartsToScrapeFor.parts

def getPriceFor(str):
    price_regex = lambda str : re.search("(?<=\$)[\d,]*", str)

    params = {
        '_nkw': str
    }

    r = None
    bad = True

    while bad:
        try:
            r = requests.get(EBAY_SEARCH_URL, params=params)
            if scraper.checkRequest(r):
                bad = False
        except:
            time.sleep(scraper.timeout())
            continue

    res = BeautifulSoup(r.text, 'html.parser')
    first_listing = res.find(id="srp-river-results-listing1")

    if first_listing:
        price = first_listing.find(class_="s-item__price").text
        price = price_regex(price)
        if price:
            return price.group()
        # great
    else:
        return "0"

def partOut(listing):
    name = listing['name']
    parts = getPartsToScrapeFor()
    prices = {}
    for part in parts:
        prices[part] = getPriceFor(name + ' ' + part)
        print("... " + part)

    return prices
