#!/bin/python3
import argparse
import sys
import getpass
import json
import os

sys.path.append("./lib")
from util import *
import BattleFinder
import BattleParser
import RoutePlaner
import PullCities
import StartBattle

parser = argparse.ArgumentParser(description='find Evergore Battle')

# general arguments
parser.add_argument('-w', '--world', metavar="<world>", help='The world to use', dest="world", type=str, choices=["zyrthania","dunladan","keloras"], default='zyrthania')
parser.add_argument('-v', '--verbose', help='Activate verbose mode.', dest="verbose", action="store_true")

# how to login - mutually exclusive, but general
auth = parser.add_mutually_exclusive_group(required=False)
auth.add_argument('--login', help='If login should be performed. Mutually exclusive with --cookie', dest="login", action='store_true')
auth.add_argument('--cookie', metavar="<cookie>", help='Cookie from existing login. Mutually exclusive with --login', dest="cookie", type=str)

# subparsers for different functionalities
subparser = parser.add_subparsers(dest='command')
bfParser = subparser.add_parser('BattleFinder')
bpParser = subparser.add_parser('BattleParser')
rpParser = subparser.add_parser('RoutePlaner')
pcParser = subparser.add_parser('PullCities')
sbParser = subparser.add_parser('StartBattle')

# battleFinder args
bfParser.add_argument('-l', '--lower-id', metavar='<lower-battleid>', help='the lower bound of battle IDs that should be looked at', dest='ll', type=int, required=True)
bfParser.add_argument('-u', '--upper-id', metavar='<upper-battleid>', help='the upper bound of battle IDs that should be looked at', dest='ul', type=int, default='9999999')
bfParser.add_argument('-p', '--player', metavar='<playername>', help='a name (or colon-separated list names) of players to look for', dest='player', type=str)
bfParser.add_argument('-f', '--first', help='Wether only one battle should be printed', dest="first", action='store_true')

# RoutePlaner args
rpParser.add_argument('-s', '--source', metavar='<source>', help='The coordinates (XX:YY) or city where you start', dest="source", type=egCoord, required=True)
rpParser.add_argument('-t', '--target', metavar='<target>', help='The coordinates (XX:YY) or city where you want to go', dest="target", type=egCoord, required=True)
rpParser.add_argument('-a', '--add', help='should commands be added?', dest='add', action='store_true')
rpParser.add_argument('-l', '--list', help='should commands be printed?', dest='list', action='store_true')
rpParser.add_argument('-c', '--create-group', help='should the group be opened (if not already in group)', dest='create',action='store_false')

# BattleParser
bpParser.add_argument('--id', metavar='<battleid>', help='The Battle ID to be analysed', dest='battleid', type=int)
bpParser.add_argument('--report',metavar='<reportid>',help='The Message ID of the group to be analysed', dest='msgid',type=int)
bpParser.add_argument('--print',help='If the result should be printed', dest='print', action='store_true')
bpParser.add_argument('--filter',metavar='<feld>[,<feld>]',help='Comma-separated list of Fields to print', dest='filter', type=str,default="")

# StartParser
# sbParser

args = parser.parse_args()

if args.login:
  try:
    with open('.config') as f:
      data = json.load(f)
    user = data['user']
    password = data['password']
  except:
    printVerbose("config not found, reading from stdin",args.verbose)
    user,password = readCredentials(args.verbose)
  cookie=performLogin(user,password)
  printVerbose("Got cookie: "+cookie,args.verbose)
elif args.cookie:
  cookie=args.cookie
  setCookie(cookie)

if args.login or args.cookie:
  chooseCharacter(args.world)
  printVerbose("Command: "+args.command,args.verbose)

if args.command == 'BattleFinder':
  BattleFinder.findBattleIDs(args.world,args.verbose,args.player,args.ll,args.ul,args.first)
elif args.command == 'PullCities':
  PullCities.getCities(args.verbose,args.world)
elif args.command == 'RoutePlaner':
  RoutePlaner.travel(args.source,args.target,args.verbose,args.add,args.list,args.create,args.world)
elif args.command == 'BattleParser':
    printVerbose("Running BattleParser",args.verbose)
    if args.battleid is not None:
        res = BattleParser.analyseBattle(args.world,args.battleid,args.verbose)
    elif args.msgid is not None:
        res = BattleParser.analyseHunt(args.world,args.msgid,args.verbose)
    else:
        print("Need either '--msgid' or '--id'")
    if args.print:
        printBattleStats(res,args.filter.split(','))
elif args.command == "StartBattle":
    printVerbose("Running StartBattle", args.verbose)

    if StartBattle.start_horde_battle(args.world, 50, args.verbose):
        os.sys.exit(0)
    else:
        os.sys.exit(1)
