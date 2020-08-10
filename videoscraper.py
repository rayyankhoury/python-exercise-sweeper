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



https://player.vimeo.com/video/

?muted=1