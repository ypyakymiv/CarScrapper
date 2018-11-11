import requests
import re
import scraper
import pdb
import time
import urllib
import part_scraper
from bs4 import BeautifulSoup

IAAI_URL = "https://www.iaai.com"
SEARCH = "/Search"
CHANGE_KEY = "/ChangeKey"
BUY_NOW = "crefiners=|quicklinks:i-buy%20fast"
IAAI_VEHICLES = IAAI_URL + "Vehicle"


def has_next_page(response):
    raw = response.find(id="dvSearchList").find(class_="col-12 flexbox flexCenter").find("div", class_="flexItem").text
    nums = raw.split("of")
    for i, num in enumerate(nums):
        nums[i] = int(num)
    current, total = nums
    print("-----------------------")
    print("Got page " + str(current) + " of " + str(total))
    print("-----------------------")
    return current < total

def initialPageURL():
    return IAAI_URL + SEARCH + "?" + BUY_NOW

def changeKey(n, t, i):
    url = IAAI_URL + SEARCH + CHANGE_KEY
    data = "{'URL': '" + i + "', 'Key': '" + t + "', 'Value': '" + n + "'}"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    bad = True

    r = None

    while bad:
        r = None

        try:
            r = requests.post(url, data=data, headers=headers)
        except:
            time.sleep(scraper.timeout())
            continue

        if scraper.checkRequest(r):
            bad = False
    return r

def nextPageURL(response):
    if not has_next_page(response):
        return None

    text_is_next = lambda node : node.text and node.text == "Next"
    expr = r"(?<=[('])[^',]+(?=[),'])"

    nextButton = response.find(text_is_next)

    n, t, i = re.findall(expr, nextButton['onclick'])
    nextPagePath = changeKey(n, t, i).text

    if nextPagePath:
        return IAAI_URL + '/' + nextPagePath
    else:
        print("error")
        # error

def getURL(row):
    sep_url = lambda str : re.search("(?<=..).*", str)
    url = sep_url(row.find("a")["href"]).group()

    return IAAI_URL + url

def getVIN(row):
    vin_regex = lambda str : re.search(r"(?<=VIN: )\w*", str)
    has_vin = lambda node : node.text and vin_regex(node.text)

    vin = row.find(has_vin)
    if vin:
        return vin_regex(vin.text).group()
    else:
        print("Get VIN error")
        # error

def getName(row):
    return row.find("h4").text

def getLocation(row):
    location = row.find(width="160").find("p").find("a")

    if location:
        return location.text
    else:
        print("Get location error")

def getSaleTime(row):
    saleTime = row.find(width="200").find("p").text

    return saleTime

def getPrice(row):
    price_regex = lambda str : re.search("(?<=\$)[\d,]*", str)

    price = price_regex(row.find(width="200").find("span").text).group()
    return price

def stripRow(row):
    name = getName(row)
    vin = getVIN(row)
    location = getLocation(row)
    saleTime = getSaleTime(row)
    price = getPrice(row)
    url = getURL(row)

    return {
        "name": name,
        "vin": vin,
        "location": location,
        "saleTime": saleTime,
        "url": url,
        "price": price
    }


def stripListings(response):
    rows = response.find("table", class_="table").find("tbody").find_all("tr")
    data = []
    for row in rows:
        data.append(stripRow(row))
        # print(data)

    return data


def headers():
    parts = part_scraper.getPartsToScrapeFor()

    total = ""

    if len(parts) > 1:
        total = "\tTotal Part Out Value"

    partsHeaders = ""

    for part in parts:
        partsHeaders = partsHeaders + "\t" + part

    return "Name\tVIN\tLocation\tSaleTime\tURL\tPrice" + total + partsHeaders + "\n"

def output(row, partPrices):
    origin = lambda r : "{n}\t{v}\t{l}\t{s}\t{u}\t{p}".format(n=r["name"], v=r["vin"], l=r["location"], s=r["saleTime"], p=r["price"], u=r["url"])
    parts = part_scraper.getPartsToScrapeFor()

    prices = ""

    total = 0

    for part in parts:
        total = total + int(partPrices[part])
        prices = prices + "\t" + partPrices[part]

    partsTotal = ""

    if len(parts) > 1:
        partsTotal = "\t" + str(total)

    return origin(row) + partsTotal + prices + "\n"

def fetchBuyNowListings():

    f = open("scrappers.tsv", "a")
    f.write(headers())

    url = initialPageURL()
    while url:
        r = None

        try:
            r = requests.get(url, timeout=5)
        except:
            time.sleep(scraper.timeout())
            continue

        if not scraper.checkRequest(r):
            continue

        res = BeautifulSoup(r.text, 'html.parser')
        page = stripListings(res)

        for row in page:
            print("Parting out " + row["name"])
            f.write(output(row, part_scraper.partOut(row)))

        url = nextPageURL(res)

    f.close()


fetchBuyNowListings()
