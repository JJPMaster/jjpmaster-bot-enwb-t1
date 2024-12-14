# ------------------------------------------------------------------------------
#  Copyright (C) 2024 Juniper J. Ponce
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------

import pywikibot
import json
from datetime import datetime, timezone

site = pywikibot.Site('en', 'wikibooks')
metawiki = pywikibot.Site('meta', 'meta')


def globalallusers(site, group):
    """

    :param site: The site to get our data from.
    :type site: pywikibot.site.APISite
    :param group: The group to get.
    :type group: str
    :return: A pywikibot generator of all global users in the given global group.
    :rtype: pywikibot.data.api.ListGenerator
    """
    agugen = pywikibot.data.api.ListGenerator('globalallusers',
                                              aguprop='groups', site=site)
    if group:
        agugen.request['agugroup'] = group
    return agugen

def sortkeys(key: str) -> str:
    """
    Sorts the user groups before saving them to the wiki.

    @param key: User right
    @type key: str
    @return: Corresponding abbreviation
    @rtype: str
    """
    sortkeyDict = {
        "sysop": "A",
        "bureaucrat": "B",
        "checkuser": "CU",
        "global-sysop": "GS",
        "suppress": "OS",
        "interface-admin": "IA",
        "accountcreator": "ACC",
        "autoreview": "AR",
        "editor": "REV",
        "global-renamer": "GRe",
        "global-rollbacker": "GRb",
        "vrt-permissions": "VRT",
        "ombuds": "Omb",
        "steward": "S"
    }
    return sortkeyDict[key]
    

combinedJsDataPage = pywikibot.Page(site, "User:JJPMaster (bot)/markAdmins-Data.js")
combinedJsonDataPage = pywikibot.Page(site, "User:JJPMaster (bot)/markAdmins-Data.json")


localGroups = ["accountcreator",
               "bureaucrat", "checkuser",
               "interface-admin", "suppress",
               "sysop"]
extraLocalGroups = ["autoreview", "editor"]
globalGroups = ["vrt-permissions", "steward", "global-rollbacker", "global-sysop", "ombuds"]
metaGroups = ["global-renamer"]

outputDict = {}

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +
      " -- Starting!", flush=True)

for group in localGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in globalGroups:
    for user in globalallusers(site, group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in extraLocalGroups:
    for user in site.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

for group in metaGroups:
    for user in metawiki.allusers(group=group):
        if user['name'] in outputDict.keys():
            outputDict[user['name']].append(group)
        else:
            outputDict[user['name']] = [group]

print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f") +
      " -- Computing output...", flush=True)

# Sort our flags
for item in outputDict:
    outputDict[item].sort(key=sortkeys)

# Construct combined JSON page
pageTop = "mw.hook('userjs.script-loaded.markadmins').fire("
outputJson = json.dumps(outputDict, sort_keys=True,
                        indent=4, separators=(',', ': '), ensure_ascii=False)
pageBottom = ");"

newText = pageTop + outputJson + pageBottom
oldJspage = combinedJsDataPage.get()
oldJsonpage = combinedJsonDataPage.get()

if newText != oldJspage or outputJson != oldJsonpage:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")
          + " -- Updated!", flush=True)
    combinedJsDataPage.put(newText, "Update markAdmins data")
    combinedJsonDataPage.put(outputJson, "Update markAdmins data")
else:
    print(datetime.now(timezone.utc).strftime("%b %d %Y %H:%M:%S.%f")
          + " -- No changes", flush=True)
