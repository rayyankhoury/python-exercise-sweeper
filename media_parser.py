import os
import sys
import re
import subprocess
import pickle
import urllib
import urllib.request
import requests
from bs4 import BeautifulSoup
from json_constants import URL, URL_WWW, FAKE_IMAGE, HEADERS

_LOGO_GIF_TEXT = "ExRx.net: Exercise Prescription on Internet"
_VIDEO_REGEX_STRING = "https://player.vimeo.com/video/(.*)?muted=1&autoplay=1"

# Can tweak these to start at different locations within the file directory
GROUP_INDEX_START = 5
MUSCLE_INDEX_START = 0
TYPE_INDEX_START = 0

with open(os.path.join('dictionary', 'dictionary.pk1'), 'rb') as file_input:
    sys.setrecursionlimit(10000)
    organized = pickle.load(file_input)


# URL Manipulations


def get_soup(exercise_type, muscle_class, exercise_id):
    """Retrieves the soup from the BeautifulSoup import

    Args:
        exercise_type (string): WeightExercise, Stretches or Plyometrics (possible??)
        muscle_class (string): The muscle class within the muscle group (e.g. Sternocleidomastoid)
        exercise_id (string): The shorthand version of the website name used on the website itself

    Returns:
        BeautifulSoup: soup of the website page
    """

    # URL Setup
    referrer_url = URL + exercise_type + "/" + muscle_class + "/" + exercise_id

    req = urllib.request.Request(referrer_url, headers=HEADERS)

    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as err:
        print(err.reason)

    return BeautifulSoup(page, "lxml")


def save_image(soup, path):
    """Saves the image persistently to storage at the path location

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page
        path (os.path): Path object of the location to store the image
    """

    image_blocks = soup.findAll(
        'img', {"class": "ccm-image-block"})
    if image_blocks is not None:
        for image in image_blocks:
            if _LOGO_GIF_TEXT in image.get('alt'):
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
                    URL, URL_WWW)
                if not "http" in image_link:
                    image_link = URL_WWW + image_link
                path = path + '.' + extension
                print(image_link)
                with open(path, "wb") as media_file:
                    response = requests.get(image_link)
                    if response.url == FAKE_IMAGE:
                        image_link = image_link.replace("www.", "")
                        response = requests.get(image_link)
                        if response.url == FAKE_IMAGE:
                            break
                    media_file.write(response.content)
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
                    URL, URL_WWW)
                if not "http" in image_link:
                    image_link = URL_WWW + image_link
                path = path + '.' + extension
                print(image_link)
                with open(path, "wb") as media_file:
                    media_file.write(requests.get(image_link).content)
                return

    file = open("error.log", "a")
    file.write("Image not found at: " + path + '\n')
    file.close()


def save_media(soup, path, referrer_url):
    """Finds whether the media on the page is a video or an image and saves this media to storage using priority for a video

    Args:
        soup (BeautifulSoup): the beautiful soup of the page
        path (os.path): The location to store the image or video
        referrer_url (string): The actual URL of the website, used with the Vimeo extractor to spoof the website in to thiking that it is being requested from here
    """

    # Finding video in soup
    result = re.search(_VIDEO_REGEX_STRING, soup.decode('utf-8'))
    # is not a video, saves an image instead
    if result is None:
        save_image(soup, path)
    # otherwise runs and saves an image
    else:
        video_id = ''.join([n for n in result.group(1) if n.isdigit()])
        result = subprocess.run(["youtube-dl", "-v", "https://player.vimeo.com/video/" + video_id,
                                 "--referer", referrer_url, "-o", path + '.%(ext)s'], capture_output=True, text=True, check=True)
        if "ERROR:" in result.stderr:
            file = open("error.log", "a")
            file.write("Video not found at: " + path + '\n')
            file.close()


def parse_media(exercise_type, muscle_class, exercise_id, path):
    """Takes in the information as dictated by the URL structure to generate the BeautifulSoup of the page
    and also generates the exact location to store the media file

    Args:
        exercise_type (string): Weight, stretch, plyometrics
        muscle_class (string): Actual muscle within the group
        exercise_id (string): The ID used on the website to identify the particular exercise
        path (os.path): the location on the storage where we store this file
    """
    print(exercise_type, muscle_class, exercise_id, path)
    soup = get_soup(exercise_type, muscle_class, exercise_id)
    path = os.path.join(path, exercise_id.replace(" ", ""))
    referrer_url = URL + exercise_type + "/" + muscle_class + "/" + exercise_id
    save_media(soup, path, referrer_url)


def parse(href, path):
    if not ("../../" in href or URL_WWW in href):
        raise ValueError("Unacceptable website input:" + href)

    cut = href.split("/")
    cut = cut[-3:]
    return parse_media(cut[0], cut[1], cut[2], path)


def write_to_file(group, muscle, mtype):
    hrefs = organized[group][muscle][mtype]
    path = os.path.join(
        'data', group, muscle, mtype)
    for href in hrefs:
        try:
            parse(href['href'], path)
        except ValueError as err:
            print(err.args)


muscle_group_keys = organized.keys()

for group_index, group_key in enumerate(muscle_group_keys):
    if group_index < GROUP_INDEX_START:
        continue
    # group_key = list(organized.keys())[0]
    muscle_keys = organized[group_key].keys()
    for muscle_index, muscle_key in enumerate(muscle_keys):
        print(muscle_key)
        if muscle_index < MUSCLE_INDEX_START and GROUP_INDEX_START == group_index:
            continue
        type_keys = organized[group_key][muscle_key].keys()
        for type_index, type_key in enumerate(type_keys):
            if type_index < TYPE_INDEX_START and muscle_index == MUSCLE_INDEX_START and GROUP_INDEX_START == group_index:
                continue
            if "stretch".lower() not in type_key.lower():
                continue
            print("Media Parsing: " + group_key +
                  "," + muscle_key + "," + type_key + "," + str(group_index) + str(muscle_index) + str(type_index))
            write_to_file(group_key, muscle_key, type_key)
