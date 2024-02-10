#!/bin/python
import sys
import requests
import re
import getpass
from EgCli.util import *

def findBattleIDs(world,verbose,player,ll,ul,first):
  print_verbose("looking for battles on "+world)
  print_verbose("Lower bound of battle IDs: "+str(ll))
  print_verbose("Upper bound of battle IDs: "+str(ul))
  if player:
    print_verbose("Filtering for player "+player)
  
  battleID=ll
  while battleID <= ul:
    print_verbose("looking for battle ID "+str(battleID))
    battleContent=getBattle(world,battleID)
    print(battleContent)
    print(player)
    if re.search("setParticipant\(.*,[\"']"+player+"[\"']", battleContent):
      print("Battle found: "+str(battleID))
      if first:
        print_verbose("Got --first parameter, not looking further...")
        break
    elif re.search("Kampfbericht.*Der Kampf existiert nicht.",battleContent):
      print_verbose("BattleID higher than existing battles - aborting")
      break
    battleID+=1
