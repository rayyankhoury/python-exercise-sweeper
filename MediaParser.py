import ExerciseDetailsParserJSON
import os
import sys
import pickle
import pprint
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
import pprint
import time

# JSON usage
_ID = "id"
_EXERCISE_TYPE = "exercisetype"
_MUSCLE_CLASS = "muscleclass"
_EXERCISE_ID = "exerciseid"

# Website Inputs
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
_URL = "https://exrx.net/"
_EXERCISE_NAME_DIV = "fruitful-page-title fruitfull-title-padding"
_COLUMN_DIV = "col-sm-6"


with open(os.path.join('dictionary', 'dictionary.pk1'), 'rb') as input:
    sys.setrecursionlimit(10000)
    organized = pickle.load(input)


# URL Manipulations


def get_soup(exercise_type, muscle_class, exercise_id):
    '''
    Retrieves the soup from the BeautifulSoup import

    exercise_type: WeightExercise or Stretches

    muscle_class: Muscle class within muscle group (e.g. Sternocleidomastoid)

    exercise_id: shorthand version of website name used on website
    '''

    # URL Setup
    referrer_url = _URL + exercise_type + "/" + muscle_class + "/" + exercise_id

    req = urllib.request.Request(
        referrer_url,
        headers={'User-Agent': _USER_AGENT})

    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)

    return BeautifulSoup(page, "lxml")


def save_image(soup, path):

    image_blocks = soup.findAll(
        'img', {"class": "ccm-image-block"})
    if image_blocks != None:
        for image in image_blocks:
            if "ExRx.net: Exercise Prescription on Internet" in image.get('alt'):
                continue
            image_link = image.get('src')
            print(image_link)
            if "/application/files/" not in image_link:
                image_link = image.get('data-ezsrc')
                print(image_link)
            if "/application/files/" in image_link:
                extension = image_link.split('.')[-1:][0]
                # Can access the file directly, otherwise need to access through the thumbnails link
                if extension != 'gif' and '/application/files/cache/thumbnails/' not in image_link:
                    image_link = image_link.replace("/application/files/",
                                                    "/application/files/thumbnails/small/")
                image_link = image_link.replace(
                    "https://exrx.net/", "https://www.exrx.net/")
                if not "http" in image_link:
                    image_link = "https://www.exrx.net" + image_link
                path = path + '.' + extension
                print(image_link)
                with open(path, "wb") as f:
                    response = requests.get(image_link)
                    if (response.url == "https://www.solidbackgrounds.com/images/2560x1440/2560x1440-black-solid-color-background.jpg"):
                        image_link = image_link.replace("www.", "")
                        response = requests.get(image_link)
                        if (response.url == "https://www.solidbackgrounds.com/images/2560x1440/2560x1440-black-solid-color-background.jpg"):
                            break
                    f.write(response.content)
                return
    # yes
    image_block = soup.find('picture')
    if image_block is not None:
        if image_block.parent.get('data-redactor-inserted-image') is not None:
            image = image_block.find('img')
            image_link = image.get('src')
            if "/application/files/" in image_link:
                extension = image_link.split('.')[-1:][0]
                # Can access the file directly, otherwise need to access through the thumbnails link
                if extension != 'gif' and '/application/files/thumbnails/' in image_link:
                    image_link = image_link.replace("/application/files/thumbnails/",
                                                    "/application/files/cache/thumbnails/")
                elif extension != 'gif' and '/application/files/cache/thumbnails/' not in image_link:
                    image_link = image_link.replace("/application/files/",
                                                    "/application/files/thumbnails/small/")
                image_link = image_link.replace(
                    "https://exrx.net/", "https://www.exrx.net/")
                if not "http" in image_link:
                    image_link = "https://www.exrx.net" + image_link
                path = path + '.' + extension
                print(image_link)
                with open(path, "wb") as f:
                    f.write(requests.get(image_link).content)
                return

    file = open("error.log", "a")
    file.write("Image not found at: " + path + '\n')
    file.close()


def save_media(soup, path, referrer_url):
    # Finding video in soup
    search_string = "https://player.vimeo.com/video/(.*)?muted=1&autoplay=1"
    result = re.search(search_string, soup.decode('utf-8'))
    # is not a video, saves an image instead
    if result is None:
        save_image(soup, path)
    # otherwise runs and saves an image
    else:
        video_id = ''.join([n for n in result.group(1) if n.isdigit()])
        result = subprocess.run(["youtube-dl", "-v", "https://player.vimeo.com/video/" + video_id,
                                 "--referer", referrer_url, "-o", path + '.%(ext)s'], capture_output=True, text=True)
        if "ERROR:" in result.stderr:
            file = open("error.log", "a")
            file.write("Video not found at: " + path + '\n')
            file.close()


def parse_media(exercise_type, muscle_class, exercise_id, path):
    print(exercise_type, muscle_class, exercise_id, path)
    soup = get_soup(exercise_type, muscle_class, exercise_id)
    path = os.path.join(path, exercise_id.replace(" ", ""))
    referrer_url = _URL + exercise_type + "/" + muscle_class + "/" + exercise_id
    save_media(soup, path, referrer_url)


def parse(href, path):
    if not ("../../" in href or "https://www.exrx.net/" in href):
        raise ValueError("Unacceptable website input:" + href)

    cut = href.split("/")
    cut = cut[-3:]
    return parse_media(cut[0], cut[1], cut[2], path)


def write_to_file(group_key, muscle_key, type_key):
    hrefs = organized[group_key][muscle_key][type_key]
    path = os.path.join(
        'data', group_key, muscle_key, type_key)
    for href in hrefs:
        try:
            parse(href['href'], path)
        except ValueError as err:
            print(err.args)


muscle_group_keys = organized.keys()

group_index_start = 0
muscle_index_start = 0
type_index_start = 0

# 5 0 13 failuire

# 5 3 7 failure

# 6 0 9 failure

# 6 1 8 failure

for group_index, group_key in enumerate(muscle_group_keys):
    if group_index < group_index_start:
        continue
    # group_key = list(organized.keys())[0]
    muscle_keys = organized[group_key].keys()
    for muscle_index, muscle_key in enumerate(muscle_keys):
        print(muscle_key)
        if muscle_index < muscle_index_start and group_index_start == group_index:
            continue
        type_keys = organized[group_key][muscle_key].keys()
        for type_index, type_key in enumerate(type_keys):
            if type_index < type_index_start and muscle_index == muscle_index_start and group_index_start == group_index:
                continue
            if "stretch".lower() not in type_key.lower():
                continue
            print("Media Parsing: " + group_key +
                  "," + muscle_key + "," + type_key + "," + str(group_index) + str(muscle_index) + str(type_index))
            write_to_file(group_key, muscle_key, type_key)
