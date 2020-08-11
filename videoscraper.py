import urllib
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from requests_html import HTMLSession

# URL Setup
URL = 'https://exrx.net/WeightExercises/ErectorSpinae/CBStraightLegDeadlift'
session = HTMLSession()
r = session.get(URL, headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0"})
r.html.render()
print(r.headers)
print(r.content)


https: // player.vimeo.com/video/

?muted = 1

# subprocess.run(["youtube-dl", "-v", "https://player.vimeo.com/video/" + videoID,
#                "--referer", url, "-o", os.path.join(subdirectory, 'video.%(ext)s')])

# youtube-dl -v "https://player.vimeo.com/video/157005421" --referer "https://www.exrx.net/WeightExercises/BackGeneral/BWSupineRow" -o "video.mp4"
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
# open("video.mp4", 'wb').write(r.content)

# videoreq = urllib.request.Request(videoURL, headers)
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
