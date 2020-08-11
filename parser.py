import os
import sys
import individual
import urllib.request
from bs4 import BeautifulSoup


def createSubdirectory(name):
    subdirectory = name
    if not os.path.exists(name):
        os.makedirs(name)


def createSubdirectoryStructure(current, weightExercises, stretches):
    createSubdirectory(current)
    createSubdirectory(weightExercises)
    createSubdirectory(stretches)
    file = open(os.path.join(weightExercises, 'details.json'), 'w')
    file = open(os.path.join(stretches, 'details.json'), 'w')


neck = "neck"
neckURL = "https://www.exrx.net/Lists/ExList/NeckWt"
shoulders = "shoulders"
shouldersURL = "https://www.exrx.net/Lists/ExList/ShouldWt"
upperarms = "upperarms"
upperarmsURL = "https://www.exrx.net/Lists/ExList/ArmWt"
forearms = "forearms"
forearmsURL = "https://www.exrx.net/Lists/ExList/ForeArmWt"
back = "back"
backURL = "https://www.exrx.net/Lists/ExList/BackWt"
chest = "chest"
chestURL = "https://www.exrx.net/Lists/ExList/ChestWt"
waist = "waist"
waistURL = "https://www.exrx.net/Lists/ExList/WaistWt"
hips = "hips"
hipsURL = "https://www.exrx.net/Lists/ExList/HipsWt"
thighs = "thighs"
thighsURL = "https://www.exrx.net/Lists/ExList/ThighWt"
calves = "calves"
calvesURL = "https://www.exrx.net/Lists/ExList/CalfWt"

groupNames = [neck, shoulders, upperarms, forearms,
              back, chest, waist, hips, thighs, calves]
groupURLS = [neckURL, shouldersURL, upperarmsURL, forearmsURL,
             backURL, chestURL, waistURL, hipsURL, thighsURL, calvesURL]

for name, url in zip(groupNames, groupURLS):

    # subdirectory for muscle group
    createSubdirectory(name)

    req = urllib.request.Request(url, headers={
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"})
    try:
        page = urllib.request.urlopen(req)
    except urllib.error.URLError as e:
        print(e.reason)
    soup = BeautifulSoup(page, "lxml")

    links = (soup.findAll('a'))
    currentSubdirectory = ""
    weightExercisesSubdirectory = ""
    stretchesSubdirectory = ""
    currentMuscle = ""
    first = False
    for link in links:
        if link.has_attr('href'):
            # is the title of the muscle
            if "Muscles" in link.get("href"):
                currentMuscleBoolean = True

            # first entry
            if "WeightExercises" in link.get("href") and first:
                first = False
                result = re.search(
    #     'https://player.vimeo.com/video/(.*)?muted=1&autoplay=1', soup.decode('utf-8'))
                currentMuscle = link.text.lower().replace(" ", "")
                currentSubdirectory = os.path.join(
                    name, currentMuscle)
                weightExercisesSubdirectory = os.path.join(
                    currentSubdirectory, "weightexercises")
                stretchesSubdirectory = os.path.join(
                    currentSubdirectory, "stretches")
                createSubdirectoryStructure(
                    currentSubdirectory, weightExercisesSubdirectory, stretchesSubdirectory)
                print(currentSubdirectory)

            # second and follow up

            # # is an exercise
            # if "WeightExercises" in link.get("href"):
            #     createSubdirectory(os.path.join(
            #         name, link.text.lower().replace(" ", "")))

            # # is a stretch
            # if "Stretches" in link.get("href"):
            #     createSubdirectory(os.path.join(
            #         name, link.text.lower().replace(" ", "")))

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
