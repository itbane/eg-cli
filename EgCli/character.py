from EgCli.util import *
import os

class EvergoreCharacter():
    def __init__(self, eg):
        self.eg = eg
        self.craft_category_map = {
            "schwere-rüstung": 62
        }
        self.max_craft_time: int = 36*3600

    def get_available_crafting_time(self):
        params = {
            "page": "craftkits"
        }
        craftkits_page = self.eg.get_from_eg(self.eg.link, params=params)
        time = re.search(r"<th>Restdauer<br>(.*?)</th>", craftkits_page.text, re.DOTALL)
        time_seconds = translate_time(time.group(1))
        return self.max_craft_time - time_seconds

    def get_available_recipes(self, category: str=None) -> list[str]:
        params = {
            "page": "craft"
        }
        try:
            params["selection"] = self.craft_category_map[category]
        except KeyError:
            print("Bausatz-Kategorie '{}' wird noch nicht unterstützt.".format(category))
            os.sys.exit(1)
        craft_page = self.eg.get_from_eg(self.eg.link, params=params)
        craftkit_table = re.search(r"<thead>.*?</tbody>",
                         craft_page.text, re.DOTALL)
        kits = []
        for kit in re.findall(r"<b>(.*?)</b>", craftkit_table.group(0)):
            kits.append(kit)
        return kits
