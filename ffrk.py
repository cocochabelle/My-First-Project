from prettytable import PrettyTable
import json
import requests
import sys

charAlias = {
        'ok': 'onion knight',
        'tgc': 'orlandeau',
        'butz': 'bartz',
        'butts': 'bartz',
        'cid4': 'cid (iv)',
        'cid7': 'cid (vii)',
        'cid14': 'cid (xiv)',
        'gogo5': 'gogo (v)',
        'gogo6': 'gogo (vi)',
        'greg': 'gilgamesh',
        'w o l': 'warrior of light',
        'cod': 'cloud of darkness',
        'pecil': 'cecil (paladin)'
}

tier = {
    'default': 1,
    'def': 1,
    'sb': 4,
    'unique': 4,
    'ssb': 5,
    'super': 5,
    'bsb': 6,
    'burst': 6,
    'osb': 7,
    'usb': 8,
    'ultra': 8,
    'csb': 9,
    'chain': 9,
    'gsb': 10,
    'glint': 10,
    'asb': 11,
    'aosb': 11,
    'arcane': 11
}

tierName = {
    1: 'default',
    4: 'unique',
    5: 'ssb',
    6: 'bsb',
    7: 'osb',
    8: 'usb',
    9: 'csb',
    10: 'glint',
    11: 'aosb'
}

elements = {
    2: '-',
    3: 'Dark',
    4: 'Earth',
    5: 'Fire',
    6: 'Holy',
    7: 'Ice',
    8: 'Lightning',
    9: 'NE',
    10: 'Poison',
    12: 'Water',
    13: 'Wind'
}

revElements = {elemName.lower(): elemNum for elemNum, elemName in elements.items()}

schools = {
    2: 'Bard',
    3: 'Black Magic',
    4: 'Celerity',
    5: 'Combat',
    6: 'Dancer',
    7: 'Darkness',
    8: 'Dragoon',
    9: 'Heavy',
    10: 'Knight',
    11: 'Machinist',
    12: 'Monk',
    13: 'Ninja',
    14: 'Samurai',
    15: 'Sharpshooter',
    18: 'Spellblade',
    19: 'Summoning',
    20: 'Support',
    21: 'Thief',
    22: 'White Magic',
    23: 'Witch'
}

targetTypes = {
    2: 'all allies',
    3: 'all enemies',
    8: 'random enemy',
    10: 'self',
    12: 'single ally',
    13: 'single enemy'
}

statuses = {
    'en': 'attach',
    'attach': 'attach',
    'imp': 'imperil',
    'imperil': 'imperil'
}

statusBlacklist = [
    5, 212, 60, 86, 147, 8, 9, 64, 577, 190, 211, 10, 50, 51, 52, 53, 54, 151,
    542, 546, 582, 547, 25, 204, 615, 6, 26
]

otherEffectsBlacklist = [1]

# ********** FUNCTIONS ************************


def decodeElements(elementIdList):
    """
    input:  a list of integers representing element IDs
    output: a list of strings representing:
          - the element name if found in the decoding dictionary or
          - the element ID if no corresponding name was found"""

    elementsText = []
    for element in elementIdList:
        elementsText.append(elements.get(element, str(element)))

    return elementsText


def decodeSchool(schoolId):
    """
    input:  an integer representing the school ID
    output: a string representing:
          - the school name if found in the decoding dictionary or
          - the school ID if no corresponding name was found"""

    return schools.get(schoolId, str(schoolId))


def decodeTarget(targetId):
    """
    input:  an integer representing the target type
    output: a string representing:
          - the target type if found or
          - the target type ID if no corresponding name was found"""

    return targetTypes.get(targetId, str(targetId))


def decodeSbType(sbTypeStr):
    """
    input:  a strings
    output: a tuple of strings representing the alpha characters until the
            first digit, then the rest
            eg: input -> 'usb0' output -> ('usb', '0')"""

    sbType = ''
    sbNum = ''

    for char in sbTypeStr:
        if char.isalpha():
            sbType = sbType + char
        else:
            sbNum = sbTypeStr[sbTypeStr.index(char):]
            break

    return (sbType, sbNum)


def getSbIdNum(sbName):
    """
    input:  a string
    output: a list of integers representing the id of all soulbreaks found
          if no match is found, returns None"""

    url = 'http://ffrkapi.azurewebsites.net/api/v1.0/SoulBreaks/Name/%s' % (
            sbName)

    response = requests.get(url)
    data = json.loads(response.text)

    if data:
        sbIdList = [sb['id'] for sb in data]

    else:
        return None

    return sbIdList


def getSbIdList(args):
    """
    input:  a list of strings (size 1 or 2)
          - the first arg represents a char name or sb name
          - if 2 args, 1st is tested as char name, second as sb type
            Typical: ['charname', 'sbtype#']
    output: - a list of integers representing soulbreak IDs matching criteria,
            sorted
          - if 1 arg and no character was found, arg1 passed to
              sb search by name to return list of matching IDs
          - if more than one character was found, returns None
          - if no character was found and there were 2 args, returns None """

    charName = args[0]
    charName = charAlias.get(charName, charName)

    try:
        sbType = args[1]
    except IndexError:
        sbType = ''

    url = 'http://ffrkapi.azurewebsites.net/api/v1.0/Characters/Name/%s' % (
            charName)

    response = requests.get(url)
    data = json.loads(response.text)

    if len(data) > 1:
        print('More than 1 character found, please try again.')
        sys.exit()
    elif len(data) == 0 and len(sbType) > 0:
        print('Character name not found.')
        sys.exit()
    elif len(data) == 0 and len(sbType) == 0:
        if getSbIdNum(charName):
            return getSbIdNum(charName)
        else:
            print('No character or sb found.')
            sys.exit()
    else:
        charData = data[0]

    chosenTier = 0
    if len(sbType) > 0:
        sbType, sbNum = decodeSbType(sbType)
    try:
        chosenTier = tier[sbType]
    except KeyError:
        pass

    sbIdList = []

    for relic in charData['relics']:
        if relic['soulBreakId'] != 0:
            if (chosenTier == 0 or
                    chosenTier == relic['soulBreak']['soulBreakTier']):
                sbIdList.append(relic['soulBreakId'])
    sbIdList.sort()

    try:
        sbId = sbIdList[int(sbNum) - 1]
    except ValueError:
        pass
    except NameError:
        pass
    except IndexError:
        pass
    else:
        sbIdList = [sbId]

    return sbIdList


def getSbIdListByElem(tier, element):
    """
    input:  2 strings: a valid sb tier number, a valid element
    output: a list of integers, matching the search criteria"""

    url = 'http://ffrkapi.azurewebsites.net/api/v1.0/SoulBreaks/Tier/%s' % (
            tier)

    response = requests.get(url)
    data = json.loads(response.text)

    elementNum = revElements[element]
    if tier == '9':
        searchStr = 'Activates ' + elements[elementNum] + ' Chain'
        sbIdList = [relic['id'] for relic in data
                                if searchStr in relic['effects']]
    else:
        sbIdList = [relic['id'] for relic in data
                                if elementNum in relic['elements']]
    return sbIdList


def getSbIdListByStat(status, element):
    """
    input:  2 strings: a valid status, a potential element
    output: a list of integers, matching the search criteria"""

    if element in revElements:
        search_str = status + ' ' + element
        url = 'http://ffrkapi.azurewebsites.net/api/v1.0/SoulBreaks/Effect/%s' % (
                search_str)

        response = requests.get(url)
        data = json.loads(response.text)

        if data:
            sbIdList = [sb['id'] for sb in data]
        else:
            print('No soulbreak found.')
            return None

    else:
        print('Unrecognised element.')
        return None

    return sbIdList


def setupTable(fields):
    """
    input: a list of tuples containing 1 or 2 strings: the column name and,
        optionally, the alignment
    output: a PrettyTable object"""

    fieldNames = []
    alignments = []

    for field in fields:
        fieldNames.append(field[0])
        try:
            alignments.append(field[1])
        except IndexError:
            alignments.append('')

    table = PrettyTable(fieldNames)

    for index, alignment in enumerate(alignments):
        if alignment:
            table.align[fieldNames[index]] = alignment
    return table


def getSbData(sbId):
    """
    input:  an integer representing the sb ID number
    output: a dictionary containing the sb data """

    url = 'http://ffrkapi.azurewebsites.net/api/v1.0/SoulBreaks/%s' % (sbId)
    response = requests.get(url)
    data = json.loads(response.text)
    sbData = data[0]

    return sbData


def hasCommands(sbData):
    """
    input: individual sb data from json response
    output: boolean """

    if sbData['commands']:
        return True
    else:
        return False


def hasStatus(sbData):
    """
    input: individual sb data from json response
    output: boolean """

    if sbData['statuses']:
        return True
    else:
        return False


def hasOtherEffects(sbData):
    """
    input: individual sb data from json response
    output: boolean """

    if sbData['otherEffects']:
        return True
    else:
        return False


def printSbResult(sbIdList, details=True):
    """
    input: a non-empty list of integers representing the sb ID numbers
    output: prints result to screen, returns None """

    mainTable = setupTable([('Char', 'l'),
                            ('SB Name', 'l'),
                            ('Type',),
                            ('Target', 'l'),
                            ('Mult', ),
                            ('Elements', ),
                            ('CTime', ),
                            ('Effects', 'l')])

    if details:
        commandsTable = setupTable([('SB Name', ),
                                    ('Command Name', 'l'),
                                    ('School', ),
                                    ('Target', 'l'),
                                    ('Mult', ),
                                    ('Elements', ),
                                    ('CTime', ),
                                    ('Effects', 'l'),
                                    ('Gauge', )])

        statusTable = setupTable([('ID', 'l'),
                                  ('Status Name', 'l'),
                                  ('Effects', 'l'),
                                  ('Dur', )])

        otherTable = setupTable([('ID', 'l'),
                                 ('Name', 'l'),
                                 ('Mult', ),
                                 ('Effects', 'l')])

    printCommands = False
    printStatuses = False
    printOtherEffects = False
    for sbId in sbIdList:
        sbData = getSbData(sbId)

        mainTable.add_row([sbData['characterName'],
                           sbData['soulBreakName'],
                           tierName[sbData['soulBreakTier']],
                           decodeTarget(sbData['targetType']),
                           sbData['multiplier'],
                           ', '.join(decodeElements(sbData['elements'])),
                           sbData['castTime'],
                           sbData['effects']])
        if details:
            if hasCommands(sbData):
                printCommands = True
                for c in sbData['commands']:
                    commandsTable.add_row([c['sourceSoulBreakName'],
                                           c['commandName'],
                                           decodeSchool(c['school']),
                                           decodeTarget(c['targetType']),
                                           c['multiplier'],
                                           ', '.join(decodeElements(c['elements'])),
                                           c['castTime'],
                                           c['effects'],
                                           c['soulBreakPointsGained']	])

            if hasStatus(sbData):
                for s in sbData['statuses']:
                    if s['id'] not in statusBlacklist:
                        printStatuses = True
                        statusTable.add_row([s['id'],
                                             s['commonName'],
                                             s['effects'],
                                             s['defaultDuration']])

            if hasOtherEffects(sbData):
                for o in sbData['otherEffects']:
                    if o['id'] not in otherEffectsBlacklist:
                        printOtherEffects = True
                        otherTable.add_row([o['id'],
                                            o['name'],
                                            o['multiplier'],
                                            o['effects']])

    print(mainTable)
    print()
    if details:
        if printCommands:
            print(commandsTable)
            print()
        if printStatuses:
            print(statusTable)
            print()
        if printOtherEffects:
            print(otherTable)
            print()

# ************ MAIN *********************


def usage(category='gen'):
    print()
    if category == 'gen':
        print('Usage: <search type> <argument1> [<argument2> ...]')
    elif category == 'sb':
        print("""Soulbreak search:

          ffrk.py sb <character name>
          ffrk.py sb <character name> <sb type>
          ffrk.py sb <sb name>""")
    elif category == 'elem':
        print("""Soulbreak search by type and element:

          ffrk.py <type> <element>
          types: bsb, usb, osb, aosb, gsb, csb
          elements: ice, wind, fire, water, lightning, earth, holy, dark, ne""")

    print()


def main(args):

    if args:
        args = [arg.lower() for arg in args]
 
# *************** SB SEARCH *******************
        if args[0] in ['sb', 'soulbreak']:
            args = args[1:]
            if args:  # has at least 1 arg after sb
                sbType, sbNum = decodeSbType(args[-1])
                try:
                    tier[sbType]
                except KeyError:  # last arg is not sb type
                    args = [' '.join(args)]
                    if getSbIdList(args):
                        return printSbResult((getSbIdList(args)))
                    else:  # char was found but has no relic
                        print('Character has no soulbreaks from relics.')
                        sys.exit()
                else:  # last arg is sb type
                    if args:
                        args = [' '.join(args[:-1]), sbType + sbNum]
                        if args[1] == 'usb0' and 'edge' in args[0]:
                            return printSbResult((getSbIdList(['edge',
                                                               'ssb2'])))
                        else:
                            return printSbResult((getSbIdList(args)))
                    else:
                        print('Missing argument: character name.')
                        return usage(category='sb')
            else:
                print('Missing arguments.')
                return usage(category='sb')

# *************** SB SEARCH by element *******************
        elif args[0] in tier:
            sbTypeInt = tier[args[0]]
            if sbTypeInt in [6, 7, 8, 9, 10, 11]:
                try:
                    revElements[args[1]]
                except KeyError:
                    print('Second argument does not match any element.')
                    return usage(category='elem')
                else:
                    return printSbResult(
                            (getSbIdListByElem(str(sbTypeInt), args[1])),
                            details=False)
            else:
                print('This soulbreak type is not accepted for the element'
                      'search.')
                return usage(category='elem')

# *************** SB SEARCH by status *******************
        elif args[0] in statuses:
            if getSbIdListByStat(args[0], args[1]) is not None:
                return printSbResult(
                    (getSbIdListByStat(args[0], args[1])), details=False)

        elif args[0] in ['ab', 'a', 'ability']:
            print('Not available yet.')
            sys.exit()
       
        elif args[0] in ['lm']:
            print('Not available yet.')
            sys.exit()
        else:
            print('Argument(s) not recognised.')
            return usage()

    else:
        return usage()


if __name__ == "__main__":
    main(sys.argv[1:])
