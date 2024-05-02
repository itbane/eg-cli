#!/usr/bin/env python3
import argparse
import sys
import getpass
import json
import os
import inspect

from time import sleep
import datetime

from EgCli.util import *
import EgCli.BattleFinder as BattleFinder
import EgCli.BattleParser as BattleParser
import EgCli.RoutePlaner as RoutePlaner
import EgCli.PullCities as PullCities
import EgCli.StartBattle as StartBattle
import EgCli.GuildStorage as GuildStorage
import EgCli.PullRecipes as PullRecipes
import EgCli.Recipes as Recipes
import EgCli.character as character


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
    sbParser.add_argument('--forever', help='Keep fighting until APs are empty', action="store_true", dest="forever")
    # sbParser

    return parser.parse_args()

def main():
    parser_data = {}
    plugin_list = [
        GuildStorage,
        PullRecipes,
        Recipes
    ]
    for plugin in plugin_list:
        parser_name, sub_arguments = plugin.get_arguments()
        parser_data[parser_name] = sub_arguments

    args = get_arguments(parser_data)
    set_verbosity(args.verbose)

    todo_functions = {
        "GuildStorage": guild_storage,
        "BattleFinder": battle_finder,
        "PullCities": pull_cities,
        "RoutePlaner": route_planer,
        "BattleParser": battle_parser,
        "StartBattle":start_battle,
        "PullRecipes": pull_recipes,
        "Recipes": recipes
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
        print_verbose("Running BattleParser")
        if args.battleid is not None:
            res = BattleParser.analyseBattle(args.world,args.battleid,args.verbose)
        elif args.msgid is not None:
            res = BattleParser.analyseHunt(args.world,args.msgid,args.verbose)
        else:
            print("Need either '--msgid' or '--id'")
        if args.print:
            printBattleStats(res,args.filter.split(','))

def start_battle(eg, args):
    print_verbose("Running StartBattle")

    if args.forever:
        while True:
            result = StartBattle.start_horde_battle(eg, 50, args.verbose)
            if result in [ "too_few_ap", "no_enemy_group", "no_group_id", "battle_not_started" ]:
                break
            print("{}: Wait for 120 seconds".format(datetime.datetime.now()))
            sleep(120)
    elif StartBattle.start_horde_battle(eg, 50, args.verbose):
        os.sys.exit(0)
    else:
        os.sys.exit(1)

def guild_storage(eg, args):
    print_verbose("Running GuildStorage")
    gs = GuildStorage.GuildStorage(eg)
    items = gs.list_items(args.item_category, args.use_broken)
    char = character.EvergoreCharacter(eg)

    build_items = {}
    # take items in queue into account
    queued_items = char.get_current_craftkits()

    map_craft_and_storage_itemcategories = {
        "schwere-rüstung": "Schmieden (Schwere Rüstungen)"
    }

    all_items = char.get_available_recipes(map_craft_and_storage_itemcategories[args.item_category])

    # print("Anzahl Items: {}".format(len(items)))
    if args.create_itemlist or args.add_craftkits:
        # get list of specific items
        for num in range(1, args.wanted_minimum + 1):
            build_items[num] = []

        for item in all_items.keys():
            try:
                queued_count = queued_items[item]
            except KeyError:
                # item not in queue
                queued_count = 0
            try:
                comb_item_count = items[item] + queued_count
            except KeyError:
                comb_item_count = 0 + queued_count
            if comb_item_count < args.wanted_minimum:
                build_items[args.wanted_minimum - comb_item_count].append(item)
        print(build_items)
    elif args.list_items:
        # list ALL the items
        for item, amount in items.items():
            print("{}: {}".format(item, amount))
        return True
    if len(build_items) == 0:
        print("Keine Objekte benötigt")
        return True

    if args.wanted_minimum and args.create_itemlist:
        # only print the list, most required to least
        for count, items in reversed(build_items.items()):
            for name in items:
                print("{}: Need {} more!".format(name, count))
    elif args.add_craftkits:
        # create crafting kits for the required items
        r = Recipes.Recipes(eg)
        time_left = char.get_available_crafting_time()
        recipes = {}

        for count, items in reversed(build_items.items()):
            # add most required items to list of recipes if they still fit in the available time
            for item in items:
                print_verbose("looking at {}, wanting {}".format(item, count))
                print_verbose("  Time left: {}".format(time_left))
                print_verbose("  Time required: {}".format(r.get_recipe(item)["time"]))
                if time_left > r.get_recipe(item)["time"]:
                    time_left -= r.get_recipe(item)["time"]
                    try:
                        build_items[count-1].append(item)
                    except KeyError:
                        # Kein Item wird mehr benötigt
                        pass
                    try:
                        recipes[item] += 1
                    except KeyError:
                        recipes[item] = 1
        print_verbose("Zu bauende Gegenstände:")
        print_verbose(recipes)
        print_verbose("Übrige Zeit: {}".format(time_left))

        recipe_filename = "data/recipes_{}.json".format(str(datetime.date.today()))
        print_verbose("Liste der zu bauenden Gegenstände wird unter {} abgelegt.".format(recipe_filename))
        # save the recipes for old times' sake
        with open (recipe_filename, "w") as f:
            json.dump(recipes, f, indent=2)

        # gs.get_items_from_storage(r.calculate_ingredients(recipes))
        char.add_craftkit_list(recipes)

def pull_recipes(eg, args):
    print_verbose("Running PullRecipes")
    pr = PullRecipes.PullRecipes(eg)
    if args.get_categories:
        print(json.dumps(pr.get_category_mapping()))
    else:
        recipes = pr.get_recipes(args.item_category)
        save_json(recipes, filename="data/recipes_{}_{}.json".format(eg.world, args.item_category))
        print("Itemlist wurde in {} abgelegt.".format("data/recipes_{}_{}.json".format(eg.world, args.item_category)))

def recipes(eg, args):
    print_verbose("Running Recipes")
    r = Recipes.Recipes(eg)
    char = character.EvergoreCharacter(eg)
    if args.itemset is not None:
        recipe_list = {}
        # elif args.add_craftkits and args.engrave_target is not None and 
        print(f"Erstelle Bausätze Set: {args.itemset}")
        r = Recipes.Recipes(eg)
        char_recipes = char.get_available_recipes().keys()
        req_time = 0
        for item in r.get_items_of_set(args.itemset):
            if item not in char_recipes:
                print(f"Bausatz {item} kann nicht hergestellt werden: Rezept nicht bekannt. Breche ab")
                os.sys.exit(1)
            recipe_list[item] = 1
            req_time += r.get_recipe(item)["time"]
        time_left = char.get_available_crafting_time()
        if time_left < req_time:
            print(f"Benötigte Zeit ({req_time}s) ist länger als verfügbare Zeit ({time_left}s). Breche ab.")
            os.sys.exit(1)
        ingredients = r.calculate_ingredients(recipe_list)

    elif args.recipe_list is not None:
        recipe_list = args.recipe_list
        ingredients = r.calculate_ingredients(args.recipe_list)
    else:
        print(f"Kein bekanntes Kommando - verwende entweder '--from-recipe-list' or '--itemset'")
        os.sys.exit(1)
    print_verbose(f"Continue to add recipies")

    print(recipe_list)
    print(ingredients)

    if args.get_from_guild_storage:
        gs = GuildStorage.GuildStorage(eg)
        gs.get_items_from_storage(ingredients)
    if args.add_craftkits:
        char.add_craftkit_list(recipe_list, target = args.engrave_target)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Aborted")
        os.sys.exit(0)
    except NotImplementedError as e:
        print("Fehler: {}".format(e))
    except argparse.ArgumentTypeError as e:
        print("Fehler: {}".format(e))
