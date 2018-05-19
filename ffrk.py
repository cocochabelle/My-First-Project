from prettytable import PrettyTable
import json
import requests
import sys
import argparse
from timeit import default_timer as timer

API = 'http://ffrkapi.azurewebsites.net/api/v1.0/'
TABLE_WIDTH = 200


def time_this(func):

    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        duration = end - start
        print('Execution time: ', duration)
        return result

    return wrapper


class Timer:
    """ A timer context manager for performance testing"""

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.start = timer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = timer()
        print("Execution time for {} =".format(self.name),
              self.end - self.start)


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
        'pecil': 'cecil (paladin)',
}

tier = {
    'default': 1,
    'def': 1,
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
    'arcane': 11,
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
    11: 'aosb',
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
    13: 'Wind',
}

revElements = {elemName.lower():
               elemNum for elemNum, elemName in elements.items()}

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
    23: 'Witch',
}

targetTypes = {
    2: 'all allies',
    3: 'all enemies',
    8: 'random enemy',
    10: 'self',
    12: 'single ally',
    13: 'single enemy',
}

statuses = {
    'en': 'attach',
    'attach': 'attach',
    'imp': 'imperil',
    'imperil': 'imperil',
}

statusBlacklist = [
    5, 212, 60, 86, 147, 8, 9, 64, 577, 190, 211, 10, 50, 51, 52, 53, 54, 151,
    542, 546, 582, 547, 25, 204, 615, 6, 26, 217,
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

    url = API + 'SoulBreaks/Name/' + sbName

    response = requests.get(url)
    data = json.loads(response.text)

    if data:
        sbIdList = [sb['id'] for sb in data]
        return sbIdList
    else:
        return None


def getSbIdList(args):
    """
    input:  a list of strings
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

    url = API + 'Characters/Name/' + charName

    response = requests.get(url)
    data = json.loads(response.text)

    if len(data) > 1:
        print('More than 1 character found, please try again.')
        return None
    elif len(data) == 0 and len(sbType) > 0:
        print('Character name not found.')
        return None
    elif len(data) == 0 and len(sbType) == 0:
        if getSbIdNum(charName):    # no char found but sb by name found
            return getSbIdNum(charName)
        else:
            print('No character or soulbreak found.')
            return None
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
            if (chosenTier == 0
            or chosenTier == relic['soulBreak']['soulBreakTier']):
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

    if sbIdList:
        return sbIdList
    else:
        print(charData['characterName'] + " appears to not have any soulbreaks.")
        return None


def getSbIdListByElem(tier, element, details=False, width=TABLE_WIDTH):
    """
    input:  a valid sb tier number in string form, a valid element number int
    output: a list of integers, matching the search criteria"""

    url = API + 'SoulBreaks/Tier/' + tier

    response = requests.get(url)
    data = json.loads(response.text)

    if tier == '9':
        searchStr = 'Activates ' + elements[element] + ' Chain'
        sbIdList = [relic['id'] for relic in data
                                if searchStr in relic['effects']]
    else:
        sbIdList = [relic['id'] for relic in data
                                if element in relic['elements']]
    return sbIdList


def getSbIdListByStat(status, element, details=False, width=TABLE_WIDTH):
    """
    input:  2 strings: a valid status keyword, a valid element
    output: a list of integers, matching the search criteria"""

    if element in revElements:
        search_str = status + ' ' + element
        url = API + 'SoulBreaks/Effect/' + search_str

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

    url = API + 'SoulBreaks/' + str(sbId)
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


def printSbResult(sbIdList, details=True, width=200):
    """
    input: a non-empty list of integers representing the sb ID numbers
    output: prints result to screen, returns None """

    assert sbIdList, "sbIdList is an empty list"

    mainTable = setupTable([
                            ('Char', 'l'),
                            ('SB Name', 'l'),
                            ('Type',),
                            ('Target', 'l'),
                            ('Mult', ),
                            ('Elements', ),
                            ('CTime', ),
                            ('Effects', 'l'),
                            ])

    if details:
        commandsTable = setupTable([
                                    ('SB Name', ),
                                    ('Command Name', 'l'),
                                    ('School', ),
                                    ('Target', 'l'),
                                    ('Mult', ),
                                    ('Elements', ),
                                    ('CTime', ),
                                    ('Effects', 'l'),
                                    ('Gauge', ),
                                    ])

        statusTable = setupTable([
                                    ('ID', 'l'),
                                    ('Status Name', 'l'),
                                    ('Effects', 'l'),
                                    ('Dur', ),
                                    ])

        otherTable = setupTable([
                                ('ID', 'l'),
                                ('Name', 'l'),
                                ('Mult', ),
                                ('Effects', 'l'),
                                ])

    printCommands = False
    printStatuses = False
    printOtherEffects = False
    for sbId in sbIdList:
        sbData = getSbData(sbId)

        mainTable.add_row([
                sbData['characterName'],
                sbData['soulBreakName'],
                tierName[sbData['soulBreakTier']],
                decodeTarget(sbData['targetType']),
                sbData['multiplier'],
                ', '.join(decodeElements(sbData['elements'])),
                sbData['castTime'],
                sbData['effects'],
                ])
        if details:
            if hasCommands(sbData):
                printCommands = True
                for c in sbData['commands']:
                    commandsTable.add_row([
                            c['sourceSoulBreakName'],
                            c['commandName'],
                            decodeSchool(c['school']),
                            decodeTarget(c['targetType']),
                            c['multiplier'],
                            ', '.join(decodeElements(c['elements'])),
                            c['castTime'],
                            c['effects'],
                            c['soulBreakPointsGained'],
                            ])

            if hasStatus(sbData):
                for s in sbData['statuses']:
                    if s['id'] not in statusBlacklist:
                        printStatuses = True
                        statusTable.add_row([
                                s['id'],
                                s['commonName'],
                                s['effects'],
                                s['defaultDuration'],
                                ])

            if hasOtherEffects(sbData):
                for o in sbData['otherEffects']:
                    if o['id'] not in otherEffectsBlacklist:
                        printOtherEffects = True
                        otherTable.add_row([
                                o['id'],
                                o['name'],
                                o['multiplier'],
                                o['effects'],
                                ])

    print(mainTable)
    print()
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


def usage(*args, category='gen'):
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
          types: ssb, bsb, usb, osb, aosb, gsb, csb
          elements: ice, wind, fire, water, lightning, earth, holy, dark, ne""")

    print()


def sbParser(args):
    """
    input: the list of raw command line args after the trigger arg
    output: namespace object with parser results

    The job of the parser is to extract optionals, not validate positonals.
    It does guarantee the presence of at least 1 positional. """

    sbParser = argparse.ArgumentParser()
    sbParser.add_argument('posArgs', nargs='+',
                          help="Search string")
    sbParser.add_argument("-w", "--width", type=int, default=TABLE_WIDTH,
                          help="Width of result table in characters")

    sbArgs = sbParser.parse_args(args)
    return sbArgs


def validateSb(posArgs):
    """
    input: the non-empty list of positional args returned by the sb parser
    output: a list of 1 or 2 strings:
            if a second string is present, it represents the sb tier
            the first string represents a potential char name or sb name"""

    sbType, sbNum = decodeSbType(posArgs[-1])

    try:
        tier[sbType]
    except KeyError:  # last arg is not sb type
        return [' '.join(posArgs)]
    else:             # Last arg is sb type
        if posArgs[:-1]:
            return [' '.join((posArgs[:-1])), posArgs[-1]]
        else:
            print("Character name required when sb tier specified.")
            usage(category='sb')


def sbSearch(args):
    """
    input: raw command line arguments
    output: prints results of search to screen
            or appropriate error message when search fails"""

    ParserData = sbParser(args[1:])
    search_args = validateSb(ParserData.posArgs)
    if search_args:
        sbIds = getSbIdList(search_args)
        if sbIds:
            return printSbResult(sbIds, width=ParserData.width)
        else:
            return None


def sbTierParser(args):
    """
    input: the list of raw command line args
    output: namespace object with parser results """

    sbTierParser = argparse.ArgumentParser()
    sbTierParser.add_argument('sb_tier',
                  choices=[tier for tier, value in tier.items() if value >= 5],
                  help="Soulbreak tier")
    sbTierParser.add_argument('element',
                  choices=[key for key in revElements.keys() if key != '-'],
                  help="Element")
    sbTierParser.add_argument("-d", "--details", action='store_true',
                  help="Provides details (commands, statuses, etc.)")
    sbTierParser.add_argument("-w", "--width", type=int, default=TABLE_WIDTH,
                  help="Width of result table in characters")

    sbArgs = sbTierParser.parse_args(args)

    sbArgs.sb_tier = str(tier[sbArgs.sb_tier])
    sbArgs.element = revElements[sbArgs.element]

    return sbArgs


def sbTierSearch(args):
    """
    input: raw command line arguments
    output: prints results of search to screen
            or appropriate error message when search fails"""

    parserData = sbTierParser(args)

    return printSbResult(getSbIdListByElem(
                                parserData.sb_tier,
                                parserData.element,
                                ), details=parserData.details)


def sbStatusParser(args):
    """
    input: the list of raw command line args
    output: namespace object with parser results """

    sbStatusParser = argparse.ArgumentParser()
    sbStatusParser.add_argument('status_type',
                  choices=['imperil', 'attach'],
                  help="Status type")
    sbStatusParser.add_argument('element',
                  choices=[key for key in revElements.keys() if key != '-'],
                  help="Element")
    sbStatusParser.add_argument("-d", "--details", action='store_true',
                  help="Provides details (commands, statuses, etc.)")
    sbStatusParser.add_argument("-w", "--width", type=int, default=TABLE_WIDTH,
                  help="Width of result table in characters")

    sbArgs = sbStatusParser.parse_args(args)

    return sbArgs


def sbStatusSearch(args):
    """
    input: raw command line arguments
    output: prints results of search to screen
            or appropriate error message when search fails"""

    parserData = sbStatusParser(args)

    return printSbResult(getSbIdListByStat(
                                parserData.status_type,
                                parserData.element,
                                ), details=parserData.details)


@time_this
def main(sysargs):

    if not sysargs:
        return usage()

    newargs = [arg.lower() for arg in sysargs]

    function = usage

    if newargs[0] in ['sb', 'soulbreak']:
        function = sbSearch
    elif newargs[0] in tier:
        function = sbTierSearch
    elif newargs[0] in ['imperil', 'attach']:
        function = sbStatusSearch
    else:
        print('First argument not recognized.')
        return usage()

    return function(newargs)


if __name__ == "__main__":
    main(sys.argv[1:])
