import os
import requests
from util import *

def get_arguments():
    subarguments = {
        "--category": { "metavar": "<item_category>", "help": 'Kategorie der Gegenstände, die überprüft werden sollen',
                       "dest": "item_category", "type": str, "choices": ["schwere-rüstung","handwerksmaterial", "bauteile", "rohstoffe"],
                       "default": "handwerksmaterial" },
        "--count-broken": { "action": "store_true", "help": "Auch nicht pristine Gegenstände einbeziehen", "dest": "use_broken" },
        "--wanted-minimum": { "metavar": "<amount>", "help": "Mindestanzahl Gegenstände, die vorhanden sein sollen", "dest": "wanted_minimum",
                             "type": int },
        "--list": { "action": "store_true", "help": "Alle Gegenstände listen", "dest": "list_items" },
    }
    return "GuildStorage", subarguments

def get_function():
    return GuildStorage.do_stuff

def get_full_item_list(cat):
    item_list = {
        "bauteile": [ "Kalk-Mauerstück", "Kalk-Bodenplatte", "Buchen-Dachkonstrukt", "Buchen-Stützbalken", "Sand-Mauerstück", "Sand-Bodenplatte",
                     "Birken-Dachkonstrukt", "Birken-Stützbalken", "Schiefer-Mauerstück", "Schiefer-Bodenplatte", "Eichen-Dachkonstrukt",
                     "Eichen-Stützbalken", "Granit-Mauerstück", "Granit-Bodenplatte", "Eschen-Dachkonstrukt", "Eschen-Stützbalken",
                     "Marmor-Mauerstück", "Marmor-Bodenplatte", "Eiben-Dachkonstrukt", "Eiben-Stützbalken"
                    ],
        "rohstoffe":[ "Kupfererz", "Kupferbarren", "Kalkstein", "Kalkziegel", "Buchenholz", "Buchenbretter", "Leinen", "Leinentuch",
                     "Weichpelze", "Weichleder", "Magiestaub", "Eisenerz", "Eisenbarren", "Sandstein", "Sandziegel", "Birkenholz",
                     "Birkenbretter", "Wolle", "Wolltuch", "Pelze", "Leder", "Todesstaub", "Sorandilerz", "Sorandilbarren", "Schiefer",
                     "Schieferziegel", "Eichenholz", "Eichenbretter", "Baumwolle", "Baumwolltuch", "Hartpelz", "Hartleder", "Schattenstaub",
                     "Adamanterz", "Adamantbarren", "Granit", "Granitziegel", "Eschenholz", "Eschenbretter", "Seide", "Seidentuch",
                     "Riesenhaut", "Riesenleder", "Mondstaub", "Mithrilerz", "Mithrilbarren", "Marmor", "Marmorziegel", "Eibenholz", "Eibenbretter",
                     "Ätherfäden", "Äthertuch", "Drachenhaut", "Drachenleder", "Sternenstaub"
                    ],
        "schwere-rüstung": [ "Kupfer-Kettenhaube", "Kupfer-Kettenhemd", "Kupfer-Kettenhandschuhe", "Kupfer-Kettenbeinlinge", "Kupfer-Kettenstiefel",
                             "Kupfer-Plattenhelm", "Kupfer-Plattenpanzer", "Kupfer-Plattenhandschuhe", "Kupfer-Plattenbeinlinge", "Kupfer-Plattenstiefel",
                             "Eisen-Kettenhaube", "Eisen-Kettenhemd", "Eisen-Kettenhandschuhe", "Eisen-Kettenbeinlinge", "Eisen-Kettenstiefel",
                             "Eisen-Plattenhelm", "Eisen-Plattenpanzer", "Eisen-Plattenhandschuhe", "Eisen-Plattenbeinlinge", "Eisen-Plattenstiefel",
                             "Sorandil-Kettenhaube", "Sorandil-Kettenhemd", "Sorandil-Kettenhandschuhe", "Sorandil-Kettenbeinlinge", "Sorandil-Kettenstiefel",
                             "Sorandil-Plattenhelm", "Sorandil-Plattenpanzer", "Sorandil-Plattenhandschuhe", "Sorandil-Plattenbeinlinge", "Sorandil-Plattenstiefel",
                             "Adamant-Kettenhaube", "Adamant-Kettenhemd", "Adamant-Kettenhandschuhe", "Adamant-Kettenbeinlinge", "Adamant-Kettenstiefel",
                             "Adamant-Plattenhelm", "Adamant-Plattenpanzer", "Adamant-Plattenhandschuhe",  "Adamant-Plattenbeinlinge", "Adamant-Plattenstiefel",
                             "Mithril-Kettenhaube", "Mithril-Kettenhemd", "Mithril-Kettenhandschuhe", "Mithril-Kettenbeinlinge", "Mithril-Kettenstiefel",
                             "Mithril-Plattenhelm", "Mithril-Plattenpanzer", "Mithril-Plattenhandschuhe", "Mithril-Plattenbeinlinge", "Mithril-Plattenstiefel"
                            ],
        "handwerksmaterial": [ "Schmiedeöl", "Bogensalbe", "Harz", "Zwirn", "Steinkohle", "Nähgarn", "Lederfett", "Magiesplitter", "Federn", "Salz", "Mörtel",
                              "Schleifstein", "Elbenhaar", "Wattierung", "Granitharz", "Glaszwirn", "Drachenzunder", "Schutzpolster", "Ledernieten", "Phasenkraut",
                              "Pfeilharz", "Kristallat", "Edelmörtel", "Griffband", "Nieten", "Vulkandraht", "Beschläge", "Erdenblut", "Drachinschneiden"
                             ]
    }
    return item_list[cat]

class GuildStorage():
    def __init__(self, eg):
        self.eg = eg
        self.name, self.id = self.__get_guild_name()

    def __get_guild_name(self):
        hero_page = self.eg.get_from_eg(self.eg.link, params={"page": "info_hero"})
        if regex_result := re.search(r'page=info_guild&guild_id=(\d+)">([^<]*)<', hero_page.text):
            pass
        else:
            print("Keine Gilde gefunden, beende")
            print(hero_page.text)
            os.sys.exit(1)
            return False
        return regex_result.groups(2), regex_result.group(1)

    def list_items(self, cat, count_broken):
        cat_map = {
            "handwerksmaterial": 32,
            "schwere-rüstung": 23,
            "rohstoffe": 31,
            "bauteile": 33
        }
        next_page = 1
        item_list = {}
        abort = 0
        while next_page:
            items_page = self.eg.get_from_eg(self.eg.link, params={"page":"stock_out", "selection":cat_map[cat], "pos":next_page})
            if res := re.search(r'<(font class="[^"]*"|a href=[^>]*)>&lt;&lt;</(font|a)>\s*\d+\s*bis\s*(\d+)\s*<(font class="[^"]*"|a href=[^>]*)>&gt;&gt;</(a|font)>\s*\(Gesamt: (\d+)\)</th>', items_page.text):
                # print("{} vs {}".format(res.group(3), res.group(6)))
                if res.group(3) == res.group(6):
                    next_page = False
                else:
                    next_page = re.search(r'pos=(\d+)"', res.group(4)).group(1)
                    # print(re.search(r'<input type="hidden" name="pos" value="(\d+)">', items_page.text).group(1))
            else:
                # print("Fehler")
                # print("URL: {}".format(self.eg.link))
                # print("Parameter:")
                # print("  pos: {}".format(next_page))
                # print("")
                # print(items_page.text)
                os.sys.exit(0)

            for i in re.finditer("<b>(<font[^>]*>)?([^ ]*) ([^<]*)(</font>)?</b>\s*(\((\d+)\))?",items_page.text):
                # print({}: {}".format(i.group(2), i.group(1)))
                # print("Groups: {}".format(len(i.groups())))
                # print("Count Broken? {}".format(count_broken))
                # print(i.groups())
                # print(i.groups(6))
                try:
                    # print("{}: {} ({})".format(i.group(3), i.group(2), i.group(6)))
                    if count_broken and int(i.group(6)) != 100:
                        # print("Counting, broken")
                        if i.group(2) in item_list.keys():
                            item_list[i.group(3)] += int(i.group(2))
                        else:
                            item_list[i.group(3)] = int(i.group(2))
                    elif int(i.group(6)) == 100:
                        # print("Counting, not broken")
                        item_list[i.group(3)] = int(i.group(2))
                    # else:
                        # print("Not Counting, broken")
                except TypeError:
                    item_list[i.group(3)] = i.group(2)
            if abort == 5:
                print("Aborted")
                break
            else:
                abort += 1
        # print(items_page.text)
        # print("Nächste Seite: {}".format(next_page))
        return item_list
