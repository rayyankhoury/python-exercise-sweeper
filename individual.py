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


# helper JSON function


def jsonify(name, value):
    return '"' + name.rstrip('\n') + '"' + ': ' + '"' + value.rstrip('\n') + '"' + ',\n'


# JSON definitions
_NAME = "name"
_UTILITY = "utility"
_MECHANICS = "mechanics"
_FORCE = "force"
_CLASSIFICATION = [_UTILITY, _MECHANICS, _FORCE]
_PREPARATION = "preparation"
_EXECUTION = "execution"
_COMMENTS = "comments"
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
_URL = "https://exrx.net/"
# exercise defintions
_exercise_full_name = ""
_url = ""


def get_soup(exercise_type, muscle_class, exercise_website_name):
    # URL Setup
    _url = _URL + exercise_type + "/" + muscle_class + "/" + exercise_website_name
    req = urllib.request.Request(_url, headers={'User-Agent': _USER_AGENT})
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)

    return BeautifulSoup(page, "lxml")


def open_file(soup):

    # Finds the name of the exercise
    name_div_class = "fruitful-page-title fruitfull-title-padding"
    name_div = soup.find('div', {"class": name_div_class})
    file_exercise_name = ""
    for i in name_div.findAll('h1'):
        file_exercise_name = jsonify(_NAME, i.text)
        exercise_full_name = i.text

    # File
    file = open('details.json', 'a')
    file.write('{')
    file.write(file_exercise_name)
    return file


def save_image(picture):
    # yes
    print(picture)


def save_media(soup):
    # Finding video in soup
    search_string = "https://player.vimeo.com/video/(.*)?muted=1&autoplay=1"
    result = re.search(search_string, soup.decode('utf-8'))
    # is not a video, saves an image instead
    if result is None:
        save_image(soup.find('picture'))
    # otherwise runs and saves an image
    else:
        video_id = ''.join([n for n in result.group(1) if n.isdigit()])
        subprocess.run(["youtube-dl", "-v", "https://player.vimeo.com/video/" + video_id,
                        "--referer", _url, "-o", _exercise_full_name.replace(" ", "") + '.%(ext)s'])


def write_classification(file, classification_table):
    # Finds the classification of the exercise
    links = (classification_table.findAll('tr'))
    for index, link in enumerate(links):
        write_to_file = jsonify(
            _CLASSIFICATION[index], link.findAll('td')[1].text)
        file.write(write_to_file)


def write_preparation_execution(file, paragraphs):
    # Finds the preparation and execution of the exercise
    for i, paragraph in enumerate(paragraphs):
        text = paragraph.text.lower().strip()
        if text == _PREPARATION:
            if (paragraphs[i + 1].text.lower().strip() != _EXECUTION):
                file.write(jsonify(_PREPARATION, paragraphs[i + 1].text))
        if text == _EXECUTION:
            if (paragraphs[i + 1].text.lower().strip() != None) and (text != _COMMENTS):
                file.write(jsonify(_EXECUTION, paragraphs[i + 1].text))


def write_comments(file, headers, right_div, left_div, paragraphs):
    # Finds the comments
    left_side_start = False
    right_side_start = False
    for header in headers:
        # Case 1 + 2, comments started on left side,
        if ("Comments" in header):
            left_side_start = True
            right_side_start = False
        else:
            left_side_start = False
            # Case 3: started on the right side
            right_side_start = True
    # Case 1: finished on left side
    left_side_finished = True
    # Case 2: finished on right side
    if (right_div.findChildren()[0].name == "p"):
        left_side_finished = False

    # Case 1: finished on left side
    if (left_side_start and left_side_finished):
        write_to_file = jsonify(_COMMENTS, paragraphs[len(paragraphs)-1].text)
        file.write(write_to_file)

    # Case 2: finished on right side
    if (left_side_start and not left_side_finished):
        temp_string = paragraphs[len(paragraphs)-1].text + \
            ' ' + right_div.find('p').text
        write_to_file = jsonify(_COMMENTS, temp_string)
        file.write(write_to_file)

    # Case 3: comments right side
    if (right_side_start):
        write_to_file = jsonify(_COMMENTS, right_div.find('p').text)
        file.write(write_to_file)


def extract_muscles(current_muscles):
    muscles = set()
    for muscle in current_muscles:
        # if the muscle has a link inside of it
        muscle_link = muscle.find('a')
        if muscle_link is not None:
            if muscle_link.has_attr('href'):
                muscles.add(muscle_link.get("href").rsplit('/', 1)[-1].lower())
            else:
                muscles.add(muscle.text)
        # otherwise just extract the name as is
        else:
            muscles.add(muscle.text)
    # create the string and return it
    muscle_string = ""
    for unique_muscle in muscles:
        muscle_string += unique_muscle + ", "

    return muscle_string[: -2]


def write_muscle_groups(file, muscle_section):
    write_to_file = ""
    category = ""
    muscles = ""
    while muscle_section.next_sibling != None:
        muscle_section = muscle_section.next_sibling
        if (muscle_section.name == "p"):
            category = muscle_section.text.rstrip('\n').lower()
        if (muscle_section.name == "ul"):
            muscles = extract_muscles(muscle_section.findAll('li'))
            write_to_file = jsonify(category, muscles) + write_to_file
    file.write(write_to_file[: -2])


def close_file(file):
    file.write('},')
    file.close()


def parse_webpage(exercise_type, muscle_class, exercise_website_name, overall_muscle_group):

    soup = get_soup(exercise_type, muscle_class, exercise_website_name)
    left_div = soup.findAll('div', {"class": "col-sm-6"})[0]
    right_div = soup.findAll('div', {"class": "col-sm-6"})[1]
    classification_table = left_div.find('table')
    paragraphs = left_div.findAll('p')
    headers = left_div.findAll('h2')
    muscle_section_start = right_div.find(name="h2", text="Muscles")
    muscle_names = right_div.findAll('ul')

    file = open_file(soup)

    # save_media(soup)

    if classification_table is not None and exercise_type == "WeightExercises":
        write_classification(file, classification_table)

    write_preparation_execution(file, paragraphs)

    write_comments(file, headers, right_div, left_div, paragraphs)

    write_muscle_groups(file, muscle_section_start)

    close_file(file)
