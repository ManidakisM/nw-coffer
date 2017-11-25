import csv
import os
import ConfigParser
import json
from collections import defaultdict
import operator

class LogEntry:
    def __init__(self, characterName, accountName, time, item, itemCount, resource, resourceQuantity, donorGuild, recipientGuild):
        # TODO: There is a trick I've forgotten that lets you assign object attributes based on the name
        # of the arguments coming in... would be better than this. Then if the format of the CSV changes
        # we only need to change the constructor signature, and not the constructor itself.
        self.characterName = characterName
        self.accountName = accountName
        self.time = time
        self.itemCount = itemCount
        self.resource = resource
        self.resourceQuantity = resourceQuantity
        self.donorGuild = donorGuild
        self.recipientGuild = recipientGuild

"""Reads a log file, returning a list of lists with the log entries"""
def readFile(filename):
    lines = []

    with open(filename, 'rb') as log:
        reader = csv.reader(log, delimiter=',', quotechar='"')
        for line in reader:
            lines.append(line)

    return lines

# Credit to https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
"""Returns the names of all of the files in a directory"""
def globDirectory(path):
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

"""Combine two log files, returning the unique entries in each"""
def combineLogs(log1, log2):
    log1.extend(log2)
    # Credit to https://stackoverflow.com/questions/3724551/python-uniqueness-for-list-of-lists
    combined = [list(i) for i in set(tuple(i) for i in log1)]
    return combined

"""
Takes a list of lists, and returns a list of objects, where each object is a representation of a row in
 the log file
"""
def objectify(log):
    l = []
    for entry in log:
        l.append(LogEntry(*tuple(entry)))

    return l

"""Filter entries to include only donations of the types specified in resourceList"""
def filterEntries(log, resourceList):
    return [e for e in log if e.resource in resourceList]

def applyMultipliers(log, multipliers):
    for entry in log:
        entry.resourceQuantity *= multipliers[entry.resource]

    return log

def sumByAccount(log):
    total = defaultdict(lambda: 0)

    for entry in log:
        total[entry.accountName] += int(entry.resourceQuantity)

    return total

def printLeaderboard(totals):
    sortedTotals = sorted(totals.items(), key=operator.itemgetter(1))
    sortedTotals.reverse()
    
    for account, total in sortedTotals:
        print(account + ": " + str(total))

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('./config')
    path = config.get('OPTIONS', 'LogLocation')

    logfiles = globDirectory(path)
    log = []
    
    for f in logfiles:
        log = combineLogs(log, readFile(path + os.sep + f))

    resourceTypes = json.loads(config.get('OPTIONS', 'ResourceTypes'))
    resourceMultipliers = json.loads(config.get('OPTIONS', 'ResourceMultipliers'))

    log = objectify(log)
    log = filterEntries(log, resourceTypes)
    log = applyMultipliers(log, dict(zip(resourceTypes, resourceMultipliers)))
    log = sumByAccount(log)
    printLeaderboard(log)
