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
    print(battleContent)
    print(player)
    if re.search("setParticipant\(.*,[\"']"+player+"[\"']", battleContent):
      print("Battle found: "+str(battleID))
      if first:
        printVerbose("Got --first parameter, not looking further...",verbose)
        break
    elif re.search("Kampfbericht.*Der Kampf existiert nicht.",battleContent):
      printVerbose("BattleID higher than existing battles - aborting",verbose)
      break
    battleID+=1
