import os
import requests
from EgCli.util import *

def get_arguments():
    """
    Provides the list of subarguments to the main script
    """
    subarguments = {
        "--category": { "metavar": "<item-category>", "help": "Kategorie der Gegenstände. für die Baupläne "
                       "heruntergeladen werden", "dest": "item_category", "type": str, "default": "Schwere-Rüstungen",
                       "choices": [
                            "Steinverarbeitung", "Erzverarbeitung", "Stoff-und-Lederverarbeitung", "Konstruktion",
                            "Schwerter", "Dolche", "Äxte", "Keulen", "Stangenwaffen", "Leichte-Rüstungen",
                            "Schwere-Rüstungen", "Magiestäbe", "Bögen", "Armbrüste", "Schneidern-Leichte-Rüstungen",
                            "Alchemie", "Holzverarbeitung"
                       ]
                      },
        "--get-categories": {
                                "help": "Exportiert die verfügbaren Kategorien in der Akademie im JSON Format",
                                "dest": "get_categories", "action": "store_true"
                            }
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

    def get_category_mapping(self):
        """
        Retrieve all the categories in the academy
        """
        params = {"page":"academy_craft"}
#        print(self.eg.get_from_eg(self.eg.link, params=params).text)
        academy_page = self.eg.get_from_eg(self.eg.link, params=params)
        craft_lines = re.search(r'Auswahl des Handwerks.*?</tbody>',
                                academy_page.text, re.DOTALL)
        categories = {}
        for category in re.findall(r'<a href=".*?selection=(\d+).*?>([^<]*)</a>', craft_lines.group(0), re.DOTALL):
            categories[category[1]] = category[0]

        # this list is missing the default category -> we need to get another page and do everything again
        params = {"page":"academy_craft", "selection": list(categories.values())[0]}
        academy_page = self.eg.get_from_eg(self.eg.link, params=params)
        craft_lines = re.search(r'Auswahl des Handwerks.*?</tbody>',
                                academy_page.text, re.DOTALL)
        for category in re.findall(r'<a href=".*?selection=(\d+).*?>([^<]*)</a>', craft_lines.group(0), re.DOTALL):
            categories[category[1]] = category[0]
        return categories

    def get_recipes(self, cat):
        """
        Retrieve a list of all recipes of a specified category.

        Currently supported categories:
            - "Schmieden (Schwere Rüstungen): schwere-rüstung"
        """
        cat_map = {
            "Steinverarbeitung": "52",
            "Erzverarbeitung": "53",
            "Stoff-und-Lederverarbeitung": "54",
            "Konstruktion": "55",
            "Schwerter": "56",
            "Dolche": "57",
            "Äxte": "58",
            "Keulen": "59",
            "Stangenwaffen": "60",
            "Leichte-Rüstungen": "61",
            "Schwere-Rüstungen": "62",
            "Magiestäbe": "63",
            "Bögen": "64",
            "Armbrüste": "65",
            "Schneidern-Leichte-Rüstungen": "66",
            "Alchemie": "67",
            "Holzverarbeitung": "51"
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
            item_data = re.match(r'.*?<b>(\d+ )?([^<]*)</b>.*?Zutaten.*?<br>(.*?</td>)', recipe, re.DOTALL)
            # print("Name: {}".format(item_data.group(1)))
            ingredients = []
            for ingredient in re.findall(r'>(\d+)\s+(.*?)</font>', item_data.group(3), re.DOTALL):
                ingredients.append({"count": ingredient[0], "name": ingredient[1]})
            time_string = re.search(r"Dauer: (.*?)</font>", recipe)
            time_seconds = translate_time(time_string.group(1))
            recipes.update({item_data.group(2): {"ingredients": ingredients, "time": time_seconds}})
        return recipes
