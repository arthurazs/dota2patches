#!/usr/bin/env python3
#coding: utf-8
import requests, os.path, argparse
from collections import defaultdict
from model import Html
from data import HeropediaData

parser = argparse.ArgumentParser(description="This software formats a Dota2' changelog text into HTML.")
parser.add_argument('--file', '-f', action='store', help="changelog to be formated", required = True, dest = 'file')
parser.add_argument('--version', '-v', action='version', version='%(prog)s: 0.0v')
args = parser.parse_args()

#CONSTANT
CHANGELOG = 'changelogs/'

#Check changelog folder
if not os.path.exists(CHANGELOG):
    os.makedirs(CHANGELOG)

#Open changelog
if os.path.isfile(CHANGELOG+args.file):
    with open(CHANGELOG+args.file, 'r') as changelog:

        #Read changelog
        lines = []
        for line in changelog:
            lines.append(line.replace('* ', '').rstrip())
        changelogName = lines[0][:-1]
        simpleChangelogName = changelogName.replace('.', '')
        lines = lines[2:]
        initialLineCount = len(lines)

    data = HeropediaData()

    #Organize changelog
    item = defaultdict(list)
    hero = defaultdict(list)
    ability = defaultdict(list)
    for line in lines[:]:
        names = line.split(' ')[:3]
        found_ability = data.get_ability_hero(names)
        if found_ability:
            ability[found_ability].append(line)
            lines.remove(line)

    for line in lines[:]:
        names = line.split(' ')[:3]
        found_hero = data.get_hero_name(names)
        if found_hero:
            hero[found_hero].append(line)
            lines.remove(line)
        else:
            found_item = data.get_item_name(names)
            if found_item:
                item[found_item].append(line)
                lines.remove(line)

    for key, value in ability.items():
        if(key in hero):
            hero[key].extend(ability[key])
        else:
            hero[key] = ability[key]

    #Generate .html
    with open(simpleChangelogName + '.html', 'w') as text:
        model = Html(changelogName)
        model.addGeneral(lines)
        model.addItems(item)
        model.addHeros(hero)
        model.close()
        print(model.getContent(), file=text)

    currentLineCount = sum(len(changes) for changes in hero.values()) + sum(len(changes) for changes in item.values())
    status = initialLineCount - currentLineCount
    if (status == 0):
        print('SUCCESS!\nConversion went smoothly.')
    elif (status < 0):
        print('CRITICAL ERROR!\nContact me at @arthurazs')
    else:
        print('WARNING!')
        if (status == 1):
            print('1 line under GENERAL updates:')
            print('* ' + ' '.join(lines))
            print('\nThis line might be a hero/item update and you should manually place it at the proper location.')
        else:
            print(str(status) + ' lines under GENERAL updates:')
            for line in lines:
                print('* ' + line)
            print('\nSome of these lines might be hero/item updates and you should manually place them at the proper location.')
    #TODO Implement a secondary list to show which lines require manual input

else:
    print ('''ERROR!
'{0}' not found.
Make sure {0} is inside the 'changelogs' folder.
Also check if the filename you typed is correct.

Contact me at @arthurazs if this error persists.'''.format(args.file))
