import os
import requests
from EgCli.util import *

def get_arguments():
    """
    Provides the list of subarguments to the main script
    """
    subarguments = {
        "--category": { "metavar": "<item-category>", "help": "Kategorie der Gegenstände. für die Baupläne "
                       "heruntergeladen werden", "dest": "item_category", "type": str, "choices": [ "schwere-rüstung" ],
                       "default": "schwere-rüstung" }
    }
    return "PullRecipes", subarguments

def get_function():
    """
    Returns the function to do the actual work
    """
    return PullRecipes.get_recipies()


class PullRecipes():
    """
    Class to encapsulate all the functions necessary to get recipes from the academy screen
    """
    def __init__(self, eg):
        self.eg = eg

    def get_recipes(self, cat):
        """
        Retrieve a list of all recipes of a specified category.

        Currently supported categories:
            - "Schmieden (Schwere Rüstungen): schwere-rüstung"
        """
        cat_map = {
            "schwere-rüstung": 62
        }
        params = {
            "page": "academy_craft",
            "selection": cat_map[cat]
        }
        # get the page with all the recipes
        academy_page = self.eg.get_from_eg(self.eg.link, params=params)
#        print(academy_page.text)
        # iterate through all the recipes
        recipes = {}
        for recipe in re.findall(r'<td><input type="checkbox" .*?</tr>', academy_page.text, re.DOTALL):
            # print(recipe)
            item_data = re.match(r'.*?<b>([^<]*)</b>.*?Zutaten.*?<br>(.*?</td>)', recipe, re.DOTALL)
            # print("Name: {}".format(item_data.group(1)))
            ingredients = []
            for ingredient in re.findall(r'>(\d+)\s+(.*?)</font>', item_data.group(2), re.DOTALL):
                ingredients.append({"count": ingredient[0], "name": ingredient[1]})
            recipes.update({item_data.group(1): ingredients})

        return recipes
