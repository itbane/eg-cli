import os
import glob
from EgCli.util import *

itemset_list = [
    "Kupfer-Kette",
    "Kupfer-Platte",
    "Eisen-Kette",
    "Eisen-Platte",
    "Sorandil-Kette",
    "Sorandil-Platte",
    "Adamant-Kette",
    "Adamant-Platte",
    "Mithril-Kette",
    "Mithril-Platte",
]

def get_arguments():
    subarguments = {
        "--from-recipe-list": {
            "help": "Comma-Separated list of recipes to calculate the requried ingredients for", "dest": "recipe_list",
            "metavar": "<recipe-list>", "type": recipes_from_input
        },
        "--get-from-guild-storage": {
            "help": "Should the ingredients be taken from guild storage?", "dest": "get_from_guild_storage",
            "action": "store_true"
        },
        "--add-craftkits": {
            "help": "Add the calculated recipes", "dest": "add_craftkits", "action": "store_true"
        },
        "--engrave": { "metavar": "<charname>", "help": "Charakter, auf den die Bausätze personalisiert werden sollen",
                      "dest": "engrave_target", "type": str },
        "--itemset": { "metavar": "<setname>", "help": "Art des Sets, das hergestellt werden soll", "type": str,
                      "choices": itemset_list, "dest": "itemset" }
    }
    return "Recipes", subarguments

def recipes_from_input(data) -> dict:
    if isinstance(data, str):
        if data.startswith("@"):
            data = data[1:]
            if data.endswith(".json"):
                recipes = read_json(data)
            else:
                raise NotImplementedError("{} is not a supported file format".format(recipes))
        else:
        # split the items
            recipes = self.__split_recipe_string(recipes)
    elif isinstance(data, dict):
        # get ingredients
        recipes = data
    else:
        print(type(recipes))
        raise argparse.ArgumentTypeError("'--calculate-ingredients' benötigt eine Kommagetrennte Liste von "
                                         "Bausätzen (<bausatz>:<anzahl>[,<bausatz>:<anzahl>]) oder eine Datei "
                                         "@datei")
    return recipes

def get_function():
    return Recipe.do_stuff

class Recipes():
    def __init__(self, eg):
        self.eg = eg
        self.recipes = self.__get_items()

    def __split_recipe_string(self, recipes):
        recipe_dict = {}
        for item in recipes.split(','):
            parts = item.split(':')
            recipe_dict[parts[0]] = parts[1]
        return recipe_dict

    def __get_items(self):
        recipes = {}
        for file in glob.glob(r"data/recipes_{}_*.json".format(self.eg.world)):
            recipes.update(read_json(file))
        return recipes

    def get_items_of_set(self, setname: str) -> list:
        items = []
        for name, data in self.recipes.items():
            if re.match(setname, name):
                items.append(name)
        return items

    def get_recipe(self, name: str) -> dict:
        return self.recipes[name]

    def calculate_ingredients(self, recipes):
        if not recipes:
            raise argparse.ArgumentTypeError("Leere Liste von Bausätzen!")
        wanted_ingredients = {}
        for recipe, count in recipes.items():
            try:
                ingredients = self.recipes[recipe]["ingredients"]
            except KeyError:
                print("Bausatz '{}' nicht bekannt".format(recipe))
                os.sys.exit(0)
            for i in ingredients:
                try:
                    wanted_ingredients[i["name"]] += int(i["count"]) * int(count)
                except KeyError:
                    wanted_ingredients[i["name"]] = int(i["count"]) * int(count)
        return wanted_ingredients
