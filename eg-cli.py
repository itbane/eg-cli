#!/usr/bin/env python3
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
import GuildStorage

def get_arguments(parser_data):
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
    parser_list = []
    for parser_name, parser_options in parser_data.items():
        temp_parser = subparser.add_parser(parser_name)
        for subarg_name, subarg_options in parser_options.items():
            temp_parser.add_argument(subarg_name, **subarg_options)
        parser_list.append(temp_parser)

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

    return parser.parse_args()

def main():
    parser_data = {}
    parser_name, sub_arguments = GuildStorage.get_arguments()
    parser_data[parser_name] = sub_arguments
    args = get_arguments(parser_data)

    todo_functions = {
        "GuildStorage": guild_storage,
        "BattleFinder": battle_finder,
        "PullCities": pull_cities,
        "RoutePlaner": route_planer,
        "BattleParser": battle_parser,
        "StartBattle":start_battle
    }

    eg = EvergoreClient(args.world, login=args.login, cookie=args.cookie)
    todo_functions[args.command](eg, args)

def battle_finder(args):
      BattleFinder.findBattleIDs(args.world,args.verbose,args.player,args.ll,args.ul,args.first)

def pull_cities(eg, args):
      PullCities.getCities(eg, args.verbose)

def route_planer(args):
      RoutePlaner.travel(args.source,args.target,args.verbose,args.add,args.list,args.create,args.world)

def battle_parser(args):
        printVerbose("Running BattleParser",args.verbose)
        if args.battleid is not None:
            res = BattleParser.analyseBattle(args.world,args.battleid,args.verbose)
        elif args.msgid is not None:
            res = BattleParser.analyseHunt(args.world,args.msgid,args.verbose)
        else:
            print("Need either '--msgid' or '--id'")
        if args.print:
            printBattleStats(res,args.filter.split(','))

def start_battle(eg, args):
    printVerbose("Running StartBattle", args.verbose)

    if StartBattle.start_horde_battle(eg, 50, args.verbose):
        os.sys.exit(0)
    else:
        os.sys.exit(1)

def guild_storage(eg, args):
    printVerbose("Running GuildStorage", args.verbose)
    gs = GuildStorage.GuildStorage(eg)
    items = gs.list_items(args.item_category, args.use_broken)

    # print("Anzahl Items: {}".format(len(items)))
    if args.wanted_minimum:
        all_items = GuildStorage.get_full_item_list(args.item_category)
        for item in all_items:
            try:
                if items[item] < args.wanted_minimum:
                    print("{}: Need {} more!".format(item, args.wanted_minimum - items[item]))
            except KeyError:
                print("{}: Need {} more!".format(item, args.wanted_minimum))
    elif args.list_items:
        for item, amount in items.items():
            print("{}: {}".format(item, args.wanted_minimum))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Aborted")
        os.sys.exit(0)
