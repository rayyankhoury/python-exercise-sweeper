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


value = input('''
This is dangerous and will overwrite JSON details files.
To overwrite type yes.
To create directory structure without overwriting type dir.
To exit type no\n''')

overwrite = False

if value == 'no':
    sys.exit("Exiting")
elif value == 'dir':
    print("Creating directory structure")
elif value == 'yes':
    print('Overwriting')
    overwrite = True
else:
    sys.exit("Wrong value entered, exiting")


def createSubdirectory(name):
    subdirectory = name
    if not os.path.exists(name):
        os.makedirs(name)


with open(os.path.join('dictionary', 'dictionary.pk1'), 'rb') as input:
    sys.setrecursionlimit(10000)
    organized = pickle.load(input)

# Create the directory structure
createSubdirectory("data")
for key in organized.keys():
    createSubdirectory(os.path.join("data", key))
    for muscle in organized[key].keys():
        createSubdirectory(os.path.join("data", key, muscle))
        for exercisetype in organized[key][muscle].keys():
            createSubdirectory(os.path.join("data", key, muscle, exercisetype))
            if overwrite:
                open(os.path.join("data", key, muscle,
                                  exercisetype, "details.json"), "w+")
