"""Finds the video or image related to a given exercise on a page

    Raises:
        ValueError: Couldn't find the image or the video, writes the issue to a file

    """

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
_VIMEO_URL = "https://player.vimeo.com/video/"

_FORMAT_X = "/application/files/"
_FORMAT_Y = "/application/files/cache/thumbnails/"
_FORMAT_Z = "/application/files/thumbnails/small/"
_FORMAT_A = "/application/files/thumbnails"

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
    referrer_url = f'{URL}{exercise_type}/{muscle_class}/{exercise_id}'

    req = urllib.request.Request(referrer_url, headers=HEADERS)

    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as err:
        print(err.reason)

    return BeautifulSoup(page, "lxml")


def image_ccm_link_parser(image):
    """Complicated Parser

    Args:
        image (BeautifulSoup Tab): the image tab

    Returns:
        string: the link that is found as the final image link
    """
    image_link = image.get('src')

    if _FORMAT_X not in image_link:
        image_link = image.get('data-ezsrc')

    if _FORMAT_X in image_link:
        extension = image_link.split('.')[-1:][0]
        # Can access the file directly, otherwise need to access through the thumbnails link
        if extension != 'gif' and _FORMAT_Y not in image_link:
            image_link = image_link.replace(_FORMAT_X, _FORMAT_Z)
        image_link = image_link.replace(
            URL, URL_WWW)
        if not "http" in image_link:
            image_link = f"{URL_WWW}{image_link}"
    return image_link


def image_ccm(path, image_blocks):
    """Called if the tab found on the page was a <img> with class ccm-image-block

    Args:
        path (os.path): the location to store the image on the harddisk
        image_blocks (BeautifulSoup Tabs): blocks of images found on the webpage
    """
    for image in image_blocks:
        # Image found is the logo image, continue loop
        if _LOGO_GIF_TEXT in image.get('alt'):
            continue
        image_link = image_ccm_link_parser(image)
        extension = image_link.split('.')[-1:][0]
        path = f"{path}.{extension}"
        with open(path, "wb") as media_file:
            response = requests.get(image_link)
            if response.url == FAKE_IMAGE:
                image_link = image_link.replace("www.", "")
                response = requests.get(image_link)
                if response.url == FAKE_IMAGE:
                    break
            media_file.write(response.content)


def image_picture(path, image_block):
    """Called if the tab found on the page was a <picture>

    Args:
        path (os.path): the location to store the image on the harddisk
        image_block (BeautifulSoup Tab): single tab of <picture> on webpage
    """

    if image_block.parent.get('data-redactor-inserted-image') is not None:
        image = image_block.find('img')
        image_link = image.get('src')
        if _FORMAT_X in image_link:
            extension = image_link.split('.')[-1:][0]
            # Can access the file directly, otherwise need to access through the thumbnails link
            if extension != 'gif' and _FORMAT_A in image_link:
                image_link = image_link.replace(_FORMAT_A, _FORMAT_Y)
            elif extension != 'gif' and _FORMAT_Y not in image_link:
                image_link = image_link.replace(_FORMAT_X, _FORMAT_Z)
            image_link = image_link.replace(URL, URL_WWW)
            if not "http" in image_link:
                image_link = f"{URL_WWW}{image_link}"
            path = f"{path}.{extension}"
            with open(path, "wb") as media_file:
                media_file.write(requests.get(image_link).content)


def save_image(soup, path):
    """Saves the image persistently to storage at the path location

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the page
        path (os.path): Path object of the location to store the image
    """

    image_blocks = soup.findAll(
        'img', {"class": "ccm-image-block"})

    # Found the class ccm-image-block
    if image_blocks is not None:
        image_ccm(path, image_blocks)
    else:
        # Found an instance of picture on the webpage
        image_block = soup.find('picture')
        if image_block is not None:
            image_picture(path, image_block)
        else:
            with open("error.log", "a") as file:
                file.write(f"Image not found at: {path}\n")


def save_media(soup, path, referrer_url):
    """Finds whether the media on the page is a video or an image
        and saves this media to storage using priority for a video

    Args:
        soup (BeautifulSoup): the beautiful soup of the page
        path (os.path): The location to store the image or video
        referrer_url (string): The actual URL of the website,
            used with the Vimeo extractor to spoof the website in to
            thiking that it is being requested from here
    """

    # Finding video in soup
    result = re.search(_VIDEO_REGEX_STRING, soup.decode('utf-8'))
    # is not a video, saves an image instead
    if result is None:
        save_image(soup, path)
    # otherwise runs and saves an image
    else:
        video_id = ''.join([n for n in result.group(1) if n.isdigit()])
        result = subprocess.run(["youtube-dl", "-v", f"{_VIMEO_URL}{video_id}",
                                 "--referer", referrer_url, "-o", f"{path}.%(ext)s"],
                                capture_output=True, text=True, check=True)
        if "ERROR:" in result.stderr:
            with open("error.log", "a") as file:
                file.write(f"Video not found at: {path}\n")


def parse(href, path):
    """Takes in the information as dictated by the URL structure
        to generate the BeautifulSoup of the page
        and also generates the exact location to store the media file

    Args:
        href (string): The URL fo the exercise
        path (os.path): the location on the storage where we store this file
    """

    if not ("../../" in href or URL_WWW in href):
        raise ValueError("Unacceptable website input:" + href)

    exercise_type, muscle_class, exercise_id = href.split("/")[-3:]

    print(exercise_type, muscle_class, exercise_id, path)
    soup = get_soup(exercise_type, muscle_class, exercise_id)
    path = os.path.join(path, exercise_id.replace(" ", ""))
    referrer_url = f'{URL}{exercise_type}/{muscle_class}/{exercise_id}'
    save_media(soup, path, referrer_url)


def write_to_file(wgroup_key, wmuscle_key, wtype_key):
    """Finds the hrefs in the dictionary using provided keys

    Args:
        wgroup_key (string): The muscle group name
        wmuscle_key (string): The individual muscle name
        wtype_key (string): The type of exercise name
    """
    hrefs = organized[wgroup_key][wmuscle_key][wtype_key]
    path = os.path.join(
        'data', wgroup_key, wmuscle_key, wtype_key)
    for href in hrefs:
        try:
            parse(href['href'], path)
        except ValueError as err:
            print(err.args)


for group_key, group_dict in organized.items():
    for muscle_key, muscle_dict in group_dict.items():
        for type_key in muscle_dict.items():
            keystring = f"{group_key}, {muscle_key}, {type_key}"
            print(f"Media Parsing: {keystring}")
            write_to_file(group_key, muscle_key, type_key)
