from EgCli.util import *
import os

class EvergoreCharacter():
    def __init__(self, eg):
        self.eg = eg
        self.craft_category_map = self.__get_available_categories()
        self.max_craft_time: int = 36*3600
        self.__all_recipes = self.__get_all_available_recipes()

    def get_available_crafting_time(self):
        params = {
            "page": "craftkits"
        }
        craftkits_page = self.eg.get_from_eg(self.eg.link, params=params)
        time = re.search(r"<th>Restdauer<br>(.*?)</th>", craftkits_page.text, re.DOTALL)
        time_seconds = translate_time(time.group(1))
        return self.max_craft_time - time_seconds

    def __get_available_categories(self) -> dict:
        category_map = {}
        params = {
            "page": "craft",
            "selection": 1
        }
        craft_page = self.eg.get_from_eg(self.eg.link, params=params)
        data = re.search(r'Auswahl des Handwerks.*?</tbody>', craft_page.text, re.DOTALL).group(0)
        categories = re.findall(r'<a href=[^>]*selection=(\d+)[^>]*>([^<]*)</a>', data, re.DOTALL)
        for cats in categories:
            category_map[cats[1]] = cats[0]
        return category_map

    def __get_all_available_recipes(self):
        res = {}
        params = {
            "page": "craft",
        }
        for name in self.craft_category_map.keys():
            res.update(self.get_available_recipes(name))
        return res

    def get_available_recipes(self, category: str | list = None) -> dict:
        params = {
            "page": "craft"
        }
        kits = {}
        if category is None:
            # alle Kategorien herausfinden
            return self.__get_all_available_recipes()
        if category is list:
            for cat in category:
                kits.update(self.get_available_recipes(cat))
        try:
            params["selection"] = self.craft_category_map[category]
        except KeyError:
            print(f"Bausatz-Kategorie '{category}' wird noch nicht unterstützt.")
            os.sys.exit(1)
        craft_page = self.eg.get_from_eg(self.eg.link, params=params)
        craftkit_table = re.search(r"</thead>.*?</tbody>",
                         craft_page.text, re.DOTALL)
        kits = {}
        for kit in re.findall(r"<tr>(.*?)</tr>", craftkit_table.group(0), re.DOTALL):
            name = re.search(r"<b>(\d+ )?(.*?)</b>", kit).group(2)
            itemid = re.search(r'<input type="number" name="recipe(\d+)"', kit, re.DOTALL).group(1)
            kits[name]= {
                "id": itemid,
                "category": category
            }
        return kits

    def get_current_craftkits(self) -> dict:
        params = {
            "page": "craftkits"
        }
        craftkits_page = self.eg.get_from_eg(self.eg.link, params=params)
        craftkit_table = re.search(r"Restdauer.*?</tbody>", craftkits_page.text, re.DOTALL)
        queued = {}
        for item in re.findall(r"<b>(.*?)</b>", craftkit_table.group(0)):
            try:
                queued[item] += 1
            except KeyError:
                queued[item] = 1
        return queued

    def add_craftkit_list(self, craftkits: dict, category: str=None, target: str=None) -> bool:
        # build recipies in format eg expects
        params = {
            "page": "craft",
            "action": "kits_create"
        }
        if category is not None:
            params["selection"]: self.craft_category_map[category]

        if target is None:
            target = ""
        print(craftkits)
        for name, count in craftkits.items():
            print_verbose("Füge Bausatz '{}' {} mal hinzu (itemid: {})".format(name, count,
                                                                                self.__all_recipes[name]["id"]))
            params["recipe"+str(self.__all_recipes[name]["id"])] = str(count)
            params["target"+str(self.__all_recipes[name]["id"])] = target

        result = self.eg.get_from_eg(params=params)

        meldung = re.search(r'<div class="eg-notes">.*?</div>', result.text, re.DOTALL)
        for name, count in craftkits.items():
            if res:=re.search(r'Bausatz '+name+r' \((\d+)x\) erstellt', meldung.group(0), re.DOTALL):
                if res.group(1) == count:
                    print_verbose("Bausatz {} erfolgreich angelegt".format(name))
                else:
                    print("Bausatz {} wurde {} von {}x angelegt".format(name, res.group(1), count))
            else:
                print("Bausatz {} wurde gar nicht angelegt!".format(name))

    def add_craftkit(self, ckid: int, target: str=None, count: int=1) -> str:
        # first, get the item-ids
        print(self.__all_recipes[name]["id"])
        return "Foo"
