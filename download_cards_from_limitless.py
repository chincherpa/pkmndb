import os
import urllib3
import urllib.request
from bs4 import BeautifulSoup

http = urllib3.PoolManager()

lSets = [
  'BLK',
  'WHT',
]

for sSet in lSets:
  print(sSet)
  # get source code
  resp = http.request("GET", f"https://limitlesstcg.com/cards/{sSet}")
  html = resp.data
  soup = BeautifulSoup(html, 'html.parser')
  # get image urls
  image_urls = [img['src'] for img in soup.find_all('img') if img.has_attr('src')]
  # iterate over urls
  for url in image_urls:
    url = url.replace('_SM', '')
    filename = url.split('/')[-1]
    # check if already downloaded
    if not os.path.isfile(filename):
      print(f"downloading {filename}")
      # download image
      urllib.request.urlretrieve(url, filename)
    else:
      print(f"skipping '{filename}' - already downloaded")
