import re
import requests

from util import *

def start_horde_battle(world, min_ap, verbose):
    data = {
        'page': 'group_encounter'
    }
    response = requests.request('GET','https://evergore.de/zyrthania',headers=HDRS,params=data)

    aps = re.search(r'<td class="bar_action" style="background-position:.*?">AP: (\d+) / 750</td></tr>', response.text).group(1)
    print("Charakter hat {} APs".format(aps))
    if int(aps) < min_ap:
        print("Beende, nicht genug APs")
        return False
    if re.search(r'<div class="eg-notes">.*?Ihr tragt zur Zeit einen Kampf aus\..*?</div>', response.text):
        print("Bereits ein Kampf im Gange, beende")
        return False

    if re.search(r"insgesamt \d+ Monster", response.text):
        printVerbose("Horde wurde gefunden", verbose)
    else:
        printVerbose("Keine Horde gefunden", verbose)
        return False
    if tr_match := re.search(r"action=group_encounter_npcgroup&group_id=(\d+)'", response.text):
        printVerbose("Found NPC group encounter: NPC group ID {}".format(tr_match.group(1)), verbose)
    else:
        print("Kein Match!")
        return False
    print("Starte Kampf...")

    att_response = requests.request("GET", "https://evergore.de/{}".format(world),headers=HDRS,
                                    params={"page":"group_encounter","action":"group_encounter_npcgroup",
                                            "group_id":tr_match.group(1)})


    if re.search(r'<div class="eg-notes">.*?Der Kampf beginnt.*?</div>', att_response.text):
        print("Kampf erfolgreich gestartet!")
        return True
    else:
        return False
