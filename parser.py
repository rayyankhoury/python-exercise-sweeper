import os
import sys
import individual
import urllib.request
from bs4 import BeautifulSoup

neckURL = "https://www.exrx.net/Lists/ExList/NeckWt"
neck = "neck"
shouldersURL = "https://www.exrx.net/Lists/ExList/ShouldWt"
shoulders = "shoulders"

groupNames = [neck, shoulders]
groupURLS = [neckURL, shouldersURL]

for name, url in zip(groupNames, groupURLS):
    

    req = urllib.request.Request(url, headers={
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"})
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
    soup = BeautifulSoup(page, "lxml")

    links = (soup.findAll('a'))
    # links = soup.findAll(
    #     'div', {"class": "col-sm-12"})
    for link in links:
        if link.has_attr('name'):
            print(link)

# file = open('details.json', 'w')
# file.write('{"exercise":[')
# file.close()

# individual.ParseWebpage("WeightExercises", "BackGeneral",
#                         "BWSupineRow", exercise)
# individual.ParseWebpage("WeightExercises", "BackGeneral", "BBBentOverRow")
# individual.ParseWebpage(
#     "WeightExercises", "BackGeneral", "CamberedBarLyingRow")
# individual.ParseWebpage("WeightExercises", "BackGeneral", "CBOneArmRow")
# individual.ParseWebpage("WeightExercises", "BackGeneral",
#                         "CBOneArmTwistingHighRow")
# file = open('details.json', 'a')
# file.write(']}')
# file.close()
