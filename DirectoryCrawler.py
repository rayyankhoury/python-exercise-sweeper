import os
import sys
import urllib
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from bs4.element import ResultSet
# from requests_html import HTMLSession
import subprocess
from collections import OrderedDict

_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"

directory_url = "https://www.exrx.net/Lists/Directory"

neck = "neck"
neck_url = "https://www.exrx.net/Lists/ExList/NeckWt"
shoulders = "shoulders"
shoulders_url = "https://www.exrx.net/Lists/ExList/ShouldWt"
upperarms = "upperarms"
upperarms_url = "https://www.exrx.net/Lists/ExList/ArmWt"
forearms = "forearms"
forearms_url = "https://www.exrx.net/Lists/ExList/ForeArmWt"
back = "back"
back_url = "https://www.exrx.net/Lists/ExList/BackWt"
chest = "chest"
chest_url = "https://www.exrx.net/Lists/ExList/ChestWt"
waist = "waist"
waist_url = "https://www.exrx.net/Lists/ExList/WaistWt"
hips = "hips"
hips_url = "https://www.exrx.net/Lists/ExList/HipsWt"
thighs = "thighs"
thighs_url = "https://www.exrx.net/Lists/ExList/ThighWt"
calves = "calves"
calves_url = "https://www.exrx.net/Lists/ExList/CalfWt"

names = [neck, shoulders, upperarms, forearms,
         back, chest, waist, hips, thighs, calves]
urls = [neck_url, shoulders_url, upperarms_url, forearms_url,
        back_url, chest_url, waist_url, hips_url, thighs_url, calves_url]


def get_soup(name, url):
    # URL Setup
    req = urllib.request.Request(url, headers={'User-Agent': _USER_AGENT})
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)

    return BeautifulSoup(page, "lxml")


main_section = get_soup(names[1], urls[1]).find(
    name="main", id="mainShell").article
divs = main_section.findAll("div", "col-sm-6")

for child in divs:
    lists = child.find("ul")
    if (lists != None):
        print(lists)
        print("\n\n\n")


while div.find_next_sibling("div") != None:

    lists = div.find("ul")
    if (lists != None):
        # print(lists)
        print("\n\n\n")

    div = div.find_next_sibling("div")

    # print(.find("div"))
