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
import pprint
import pickle

_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"

directory_url = "https://www.exrx.net/Lists/Directory"
type_a = 'WeightExercises/'
type_b = 'Stretches/'
type_a_search = 'WeightExercises/(.*)/'
type_b_search = 'Stretches/(.*)/'

neck = ["Neck", "Sternocleidomastoid", "Splenius"]
neck_url = "https://www.exrx.net/Lists/ExList/NeckWt"
shoulders = ["Shoulders", "DeltoidAnterior",
             "DeltoidLateral", "DeltoidPosterior", "Supraspinatus"]
shoulders_url = "https://www.exrx.net/Lists/ExList/ShouldWt"
upperarms = ["UpperArms", "Triceps", "Biceps", "Brachialis"]
upperarms_url = "https://www.exrx.net/Lists/ExList/ArmWt"
forearms = ["Forearms", "Brachioradialis", "WristFlexors",
            "WristExtensors", "Pronators", "Supinators"]
forearms_url = "https://www.exrx.net/Lists/ExList/ForeArmWt"
back = ["Back", "BackGeneral", "LatissimusDorsi", "TrapeziusUpper",
        "Rhomboids", "Infraspinatus", "Subscapularis"]
back_url = "https://www.exrx.net/Lists/ExList/BackWt"
chest = ["Chest", "PectoralSternal", "PectoralClavicular",
         "PectoralisMinor", "SerratusAnterior"]
chest_url = "https://www.exrx.net/Lists/ExList/ChestWt"
waist = ["Waist", "RectusAbdominis", "Obliques", "ErectorSpinae"]
waist_url = "https://www.exrx.net/Lists/ExList/WaistWt"
hips = ["Hips", "GluteusMaximus", "HipAbductors",
        "HipFlexors", "HipExternalRotators"]
hips_url = "https://www.exrx.net/Lists/ExList/HipsWt"
thighs = ["Thighs", "Quadriceps", "Hamstrings", "HipAdductors"]
thighs_url = "https://www.exrx.net/Lists/ExList/ThighWt"
calves = ["Calves", "Gastrocnemius", "Soleus", "TibialisAnterior"]
calves_url = "https://www.exrx.net/Lists/ExList/CalfWt"

names = [neck[0], shoulders[0], upperarms[0], forearms[0],
         back[0], chest[0], waist[0], hips[0], thighs[0], calves[0]]
urls = [neck_url, shoulders_url, upperarms_url, forearms_url,
        back_url, chest_url, waist_url, hips_url, thighs_url, calves_url]
muscle_groups = [neck, shoulders, upperarms, forearms,
                 back, chest, waist, hips, thighs, calves]


def array_dictionary_extend_if_no_exist(dictionary, key, value):
    if not key in dictionary:
        dictionary[key] = value


def array_dictionary_extend(dictionary, key, value):
    if key in dictionary:
        temp = dictionary.get(key)
        # Here we check to see if this type of exercise has already been added to this muscle
        for key in value.keys():
            if key in temp:
                array1 = value.get(key)
                array2 = temp.get(key)
                value[key] = list(set(array1 + array2))
        temp.update(value)
    else:
        dictionary[key] = value


def get_soup(name, url):
    # URL Setup
    # req = urllib.request.Request(url, headers={'User-Agent': _USER_AGENT})
    response = get(url, headers={'User-Agent': _USER_AGENT})
    # try:
    #     page = urllib.request.urlopen(req)
    # except urllib.error.URLError as e:
    #     print(e.reason)

    return BeautifulSoup(response.text, features="lxml")


def get_columns(name, url):
    main_section = get_soup(name, url).find(
        name="main", id="mainShell").article
    divs = main_section.findAll("div", "col-sm-6")
    return divs


def child_is_pectoralis_minor_stretch(child):
    # Very specific exception, potentially generalizable
    temp = {}
    key = "stretch"
    links = child.findAll("a")
    temp[key] = links[0:4]
    return temp


def get_column_uls_array(child):
    temp_columns = child.find("ul")
    if temp_columns is None:
        return []

    columns_array = []
    columns_array.append(temp_columns)
    while (temp_columns.find_next_sibling("ul")):
        temp_columns = temp_columns.find_next_sibling("ul")
        columns_array.append(temp_columns)
    return columns_array


def get_key(href):
    # Checks to see if the string is either a weight exercise or a stretch
    if type_a in href:
        return re.search(type_a_search, href).group(1)
    elif type_b in href:
        return re.search(type_b_search, href).group(1)
    else:
        raise ValueError('Key Exception Error: not a valid link')


def iterate_column_uls(column_uls):
    temp = {}
    # makes an assumption that the first link found in a column represents the entier columns exercises
    # exception on pectoralis minor
    key = ""
    name = ""
    First = True

    for section in column_uls:
        if not isinstance(section, NavigableString) and section is not None:
            try:
                # .replace("(", "").replace(")", "")
                name = section.contents[0].strip().replace(
                    " ", "").lower()
                # HIGHLY SPECIFIC ERROR
                if (name == ""):
                    name = section.text.split()[0].lower()
                # POSSIBLE ERROR WITH INDENTING STRETCH TYPE
                if (name == "stretch" and section.contents[1].name == "i"):
                    # .replace("(", "").replace(")", "")
                    name += section.contents[1].text.strip().replace(
                        " ", "").lower()

            except:
                continue
            links = section.findAll("a")
            if First:
                # throws a key exception error
                key = get_key(links[0]['href'])
                # HIGHLY SPECIFIC ERROR FOR FIRST EXERCISE BEING LAT ON BICEPS PAGE
                if (key == "LatissimusDorsi" and name == "bodyweight" and get_key(links[3]['href']) == "Biceps"):
                    key = "Biceps"
                    name = "stretch"
                    links = links[3:8]
                First = False
            # print([name, links])
            array_dictionary_extend_if_no_exist(temp, name, links)
    return [key, temp]


packages = {}
# Iterates through the directory list, hard coded by muscle category
for name, url in zip(names, urls):
    divs = get_columns(name, url)

    for child in divs:
        # Check exceptions
        if child is None:
            continue
        # Retrieve all column uls even if separated by text
        column_uls_array = get_column_uls_array(child)

        # Specific Error with Pectoralis Minor Stretch
        if (child.text.strip().lower() ==
                "Stretch Doorway Chest Lying Shoulder Girdle Towel Shoulder Girdle Wall Shoulder Girdle Also see Doorway Chest Stretch for General Chest.Also see Broomstick Stretch for Supscapularis.".strip().lower()):
            try:
                column_zip = child_is_pectoralis_minor_stretch(child)
            except ValueError as err:
                print(err.args)
            # check if key exists
            # print(column_zip[1])
            array_dictionary_extend(packages, "PectoralisMinor", column_zip)
            continue

        # Go through each column UL
        for column_uls in column_uls_array:
            try:
                column_zip = iterate_column_uls(column_uls)
            except ValueError as err:
                print(err.args)
            # check if key exists
            # print(column_zip[1])
            array_dictionary_extend(packages, column_zip[0], column_zip[1])


# Organizes the packages based on rules and persists
packages.pop('')
packages.pop('Power')
hipeexternalrotator = packages.pop('HipExternalRotator')
array_dictionary_extend(packages, 'HipExternalRotators', hipeexternalrotator)
hipabductor = packages.pop('HipAbductor')
array_dictionary_extend(packages, 'HipAbductors', hipabductor)

organized = dict()
for muscle_group in muscle_groups:
    organized[muscle_group[0]] = dict()
    for muscle in muscle_group[1:]:
        array_dictionary_extend(
            organized[muscle_group[0]], muscle, packages.pop(muscle))


log = open('log.txt', 'w')
pprint.pprint(organized, log)

with open('dictionary.pk1', 'wb') as output:
    sys.setrecursionlimit(10000)
    pickle.dump(organized, output, -1)
