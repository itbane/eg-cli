import requests
import re
import argparse
import sys
import json

from EgCli.exceptions import *

VERBOSE=False

def set_verbosity(verbosity: bool):
    global VERBOSE
    VERBOSE = verbosity

def readCredentials(verbose):
  print_verbose("Loging in")
  user=input("User: ")
  password=getpass.getpass()
  return user,password

def print_verbose(msg: str):
    if VERBOSE:
        print(msg)

def printHeaders():
  print(HDRS)

def egCoord(coord):
  pat=re.compile(r"^\d+:\d+$")
  if pat.match(coord):
    return coord
  elif (ccoord := getCity(coord)):
    return ccoord
  raise argparse.ArgumentTypeError

def splitCoord(coords):
 return coords.split(':')[0],coords.split(':')[1]

def read_json(filename='cities.json'):
    try:
        with open(filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return data

def save_json(data,filename='cities.json'):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False, indent=4)

def getCityList(world):
  cities = read_json()
  try:
    return list(cities[world].keys())
  except KeyError:
    return []

def getCity(city):
  cities = read_json()
  for world in cities.keys():
    try:
      return str(cities[world][city]['X'])+":"+str(cities[world][city]['Y'])
    except:
      pass

  print("City not found - maybe pull cities?")
  sys.exit(1)

def getToken(page):
  response = requests.request('GET','https://evergore.de/zyrthania?page='+page,headers=HDRS)
  return re.search('name="token"\s*value="(.*?)"', response.content.decode('utf-8')).group(1)

def getBattle(world,battleID,form='text'):
  response = requests.request('GET','https://evergore.de/'+world+'?page=battle_report&battle_id='+str(battleID),headers=HDRS,allow_redirects=False)
  if 'text' in form:
    return response.text
  elif 'iter' in form:
    return response.iter_lines()

def printBattleStats(res,filter=[],form='text'):
    for p in res.keys():
        if p == 'meta':
            print("Stats:")
            print("  Anzahl Kämpfe: "+str(res['meta']['no-battles']))
            continue
        print(res[p]["name"]+":")
        if 'Bolzen' in filter:
            try:
                for k,v in res[p]['no-bolzen'].items():
                    print("  "+k+": "+str(v))
            except KeyError:
                pass
        if 'Schaden' in filter:
            try:
                print("  Schaden (Summe): "+str(res[p]['dmg']))
            except KeyError:
                pass
        if 'Heilung' in filter:
            try:
                print("  Heilung (Summe): "+str(res[p]['heal']))
            except KeyError:
                pass
        if 'Stats' in filter:
            print("  Hits: "+str(res[p]['hits']))
            print("  Misses: "+str(res[p]['miss']))
            print("  Krits: "+str(res[p]['krits']))
            try:
                print("  Trefferchance: "+str(int(res[p]['hits']/(res[p]['hits']+res[p]['miss'])*10000)/100)+"%")
            except ZeroDivisionError:
                print("  Trefferchance: 0%")
            try:
                print("  Kritchance: "+str(int(res[p]['krits']/res[p]['hits']*10000)/100)+"%")
            except ZeroDivisionError:
                print("  Kritchance: 0%")
            try:
                print("  Ausweichchance: "+str(int(res[p]['dodged']/(res[p]['dodged']+res[p]['attacked'])*10000)/100)+"%")
            except ZeroDivisionError:
                print("  Ausweichchance: 0%")

def translate_time(timestring: str) -> int:
    time_string = re.search("((\d+) Tag)?\s*((\d+) Std\.)?\s*((\d+) Min\.)?\s*((\d+)Sek\.)?", timestring)
    time_seconds = 0

    try:
        time_seconds += int(time_string.group(8))
    except(TypeError):
        # keine Sekunden
        pass
    try:
        time_seconds += int(time_string.group(6)) * 60
    except(TypeError):
        # keine Minuten
        pass
    try:
        time_seconds += int(time_string.group(4)) * 3600
    except(TypeError):
        # keine Stunden
        pass
    try:
        time_seconds += int(time_string.group(2)) * 86400
    except(TypeError):
        # keine Sekunden
        pass

    return time_seconds

def splitParams(string):
    params = string.split(',')
    for i,v in enumerate(params):
        if (m := re.search('^"(.*)"$',v)):
            params[i] = m.group(1)
    return params


class EvergoreClient:
    def __init__(self, world, login=None, cookie=None):
        self.baselink = "https://evergore.de/"
        self.link = "{}{}".format(self.baselink, world)
        self.world = world
        self.headers = {
            "User-Agent": "itbane eg automation",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.headers["Cookie"] = self.__get_cookie(login, cookie)
        self.__chooseCharacter(world)

    def get_from_eg(self, url, params=None):
        if params is None:
            params = {}
        return requests.get(url, params=params, headers=self.headers)

    def post_to_eg(self, url, params=None, data=None):
        if data is None:
            data = {}
        if params is None:
            params = {}
        return requests.post(url, params=params, headers=self.headers, data=data)

    def __chooseCharacter(self, world):
        response = self.get_from_eg(self.baselink + "portal")
        charNumber=re.search('action="/'+world+'".*\n.*\n.*value="(.*?)"', response.content.decode('utf-8')).group(1)
        data = {'character': charNumber}
        response = self.post_to_eg(self.link,data=data)

    def __get_cookie(self, login, cookie):
        if login is not None:
            try:
                with open('.config') as f:
                    data = json.load(f)
                    user = data['user']
                    password = data['password']
            except (PermissionError, FileNotFoundError, KeyError):
                print_verbose("config not found, reading from stdin")
                user,password = readCredentials(args.verbose)

            return self.__performLogin(user,password)
        if cookie is not None:
            return cookie

    def __performLogin(self, user, password):
        data={
            'forward':'portal',
            'login':user,
            'password':password
        }
        response = requests.request('POST','https://evergore.de/login', headers=self.headers,
                                    data=data, allow_redirects=False)
        if response.status_code == 302:
            return re.search("(eg_sid=[^;]*).*", response.headers['Set-Cookie']).group(1)
        elif response.status_code == 200:
            if (re.search("Ihr seid bereits angemeldet",response.text)):
                print(response.headers)
            else:
                print("Got incorrect response code "+str(response.status_code))
                print(response.text)
                raise EGError

        print("Could not read cookie from login")
        raise EGError
