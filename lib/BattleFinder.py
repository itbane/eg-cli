#!/bin/python
import sys
import requests
import re
import getpass
from util import *

def findBattleIDs(world,verbose,player,ll,ul,first):
  printVerbose("looking for battles on "+world,verbose)
  printVerbose("Lower bound of battle IDs: "+str(ll),verbose)
  printVerbose("Upper bound of battle IDs: "+str(ul),verbose)
  if player:
    printVerbose("Filtering for player "+player,verbose)
  
  battleID=ll
  while battleID <= ul:
    printVerbose("looking for battle ID "+str(battleID),verbose)
    battleContent=getBattle(world,battleID)
    if re.search("setParticipant\('.*,'"+player+"'", battleContent):
      print("Battle found: "+str(battleID))
      if first:
        printVerbose("Got --first parameter, not looking further...",verbose)
        break
    elif re.search("Kampfbericht.*Der Kampf existiert nicht.",battleContent):
      printVerbose("BattleID higher than existing battles - aborting",verbose)
      break
    battleID+=1

def getBattle(world,battleID):
  response = requests.request('GET','https://evergore.de/'+world+'?page=battle_report&battle_id='+str(battleID),headers=HDRS,allow_redirects=False)
  return response.text
