import os
import sys
import urllib
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
#from requests_html import HTMLSession
import subprocess

#helper JSON function
def JSONify (name,value):
    return '"' + name + '"' + ': ' + '"' + value + '"' + ',\n'

#JSON definitions
NAME = "name"
UTILITY = "utility"
MECHANICS = "mechanics"
FORCE = "force"
PREPARATION = "preparation"
EXECUTION = "execution"
COMMENTS = "comments"

# exercise defintions
exerciseWebsiteName = "ContraLateralSuperman"
exerciseFullName = ""

# URL Setup
url = "https://exrx.net/WeightExercises/ErectorSpinae/" + exerciseWebsiteName
req = urllib.request.Request(url, headers={
                             'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"})
try:
    page = urllib.request.urlopen(req)
except urllib.error.URLError as e:
    print(e.reason)
soup = BeautifulSoup(page, "lxml")

# Finds the name of the exercise
nameDIV = soup.find('div', {"class": "fruitful-page-title fruitfull-title-padding"})
fileExerciseName = ""
for i in nameDIV.findAll('h1'):
    fileExerciseName = JSONify (NAME,i.text)
    exerciseFullName = i.text

# File
subdirectory = exerciseFullName
if not os.path.exists(exerciseFullName):
    os.makedirs(exerciseFullName)
file = open(os.path.join(subdirectory, 'details.json'), 'w')
file.write(fileExerciseName)

##############################
subprocess.run(["youtube-dl", "-v", "https://player.vimeo.com/video/156692562","--referer", url, "-o", os.path.join(subdirectory, 'video.%(ext)s')])
# session = HTMLSession()
# r = session.get(url)
# r.html.render()

# headers = {
# 'Host': 'player.vimeo.com',
# 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
# 'Accept-Language': 'en-US,en;q=0.5',
# 'Accept-Encoding': 'gzip, deflate, br',
# 'DNT': '1',
# 'Connection': 'keep-alive',
# 'Referer': 'https://exrx.net/',
# 'Upgrade-Insecure-Requests': '1',
# 'Pragma': 'no-cache',
# 'Cache-Control': 'no-cache'}

# videoURL = 'https://player.vimeo.com/video/157104877?muted=1&autoplay=1&loop=1&title=0&byline=0&portrait=0'
# r = requests.get(videoURL, headers)
# print(r.status_code)
#open("video.mp4", 'wb').write(r.content)


#videoreq = urllib.request.Request(videoURL, headers)
# open("video.mp4", 'wb').write(videoreq..data)

# trying to get the mp4
# x = urllib.request.Request('GET /api/video/b10412543b7667a107e178795cd5bc0c/10226 HTTP/1.1', headers={
#    'Host': "exrx.glorb.com",
#    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0",
#    'Accept': "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
#    'Accept-Language': "en-US,en;q=0.5",
#    'Range': "bytes=0-",
#    'DNT': "1",
#    'Connection': "keep-alive",
#    'Referer': "https://exrx.net/WeightExercises/ErectorSpinae/LVStraightLegDeadlift"})


################################

leftDiv = soup.findAll('div', {"class": "col-sm-6"})[0]
rightDiv = soup.findAll('div', {"class": "col-sm-6"})[1]

# Finds the classification of the exercise
classification = [UTILITY, MECHANICS, FORCE]
table = leftDiv.find('table')
links = (table.findAll('tr'))
for index, link in enumerate(links):
    writeToFile = JSONify(classification[index], link.findAll('td')[1].text)
    file.write(writeToFile)

# Finds the preparation and execution of the exercise
paragraphs = (leftDiv.findAll('p'))
if (len(paragraphs) < 4):
    file.write("PARSE ERROR FOR EXERCISE PREPARATION" + '\n')
else:
    writeToFile1 = JSONify(PREPARATION, paragraphs[1].text)
    writeToFile2 = JSONify(EXECUTION, paragraphs[3].text)
    file.write(writeToFile1)
    file.write(writeToFile2)

# Finds the comments
headers = leftDiv.findAll('h2')
leftSideStart = False
rightSideStart = False
for header in headers:
    # Case 1 + 2, comments started on left side,
    if ("Comments" in header):
        leftSideStart = True
        rightSideStart = False
    else:
        leftSideStart = False
        # Case 3: started on the right side
        rightSideStart = True
# Case 1: finished on left side
leftSideFinished = True
# Case 2: finished on right side
if (rightDiv.findChildren()[0].name == "p"):
    leftSideFinished = False

# Case 1: finished on left side
if (leftSideStart and leftSideFinished):
    writeToFile = JSONify(COMMENTS , paragraphs[len(paragraphs)-1].text)
    file.write(writeToFile)

# Case 2: finished on right side
if (leftSideStart and not leftSideFinished):
    tempString = paragraphs[len(paragraphs)-1].text + ' ' + rightDiv.find('p').text
    writeToFile = JSONify(COMMENTS , tempString)
    file.write(writeToFile)

# Case 3: comments right side
if (rightSideStart):
    writeToFile = JSONify(COMMENTS , rightDiv.find('p').text)
    file.write(writeToFile)

# Efficient Parser
muscleGroupNames = rightDiv.findAll('p')
muscleNames = rightDiv.findAll('ul')
writeToFile = ""
first = True
for i in range(len(muscleGroupNames)-1, 0, -1):
    muscleGroupName = muscleGroupNames[i].text.rstrip('\n').lower()
    currentMuscles = muscleNames[i-1].findAll('li')
    muscles = ""
    for muscle in currentMuscles:
        muscles += muscle.text + ", "
    muscles = muscles[:-2]
    if first:
        first = False
        writeToFile = JSONify(muscleGroupName, muscles)[:-2]
    else:
        writeToFile = JSONify(muscleGroupName, muscles) + writeToFile

# Writes the string to the file and closes the file
file.write(writeToFile)
file.close()


