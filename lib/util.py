import requests
import re
import argparse
import sys
import json

from exceptions import *
def readCredentials(verbose):
  printVerbose("Loging in",verbose)
  user=input("User: ")
  password=getpass.getpass()
  return user,password

def printVerbose(msg,verbose):
  if verbose:
    print(msg)

# Default values
HDRS={
  'User-Agent': 'itbane eg automation',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.5',
  'Connection': 'keep-alive',
  'Upgrade-Insecure-Requests': '1'
}

def setCookie(cookie):
    HDRS['Cookie'] = cookie

def performLogin(user,password):
  data={
    'forward':'portal',
    'login':user,
    'password':password
  }
  response = requests.request('POST','https://evergore.de/login',headers=HDRS,data=data,allow_redirects=False)
  if response.status_code == 302:
    nc=re.search("(eg_sid=[^;]*).*", response.headers['Set-Cookie']).group(1)
  elif response.status_code == 200:
    if (re.search("Ihr seid bereits angemeldet",response.text)):
      print(response.headers)
  else:
    print("Got incorrect response code "+str(response.status_code))
    print(response.text)
    raise EGError
  if nc:
    setCookie(nc)
    return nc
  else:
    print("Could not read cookie from login")
    raise EGError

def printHeaders():
  print(HDRS)

def chooseCharacter(world):
  response = requests.request('GET','https://evergore.de/portal',headers=HDRS,allow_redirects=False)
  charNumber=re.search('action="/'+world+'".*\n.*\n.*value="(.*?)"', response.content.decode('utf-8')).group(1)
  data = {'character': charNumber}
  response = requests.request('POST','https://evergore.de/'+world,headers=HDRS,data=data)

def egCoord(coord):
  pat=re.compile(r"^\d+:\d+$")
  if pat.match(coord):
    return coord
  elif (ccoord := getCity(coord)):
    return ccoord
  raise argparse.ArgumentTypeError

def splitCoord(coords):
 return coords.split(':')[0],coords.split(':')[1]

def readCities(filename='cities.json'):
    try:
        with open(filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return data

def saveCities(data,filename='cities.json'):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False, indent=4)

def getCityList(world):
  cities = readCities()
  try:
    return list(cities[world].keys())
  except KeyError:
    return []

def getCity(city):
  cities = readCities()
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

def splitParams(string):
    params = string.split(',')
    for i,v in enumerate(params):
        if (m := re.search('^"(.*)"$',v)):
            params[i] = m.group(1)
    return params
