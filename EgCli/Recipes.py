import os
import glob
from EgCli.util import *

def get_arguments():
    subarguments = {
        "--calculate-ingredients": {
            "help": "Comma-Separated list of recipes to calculate the requried ingredients for", "dest": "recipe_list",
            "metavar": "<recipe-list>", "required": True
        },
        "--get-from-guild-storage": {
            "help": "Should the ingredients be taken from guild storage?", "dest": "get_from_guild_storage",
            "action": "store_true"
        },
        "--add-recipes": {
            "help": "Add the calculated recipes", "dest": "add_recipe", "action": "store_true"
        }
    }
    return "Recipes", subarguments

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

    def get_recipe(self, name: str) -> dict:
        return self.recipes[name]

    def calculate_ingredients(self, recipes):
        if isinstance(recipes, dict):
            # get ingredients
            pass
        elif isinstance(recipes, str):
            if recipes.startswith("@"):
                recipes = recipes[1:]
                if recipes.endswith(".json"):
                    recipes = read_json(recipes)
                else:
                    raise NotImplementedError("{} is not a supported file format".format(recipes))
            else:
            # split the items
                recipes = self.__split_recipe_string(recipes)
        else:
            raise argparse.ArgumentTypeError("'--calculate-ingredients' benötigt eine Kommagetrennte Liste von "
                                             "Bausätzen (<bausatz>:<anzahl>[,<bausatz>:<anzahl>]) oder eine Datei "
                                             "@datei")

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
