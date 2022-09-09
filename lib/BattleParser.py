import sys
import requests
import re
import getpass
from util import *

def getTeamSide(nr):
    if int(nr) == 1:
        return "Angreifer"
    elif int(nr) == 2:
        return "Verteidiger"
    else:
        raise Exception

def getBattles(world,msgID,form='text'):
    response = requests.request('GET','https://evergore.de/'+world+'?page=msg_view&msg_id='+str(msgID),headers=HDRS,allow_redirects=False)
    if 'text' in form:
        return response.text
    elif 'iter' in form:
        return response.iter_lines()

def analyseHunt(world,msgid,verbosity):
    msg = getBattles(world,msgid)
    overallResult = {}
    counter=0
    for i in re.finditer("battle_id=(\d+)",msg):
        printVerbose(i.group(1),verbosity)
        res = analyseBattle(world,i.group(1),verbosity)
        counter += 1
        for char in res.keys():
            # in Jagden nur Charaktere
            if char.startswith("M"):
                continue
            if not char in overallResult:
                overallResult[char] = res[char]
            else:
                for k,v in res[char].items():
                    if k == 'name':
                        continue
                    try:
                        overallResult[char][k] += v
                    except TypeError:
                        for typ in v.keys():
                            if typ not in overallResult[char]['no-bolzen'].keys():
                                overallResult[char]['no-bolzen'][typ] = res[char]['no-bolzen'][typ]
                            else:
                                overallResult[char]['no-bolzen'][typ] += res[char]['no-bolzen'][typ]
    overallResult['meta'] = {"no-battles": counter}
    return overallResult
    

def analyseBattle(world,battleID,verbosity):
  battleText=getBattle(world,battleID,form='iter')
#  for line in battleText:
#      print(line)
#  return 0
  battle_started = 0
# Datenformat Participants:
#
# ID: {
#   name: <name>
#   no-bolzen: {
#     typ: <Anzahl verbrauchter Bolzen pro Typ>
#   }
#   
# 
  participants = {}
  casts = {}
  for line in battleText:
      if not battle_started:
          if not re.search("<h2>Kampfereignisse \(Log\)</h2>",str(line)):
              continue
          else:
              battle_started = 1
              continue
      if (m := re.search("setParticipant\(\"([^\"]*)\",\"([^\"]*)\",(\d+)",str(line))):
          if m.group(1).startswith('M'):
              cnter = 0
              for n,p in participants.items():
                  if not n.startswith('M'):
                      continue
                  if re.search('^'+m.group(2)+" #",p['name']):
                      cnter += 1
              if cnter != 0:
                  name = m.group(2)+" #" + str(cnter+1)
              else:
                  name = m.group(2)+" #1"
          else:
              name = m.group(2)
          printVerbose("Found participant: "+name+", "+m.group(2)+"; Team: "+getTeamSide(m.group(3)),verbosity)
          participants[m.group(1)] = { "name":name, "miss":0,"hits":0,"krits":0,"dmg":0,"heal":0,"dodged":0,"attacked":0}
          continue
      # dd -> direct damage; non-dot-magie, NK/FK
      if (paramstring := re.search("dd\((.*)\);'$",str(line))):
          params = splitParams(paramstring.group(1))
          aID = params[3]
          tID = params[4]
          dmg = int(params[6])
          mode = int(params[5])
          attack = params[2]

          printVerbose("Found Char "+aID+" using "+attack,verbosity)

          # Bolzenverwendung
          if (g := re.search("\((.*[bB]olzen.*)\)",attack)):
              if "no-bolzen" not in participants[aID].keys():
                  participants[aID]["no-bolzen"] = { g.group(1): 1 }
              elif g.group(1) not in participants[aID]["no-bolzen"].keys():
                  participants[aID]["no-bolzen"][g.group(1)] = 1
              else:
                  participants[aID]["no-bolzen"][g.group(1)] += 1
          # Schadenssumme
          if mode == 0:
              participants[aID]['miss'] += 1
              continue
          if mode == 1:
              participants[aID]['hits'] += 1
              participants[tID]['dodged'] +=1
          if mode == 3 or mode == 5:
              if mode == 5:
                  participants[aID]['krits'] += 1
              participants[aID]['hits'] += 1
              participants[aID]['dmg'] += dmg
              participants[tID]['attacked'] +=1
              continue
      if (paramstring := re.search("dh\((.*)\);'$",str(line))):
          params = splitParams(paramstring.group(1))
          cID = params[3]
          heal = int(params[6])
          mode = int(params[5])
          hname = params[2]

          printVerbose("Found Char "+participants[cID]['name']+" using "+hname,verbosity)

          if mode == 0 or mode == 1:
              participants[cID]['miss'] += 1
              continue
          if mode == 3 or mode == 5:
              if mode == 5:
                  participants[cID]['krits'] += 1
              participants[cID]['hits'] += 1
              participants[cID]['heal'] += dmg
              continue
      if (paramstring := re.search("cast\((.*)\);'$",str(line))):
          params = splitParams(paramstring.group(1))
          cID = params[3]
          tID = params[4]
          castName = params[2]
          mode = int(params[5])

          printVerbose("Found Char "+participants[cID]['name']+" casting "+castName+" on "+participants[tID]['name'],verbosity)

          if mode == 3:
              participants[cID]['hits'] += 1
              participants[tID]['attacked'] += 1

              try:
                  casts[cID]['targets'].append(tID)
              except KeyError:
                  casts[cID] = {'targets': [tID]}
          if mode == 0:
              participants[cID]['miss'] += 1
          if mode == 1:
              participants[cID]['hits'] += 1
              participants[tID]['dodged'] += 1
          continue
      if (paramstring := re.search("dot\((.*)\);'$",str(line))):
          params = splitParams(paramstring.group(1))
          aID = params[2]
          tID = params[3]
          mode = int(params[4])
          dmg = int(params[5])
          # Schadenssumme
          if mode == 1:
              participants[aID]['hits'] += 1
              participants[tID]['dodged'] += 1
          if mode == 0:
              participants[aID]['miss'] += 1
              participants[tID]['attacked'] += 1
              continue
          if mode == 3 or mode == 5:
              if mode == 5:
                  participants[aID]['krits'] += 1
              participants[aID]['hits'] += 1
              participants[aID]['dmg'] += dmg
              participants[tID]['attacked'] += 1
              continue
      if (paramstring := re.search("hot\((.*)\);'$",str(line))):
          params = splitParams(paramstring.group(1))
          cID = params[2]
          heal = int(params[5])
          mode = int(params[4])
          hname = params[1]

          printVerbose("Found Char "+participants[cID]['name']+" using "+hname,verbosity)

          if mode == 0 or mode == 1:
              participants[cID]['miss'] += 1
              continue
          if mode == 3 or mode == 5:
              if mode == 5:
                  participants[cID]['krits'] += 1
              participants[cID]['hits'] += 1
              participants[cID]['heal'] += dmg
              continue

      if re.search("^b'(setLife|unconcious|move|ctm|ctr)\(",str(line)):
          continue

      if re.search("winner\(\d\)",str(line)):
          break
  return participants
