import requests
import re

from EgCli.util import *

def getCities(eg, verbose):
  print_verbose('Pulling cities for '+eg.world)
  response = eg.get_from_eg(eg.link, params={"page": "ranking_town"})
  pattern = re.compile(r'page=info_town&town_id=(\d+)">([^<]*)<')

  tdata = read_json()
  change = 0

  for tid,tname in re.findall(pattern,response.text):
    response = eg.get_from_eg(eg.link, params={"page": "info_town", "town_id": str(tid)})
    if not eg.world in tdata.keys():
      X,Y = splitCoord(re.search("page=map&[^>]*>(\d+:\d+)</a>", response.content.decode('utf-8')).group(1))
      tdata[eg.world] = {}
      tdata[eg.world][tname] = {"id":tid,"X":X,"Y":Y}
      change = 1
    elif not tname in tdata[eg.world].keys():
      X,Y = splitCoord(re.search("page=map&[^>]*>(\d+:\d+)</a>", response.content.decode('utf-8')).group(1))
      tdata[eg.world][tname] = {"id":tid,"X":X,"Y":Y}
      change = 1
  if change:
    print_verbose("Änderungen in Städten, speichere")
    save_json(tdata)
  else:
    print_verbose("Keine Änderungen in Städten, Beende")

  return True

