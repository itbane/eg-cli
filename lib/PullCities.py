import requests
import re

from util import *

def getCities(verbose,world):
  printVerbose('Pulling cities for '+world,verbose)
  response = requests.request('GET','https://evergore.de/'+world+'?page=ranking_town',headers=HDRS,allow_redirects=False)
  pattern = re.compile(r'page=info_town&town_id=(\d+)">([^<]*)<')

  tdata = readCities()
  change = 0

  for tid,tname in re.findall(pattern,response.text):
    response = requests.request('GET','https://evergore.de/'+world+'?page=info_town&town_id='+str(tid),headers=HDRS,allow_redirects=False)
    if not world in tdata.keys():
      X,Y = splitCoord(re.search("page=map&[^>]*>(\d+:\d+)</a>", response.content.decode('utf-8')).group(1))
      tdata[world] = {}
      tdata[world][tname] = {"id":tid,"X":X,"Y":Y}
      change = 1
    elif not tname in tdata[world].keys():
      X,Y = splitCoord(re.search("page=map&[^>]*>(\d+:\d+)</a>", response.content.decode('utf-8')).group(1))
      tdata[world][tname] = {"id":tid,"X":X,"Y":Y}
      change = 1
  if change:
    saveCities(tdata)

  return True

