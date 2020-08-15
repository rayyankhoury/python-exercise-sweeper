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


# helper JSON function


def jsonify(key, value):
    return '"' + key.rstrip('\n') + '"' + ': ' + '"' + value.rstrip('\n') + '"' + ',\n'


# JSON definitions
_INDEX = "id"
_EXERCISE_TYPE = "exercisetype"
_MUSCLE_CLASS = "muscleclass"
_EXERCISE_ID = "exerciseid"
_NAME = "name"
_UTILITY = "utility"
_MECHANICS = "mechanics"
_FORCE = "force"
_CLASSIFICATION = [_UTILITY, _MECHANICS, _FORCE]
_PREPARATION = "preparation"
_EXECUTION = "execution"
_COMMENTS = "comments"
# Website Inputs
_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
_URL = "https://exrx.net/"
_EXERCISE_NAME_DIV = "fruitful-page-title fruitfull-title-padding"
_COLUMN_DIV = "col-sm-6"
# Exercise definitions
_exercise_full_name = ""
_url = ""
_exercise_id = ""


# JSON File Manipulation definitions

def start_json(exercise_type, muscle_class, exercise_id, index):
    'Returns opening json tag with index and the url details'
    exercise_type_json = jsonify(_EXERCISE_TYPE, exercise_type)
    muscle_class_json = jsonify(_MUSCLE_CLASS, muscle_class)
    exercise_id_json = jsonify(
        _EXERCISE_ID, exercise_id)
    index_json = jsonify(_INDEX, str(index))
    json = index_json + exercise_id_json + exercise_type_json + muscle_class_json
    return '{' + json


def name_as_json(name_div):
    # Finds the name of the exercise
    write_to_file = ''
    for i in name_div.findAll('h1'):
        write_to_file = jsonify(_NAME, i.text)
        _exercise_full_name = i.text
    return write_to_file


# URL Manipulations


def get_soup(exercise_type, muscle_class, exercise_id):
    '''
    Retrieves the soup from the BeautifulSoup import

    exercise_type: WeightExercise or Stretches

    muscle_class: Muscle class within muscle group (e.g. Sternocleidomastoid)

    exercise_id: shorthand version of website name used on website
    '''

    # URL Setup
    _url = _URL + exercise_type + "/" + muscle_class + "/" + exercise_id

    req = urllib.request.Request(
        _url,
        headers={'User-Agent': _USER_AGENT})
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)

    return BeautifulSoup(page, "lxml")


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


def classification_table_as_json(exercise_type, classification_table):
    "Returns a Value error if the table does not exist"
    # Stretches don't have a classification table
    if exercise_type != "WeightExercises":
        return ""
    if classification_table is None:
        raise ValueError('No Classification Table on page ' +
                         _exercise_id)

    # Finds the classification of the exercise
    links = (classification_table.findAll('tr'))
    write_to_file = ""
    for index, link in enumerate(links):
        write_to_file += jsonify(
            _CLASSIFICATION[index], link.findAll('td')[1].text)
    return write_to_file


def preparation_execution_as_json(paragraphs):
    write_to_file = ""
    # Finds the preparation and execution of the exercise
    for i, paragraph in enumerate(paragraphs):
        text = paragraph.text.lower().strip()
        if text == _PREPARATION:
            if (paragraphs[i + 1].text.lower().strip() != _EXECUTION):
                write_to_file += (jsonify(_PREPARATION,
                                          paragraphs[i + 1].text.replace('\xa0',
                                                                         ' ').replace('\n', '')))
        if text == _EXECUTION:
            if (paragraphs[i + 1].text.lower().strip() != None) and (text != _COMMENTS):
                write_to_file += jsonify(_EXECUTION, paragraphs[i + 1].text.replace('\xa0',
                                                                                    ' ').replace('\n', ''))
    return write_to_file


def find_section(div_list, name, text):
    for div in div_list:
        section = div.find(name=name, string=re.compile(text))
        if section is not None:
            return section
    # Strange error check
    for div in div_list:
        section = div.find(string=re.compile(text))
        if section is None:
            continue
        parent = section.parent
        if parent.name == name:
            return parent
    raise ValueError("No <" + name + '>"' + text +
                     '" on page ' + _exercise_id)


def comments_as_json(div_list):
    comments = ""
    try:
        comments_section_h2 = find_section(
            div_list, "h2", "Comments")
        muscles_section_h2 = find_section(
            div_list, "h2", "Muscles")
    except ValueError as err:
        print(err.args)
        return comments

    temp = comments_section_h2
    found = False
    second_loop_first_iteration = False
    while not found:
        while temp.next_sibling != None:
            temp = temp.next_sibling
            if second_loop_first_iteration:
                temp = temp.previous_sibling
                second_loop_first_iteration = False
            if temp == muscles_section_h2:
                found = True
                break
            try:
                comments += temp.text.replace('\xa0',
                                              ' ').replace('\n', '') + ' '
            except:
                continue
        second_loop_first_iteration = True
        temp = div_list[1].findChildren()[0]
    return jsonify(_COMMENTS, comments[:-1])


def muscle_li_list_to_string(muscles_li_list):
    # Make sure the muslces being added are unique as far as the actual referencing of muscles is concerned
    # (e.g. two specific references to different parts of a single muscle)
    muscles = set()
    for muscle in muscles_li_list:
        # If the muscle has a link inside of it, used to get the reference name used consistently on website and to bypass spelling errors
        muscle_link = muscle.find('a')
        if muscle_link is not None:
            if muscle_link.has_attr('href'):
                muscles.add(muscle_link.get("href").rsplit('/', 1)[-1].lower())
            # Otherwise just extract the name as is
            else:
                muscles.add(muscle.text)
        else:
            muscles.add(muscle.text)
    # Create the string and return it
    muscle_string = ""
    for unique_muscle in muscles:
        muscle_string += unique_muscle + ", "

    # Removes the comma from the final string
    return muscle_string[: -2]


def muscle_section_as_json(muscle_section):
    "Muscle h2 reference is the reference to the h2 heading of the muscle sub section on the page"
    write_to_file = ""
    category = ""
    muscles_string = ""
    # Starts at n-1, which in this case is the muscle_h2 header
    while muscle_section.next_sibling != None:
        muscle_section = muscle_section.next_sibling
        # Muscle Category for this particular exercise
        if (muscle_section.name == "p"):
            category = muscle_section.text.rstrip('\n').lower()
        # Actual muscle referenced within this category
        if (muscle_section.name == "ul"):
            muscles_li_list = muscle_section.findAll('li')
            muscles_string = muscle_li_list_to_string(muscles_li_list)
            write_to_file = jsonify(category, muscles_string) + write_to_file
    # Removes new line and comma from last element
    return write_to_file[: -2]


def parse_webpage(exercise_type, muscle_class, exercise_id, index):

    json = start_json(exercise_type, muscle_class,
                      exercise_id, index)
    _exercise_id = exercise_id

    soup = get_soup(exercise_type, muscle_class, exercise_id)
    name_div = soup.find('div', {"class": _EXERCISE_NAME_DIV})
    div_list = soup.findAll('div', {"class": _COLUMN_DIV})
    left_column_div = div_list[0]
    right_column_div = div_list[1]
    classification_table = left_column_div.find('table')
    left_column_paragraphs = left_column_div.findAll('p')
    muscle_section_h2 = find_section(div_list, "h2", "Muscles")
    # muscle_names = right_div.findAll('ul')

    json += name_as_json(name_div)

    # save_media(soup)

    # Retrieves the classification table from the weight exercise page and prints it to the file
    try:
        classification_table_json = classification_table_as_json(
            exercise_type, classification_table)
        json += classification_table_json
    except ValueError as err:
        print(err.args)

    # Writes the preparation and execution to the file
    preparation_execution_json = preparation_execution_as_json(
        left_column_paragraphs)
    json += preparation_execution_json

    comments_json = comments_as_json(div_list)
    json += comments_json

    # Writes the muscle section as JSON to the file
    muscle_json = muscle_section_as_json(muscle_section_h2)
    json += muscle_json

    return json + '}'


def parse(href, index):
    if not ("../../" in href or "https://www.exrx.net/" in href):
        raise ValueError("Unacceptable website input:" + href)

    cut = href.split("/")
    cut = cut[-3:]
    return parse_webpage(cut[0], cut[1], cut[2], index)
