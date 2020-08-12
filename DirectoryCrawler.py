import os
import sys
import urllib
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from bs4.element import ResultSet
from bs4.element import NavigableString
# from requests_html import HTMLSession
import subprocess
from collections import OrderedDict
from requests import get

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
    #req = urllib.request.Request(url, headers={'User-Agent': _USER_AGENT})
    response = get(url, headers={'User-Agent': _USER_AGENT})
    # try:
    #     page = urllib.request.urlopen(req)
    # except urllib.error.URLError as e:
    #     print(e.reason)

    return BeautifulSoup(response.text, features="lxml")


for name, url in zip(names, urls):
    main_section = get_soup(name, url).find(
        name="main", id="mainShell").article
    divs = main_section.findAll("div", "col-sm-6")

    for child in divs:
        if child is None:
            continue
        # stretch exception in pectoralis minor on chest
        # print(child)
        # print("\n")
        # print("\n")
        if (child.text.strip().lower() ==
                "Stretch Doorway Chest Lying Shoulder Girdle Towel Shoulder Girdle Wall Shoulder Girdle Also see Doorway Chest Stretch for General Chest.Also see Broomstick Stretch for Supscapularis.".strip().lower()):
            continue
        temp_columns = child.find("ul")
        if temp_columns is None:
            continue

        columns_array = []
        columns_array.append(temp_columns)
        while (temp_columns.find_next_sibling("ul")):
            temp_columns = temp_columns.find_next_sibling("ul")
            columns_array.append(temp_columns)

            # print(columns)
            # print("\n")
            # print("\n")
        name = ""
        for columns in columns_array:
            for section in columns:
                if not isinstance(section, NavigableString) and section is not None:
                    try:
                        name = section.contents[0].strip().replace(
                            " ", "").replace("(", "").replace(")", "").lower()
                    except:
                        continue
                    links = section.findAll("a")
                    print(name)
                    print(links)
                    print("\n")

        # if (column != None):
        #     section = column.find('ul')
        #     while column.next_sibling != None:
        #         column = column.next_sibling
